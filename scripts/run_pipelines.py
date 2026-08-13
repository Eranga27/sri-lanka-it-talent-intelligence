"""
Pipeline Orchestrator — Sri Lanka IT Talent Intelligence

Usage:
    python scripts/run_pipelines.py --layer all

Environment variables (see .env.example):
    GREENHOUSE_BOARDS
    WORKABLE_BOARDS
    LEVER_BOARDS
"""
import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb

from pipelines.connectors.greenhouse import GreenhouseConnector
from pipelines.connectors.workable import WorkableConnector
from pipelines.connectors.lever import LeverConnector
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
    gh_boards = [b.strip() for b in os.getenv("GREENHOUSE_BOARDS", "canonical,gitlab").split(",") if b.strip()]
    workable_boards = [b.strip() for b in os.getenv("WORKABLE_BOARDS", "homey,international-water-management-institute,orfium,unison,inivos").split(",") if b.strip()]
    lever_boards = [b.strip() for b in os.getenv("LEVER_BOARDS", "leverdemo").split(",") if b.strip()]
    
    return {
        "greenhouse": {
            "boards": gh_boards,
            "timeout": int(os.getenv("GREENHOUSE_TIMEOUT", "30")),
            "max_retries": int(os.getenv("GREENHOUSE_MAX_RETRIES", "3")),
        },
        "workable": {
            "boards": workable_boards,
            "timeout": int(os.getenv("WORKABLE_TIMEOUT", "30")),
            "max_retries": int(os.getenv("WORKABLE_MAX_RETRIES", "3")),
        },
        "lever": {
            "boards": lever_boards,
            "timeout": int(os.getenv("LEVER_TIMEOUT", "30")),
            "max_retries": int(os.getenv("LEVER_MAX_RETRIES", "3")),
        }
    }

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_existing_silver() -> Dict[str, str]:
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
    for job in jobs:
        jid = job["job_id"]
        job["last_seen_at"] = now_iso
        job["ingested_at"] = now_iso
        job["first_seen_at"] = existing_first_seen.get(jid, now_iso)
    return jobs

