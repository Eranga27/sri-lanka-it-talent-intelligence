"""
Pipeline Orchestrator — Sri Lanka IT Talent Intelligence

Usage:
    python scripts/run_pipelines.py --layer all
    python scripts/run_pipelines.py --layer bronze
    python scripts/run_pipelines.py --layer silver

Environment variables (see .env.example):
    GREENHOUSE_BOARDS  — comma-separated board slugs, e.g. canonical,gitlab
"""
import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Path bootstrap — allow running from project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from pipelines.connectors.greenhouse import GreenhouseConnector
from pipelines.quality.framework import DataQualityFramework
from apps.api.app.models.domain import JobContract

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("pipeline")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BRONZE_DIR = os.path.join(PROJECT_ROOT, "data", "bronze")
SILVER_DIR = os.path.join(PROJECT_ROOT, "data", "silver")
GOLD_DIR = os.path.join(PROJECT_ROOT, "data", "gold")
SILVER_JOBS_PATH = os.path.join(SILVER_DIR, "jobs.parquet")

os.makedirs(BRONZE_DIR, exist_ok=True)
os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config() -> Dict[str, Any]:
    """Load pipeline configuration from environment variables."""
    boards_str = os.getenv("GREENHOUSE_BOARDS", "canonical,gitlab")
    boards = [b.strip() for b in boards_str.split(",") if b.strip()]
    return {
        "greenhouse": {
            "boards": boards,
            "timeout": int(os.getenv("GREENHOUSE_TIMEOUT", "30")),
            "max_retries": int(os.getenv("GREENHOUSE_MAX_RETRIES", "3")),
        }
    }

# ---------------------------------------------------------------------------
# First-seen / Last-seen helpers
# ---------------------------------------------------------------------------

def _load_existing_silver() -> Dict[str, str]:
    """Load existing silver job_id → first_seen_at mapping."""
    if not os.path.exists(SILVER_JOBS_PATH):
        return {}
    try:
        df = pd.read_parquet(SILVER_JOBS_PATH, columns=["job_id", "first_seen_at"])
        return dict(zip(df["job_id"], df["first_seen_at"]))
    except Exception as exc:
        logger.warning("Could not read existing Silver data: %s", exc)
        return {}

def _apply_timestamps(
    jobs: List[Dict[str, Any]],
    existing_first_seen: Dict[str, str],
    now_iso: str,
) -> List[Dict[str, Any]]:
    """Stamp first_seen_at / last_seen_at / ingested_at on every record."""
    for job in jobs:
        jid = job["job_id"]
        job["last_seen_at"] = now_iso
        job["ingested_at"] = now_iso
        # Preserve original first_seen_at if we have seen this job before
        job["first_seen_at"] = existing_first_seen.get(jid, now_iso)
    return jobs

# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def _detect_duplicates(
    jobs: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Deduplicate on (source, source_job_id) — the strongest identity key.
    Returns (deduplicated_list, duplicate_count).
    """
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    dups = 0
    for job in jobs:
        key = (job.get("source"), job.get("source_job_id"))
        if key in seen:
            dups += 1
        else:
            seen.add(key)
            unique.append(job)
    return unique, dups

# ---------------------------------------------------------------------------
# Bronze layer
# ---------------------------------------------------------------------------

def run_bronze_ingestion(
    config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Optional[GreenhouseConnector], str]:
    """
    Fetch raw data → write to Bronze Parquet.

    Returns:
        (raw_data, connector, bronze_path)
    """
    logger.info("=" * 60)
    logger.info("BRONZE INGESTION — started")
    t0 = time.time()

    gh_config = config.get("greenhouse", {})
    connector = GreenhouseConnector(source_id="greenhouse_main", config=gh_config)

    logger.info("Source: Greenhouse | Boards: %s", gh_config.get("boards"))

    raw_data = connector.fetch()
    records_fetched = len(raw_data)
    logger.info("Records fetched: %d", records_fetched)

    if not raw_data:
        logger.warning("No records returned. Bronze phase complete with empty result.")
        return [], connector, ""

    # Build Bronze records — preserve full raw payload
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    now_iso = datetime.now(timezone.utc).isoformat()

    bronze_rows = []
    for record in raw_data:
        bronze_rows.append(
            {
                "source": "Greenhouse",
                "source_job_id": str(record.get("id", "")),
                "board_source": record.get("_board_source", ""),
                "raw_payload": json.dumps(record, default=str),
                "ingested_at": now_iso,
            }
        )

    df = pd.DataFrame(bronze_rows)
    bronze_path = os.path.join(BRONZE_DIR, f"greenhouse_{timestamp}.parquet")
    pq.write_table(pa.Table.from_pandas(df), bronze_path)

    elapsed = (time.time() - t0) * 1000
    logger.info("Records written to Bronze: %d", len(bronze_rows))
    logger.info("Output: %s", bronze_path)
    logger.info("BRONZE INGESTION — complete (%.0f ms)", elapsed)
    logger.info("=" * 60)

    return raw_data, connector, bronze_path

# ---------------------------------------------------------------------------
# Silver layer
# ---------------------------------------------------------------------------

def run_silver_transformation(
    raw_data: List[Dict[str, Any]],
    connector: GreenhouseConnector,
    bronze_path: str,
) -> Dict[str, Any]:
    """
    Normalize raw data → validate → write Silver Parquet.

    Returns quality report dict.
    """
    logger.info("=" * 60)
    logger.info("SILVER TRANSFORMATION — started")
    t0 = time.time()
    run_id = str(uuid.uuid4())[:8]
    now_iso = datetime.now(timezone.utc).isoformat()

    if not raw_data:
        logger.warning("No raw data to transform.")
        return {}

    # --- Normalize ---
    normalized = connector.normalize(raw_data)
    logger.info("Normalized: %d records", len(normalized))

    # --- Timestamps ---
    existing_first_seen = _load_existing_silver()
    normalized = _apply_timestamps(normalized, existing_first_seen, now_iso)

    # --- Duplicate detection ---
    normalized, dup_count = _detect_duplicates(normalized)
    logger.info("Duplicates removed: %d | Unique: %d", dup_count, len(normalized))

    # --- Data quality validation ---
    framework = DataQualityFramework(JobContract)
    result = framework.check_schema_validity(normalized)
    accepted = result["accepted"]
    rejected = result["rejected"]
    errors = result["errors"]
    score = framework.calculate_quality_score(len(normalized), len(accepted))

    logger.info(
        "Validation — accepted: %d | rejected: %d | score: %.1f%%",
        len(accepted),
        len(rejected),
        score,
    )
    if errors:
        logger.warning("Validation errors: %s", json.dumps(errors))

    # Sri Lanka signal
    accepted_df = pd.DataFrame(accepted) if accepted else pd.DataFrame()
    sl_count = 0
    if not accepted_df.empty and "country" in accepted_df.columns:
        sl_count = int((accepted_df["country"] == "Sri Lanka").sum())

    if not accepted:
        logger.warning("No valid records to write to Silver.")
    else:
        # Merge with existing Silver so expired jobs are preserved
        if os.path.exists(SILVER_JOBS_PATH):
            try:
                old_df = pd.read_parquet(SILVER_JOBS_PATH)
                new_ids = set(accepted_df["job_id"])
                expired_df = old_df[~old_df["job_id"].isin(new_ids)].copy()
                if not expired_df.empty:
                    expired_df["status"] = "expired"
                    expired_df["last_seen_at"] = now_iso
                    final_df = pd.concat([accepted_df, expired_df], ignore_index=True)
                    logger.info(
                        "Merged %d active + %d expired records into Silver.",
                        len(accepted_df),
                        len(expired_df),
                    )
                else:
                    final_df = accepted_df
            except Exception as exc:
                logger.warning("Could not merge existing Silver; overwriting. Reason: %s", exc)
                final_df = accepted_df
        else:
            final_df = accepted_df

        pq.write_table(pa.Table.from_pandas(final_df), SILVER_JOBS_PATH)
        logger.info("Silver written: %d total records → %s", len(final_df), SILVER_JOBS_PATH)
        logger.info("Sri Lankan IT postings identified: %d", sl_count)

    elapsed = (time.time() - t0) * 1000

    if sl_count == 0:
        logger.info(
            "No qualifying Sri Lankan IT postings found in this ingestion batch."
        )

    report = {
        "run_id": run_id,
        "source": "Greenhouse",
        "timestamp": now_iso,
        "records_fetched": len(raw_data),
        "records_normalized": len(normalized),
        "records_accepted": len(accepted),
        "records_rejected": len(rejected),
        "duplicates_removed": dup_count,
        "sri_lankan_records": sl_count,
        "validation_errors": errors,
        "processing_time_ms": round(elapsed, 1),
        "data_quality_score": score,
        "output_bronze_path": bronze_path,
        "output_silver_path": SILVER_JOBS_PATH if accepted else None,
    }

    logger.info("SILVER TRANSFORMATION — complete (%.0f ms)", elapsed)
    logger.info("=" * 60)
    return report

# ---------------------------------------------------------------------------
# Gold layer (stub — Phase 1C)
# ---------------------------------------------------------------------------

def run_gold_aggregation() -> None:
    logger.info("=" * 60)
    logger.info("GOLD AGGREGATION — Phase 1C placeholder")
    logger.info("Gold datasets will be built from Silver once classification is stable.")
    logger.info("=" * 60)

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _print_report(report: Dict[str, Any]) -> None:
    if not report:
        return
    print("\n" + "=" * 60)
    print("  PIPELINE RUN REPORT")
    print("=" * 60)
    for k, v in report.items():
        print(f"  {k:<30} {v}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sri Lanka IT Talent Intelligence Pipeline"
    )
    parser.add_argument(
        "--layer",
        choices=["all", "bronze", "silver", "gold"],
        default="all",
        help="Which layer to run (default: all)",
    )
    args = parser.parse_args()

    print("\n  Sri Lanka IT Talent Intelligence — Pipeline Runner")
    print(f"  Run started: {datetime.now(timezone.utc).isoformat()}\n")

    config = load_config()
    raw_data: List[Dict[str, Any]] = []
    connector: Optional[GreenhouseConnector] = None
    bronze_path = ""
    report: Dict[str, Any] = {}

    if args.layer in ("all", "bronze"):
        raw_data, connector, bronze_path = run_bronze_ingestion(config)

    if args.layer in ("all", "silver"):
        if connector is None:
            # Standalone silver run — cannot re-normalise without connector
            # (would need to replay from Bronze Parquet in Phase 1C)
            logger.error(
                "Silver-only run requires raw data. Use --layer all or run bronze first."
            )
        else:
            report = run_silver_transformation(raw_data, connector, bronze_path)
            _print_report(report)

    if args.layer in ("all", "gold"):
        run_gold_aggregation()

    print(f"  Run completed: {datetime.now(timezone.utc).isoformat()}\n")