def _detect_duplicates(
    jobs: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
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
# Ingestion Runner
# ---------------------------------------------------------------------------

def run_pipeline(config: Dict[str, Any]):
    """Run full Bronze → Silver → Gold pipeline for all connectors."""
    t0 = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = str(uuid.uuid4())[:8]

    connectors = [
        GreenhouseConnector(source_id="greenhouse_main", config=config.get("greenhouse")),
        WorkableConnector(source_id="workable_main", config=config.get("workable")),
        LeverConnector(source_id="lever_main", config=config.get("lever")),
    ]

    all_accepted_records = []
    reports = []
    existing_first_seen = _load_existing_silver()
    framework = DataQualityFramework(JobContract)

    for connector in connectors:
        source_name = connector.__class__.__name__.replace("Connector", "")
        logger.info("=" * 60)
        logger.info("INGESTING SOURCE: %s", source_name)
        
        # BRONZE
        raw_data = connector.fetch()
        records_fetched = len(raw_data)
        bronze_path = ""
        
        if raw_data:
            bronze_source_dir = os.path.join(BRONZE_DIR, source_name.lower())
            os.makedirs(bronze_source_dir, exist_ok=True)
            bronze_rows = []
            for record in raw_data:
                bronze_rows.append({
                    "source": source_name,
                    "source_job_id": str(record.get("id") or record.get("shortcode") or ""),
                    "board_source": record.get("_board_source", ""),
                    "raw_payload": json.dumps(record, default=str),
                    "ingested_at": now_iso,
                })
            df = pd.DataFrame(bronze_rows)
            bronze_path = os.path.join(bronze_source_dir, f"{source_name.lower()}_{timestamp}.parquet")
            pq.write_table(pa.Table.from_pandas(df), bronze_path)
            logger.info("Bronze written: %s", bronze_path)
        
        # SILVER
        if not raw_data:
            logger.info("No records to process for %s", source_name)
            continue
            
        normalized = connector.normalize(raw_data)
        normalized = _apply_timestamps(normalized, existing_first_seen, now_iso)
        normalized, dup_count = _detect_duplicates(normalized)
        
        result = framework.check_schema_validity(normalized)
        accepted = result["accepted"]
        rejected = result["rejected"]
        errors = result["errors"]
        score = framework.calculate_quality_score(len(normalized), len(accepted))
        
        all_accepted_records.extend(accepted)
        
        sl_count = sum(1 for r in accepted if r.get("country") == "Sri Lanka")
        
        report = {
            "source": source_name,
            "records_fetched": records_fetched,
            "records_normalized": len(normalized),
            "records_accepted": len(accepted),
            "records_rejected": len(rejected),
            "duplicates_removed": dup_count,
            "sri_lankan_records": sl_count,
            "data_quality_score": score,
            "bronze_path": bronze_path,
        }
        reports.append(report)
        logger.info("%s summary: %d accepted, %d rejected, %d SL records.", source_name, len(accepted), len(rejected), sl_count)

    # MERGE INTO SILVER
    logger.info("=" * 60)
    logger.info("MERGING SILVER LAYER")
    accepted_df = pd.DataFrame(all_accepted_records) if all_accepted_records else pd.DataFrame()
    
    if not accepted_df.empty:
        if os.path.exists(SILVER_JOBS_PATH):
            try:
                old_df = pd.read_parquet(SILVER_JOBS_PATH)
                new_ids = set(accepted_df["job_id"])
                expired_df = old_df[~old_df["job_id"].isin(new_ids)].copy()
                if not expired_df.empty:
                    expired_df["status"] = "expired"
                    # Only update last_seen_at if it's the current run that expired them?
                    # Or keep their old last_seen_at. We keep their old last_seen_at which means it's accurate.
                    final_df = pd.concat([accepted_df, expired_df], ignore_index=True)
                else:
                    final_df = accepted_df
            except Exception as exc:
                logger.warning("Could not merge existing Silver; overwriting. Reason: %s", exc)
                final_df = accepted_df
        else:
            final_df = accepted_df

        # Write to silver
        pq.write_table(pa.Table.from_pandas(final_df), SILVER_JOBS_PATH)
        logger.info("Silver written: %d total records → %s", len(final_df), SILVER_JOBS_PATH)
    else:
        logger.warning("No valid records to write to Silver across all sources.")

    # GOLD AGGREGATION
    logger.info("=" * 60)
    logger.info("GOLD AGGREGATION")
    if os.path.exists(SILVER_JOBS_PATH):
        try:
            conn = duckdb.connect(':memory:')
            # Generate dynamically
            gold_role_demand = conn.execute(f"""
                SELECT 
                    role_category, 
                    COUNT(*) as job_count, 
                    COUNT(DISTINCT company) as unique_companies,
                    '{now_iso}' as calculated_at
                FROM read_parquet('{SILVER_JOBS_PATH}')
                WHERE status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL
                GROUP BY role_category
            """).df()
            gold_path = os.path.join(GOLD_DIR, "gold_role_demand.parquet")
            pq.write_table(pa.Table.from_pandas(gold_role_demand), gold_path)
            logger.info("Gold Role Demand written to %s", gold_path)
        except Exception as exc:
            logger.error("Failed to generate Gold aggregations: %s", exc)

    logger.info("=" * 60)
    for r in reports:
        print(f"Source: {r['source']:<12} | Fetched: {r['records_fetched']:<4} | Accepted: {r['records_accepted']:<4} | LK: {r['sri_lankan_records']:<4} | Score: {r['data_quality_score']}%")
    
    elapsed = (time.time() - t0)
    logger.info("Pipeline complete in %.1fs", elapsed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sri Lanka IT Talent Intelligence Pipeline")
    parser.add_argument("--layer", choices=["all"], default="all", help="Which layer to run")
    args = parser.parse_args()

    print(f"\n  Sri Lanka IT Talent Intelligence — Multi-Source Pipeline Runner")
    print(f"  Run started: {datetime.now(timezone.utc).isoformat()}\n")

    config = load_config()
    run_pipeline(config)
    
    print(f"\n  Run completed: {datetime.now(timezone.utc).isoformat()}\n")
