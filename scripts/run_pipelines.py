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
from apps.api.app.models.domain import JobContract, JobSkill
from pipelines.skills import extract_skills_from_job
from pipelines.classification import classify_role_v2

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
SILVER_SKILLS_PATH = os.path.join(SILVER_DIR, "job_skills.parquet")

os.makedirs(BRONZE_DIR, exist_ok=True)
os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config() -> Dict[str, Any]:
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
        
        # SILVER NORMALIZATION
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

    # NLP & CLASSIFICATION (Phase 1D)
    logger.info("=" * 60)
    logger.info("APPLYING NLP & CLASSIFICATION (V2)")
    
    all_job_skills = []
    classified_sl_it_count = 0
    extracted_skills_count = 0
    
    for job in all_accepted_records:
        # Extract Skills
        skills = extract_skills_from_job(job)
        all_job_skills.extend(skills)
        if skills:
            extracted_skills_count += len(skills)
            
        # Re-Classify Role with V2 (including skill evidence)
        cat, method, conf = classify_role_v2(
            job.get("title"), job.get("department"), job.get("description"), skills
        )
        job["role_category"] = cat
        job["classification_method"] = method
        job["classification_confidence"] = conf
        
        if job.get("country") == "Sri Lanka" and cat is not None:
            classified_sl_it_count += 1
            
    logger.info("Classification applied. SL IT records found: %d", classified_sl_it_count)
    logger.info("Extracted %d total skills across all active jobs.", extracted_skills_count)

    # MERGING SILVER LAYER
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
                    final_df = pd.concat([accepted_df, expired_df], ignore_index=True)
                else:
                    final_df = accepted_df
            except Exception as exc:
                logger.warning("Could not merge existing Silver jobs; overwriting. Reason: %s", exc)
                final_df = accepted_df
        else:
            final_df = accepted_df

        # Write to silver jobs
        pq.write_table(pa.Table.from_pandas(final_df), SILVER_JOBS_PATH)
        logger.info("Silver jobs written: %d total records → %s", len(final_df), SILVER_JOBS_PATH)
        
        # Write silver job skills (only tracking skills for active jobs in this run for simplicity, or we could append. 
        # Overwrite with current active mapping is safer to avoid duplication over time).
        skills_df = pd.DataFrame(all_job_skills) if all_job_skills else pd.DataFrame()
        if not skills_df.empty:
            pq.write_table(pa.Table.from_pandas(skills_df), SILVER_SKILLS_PATH)
            logger.info("Silver skills written: %d total relationships → %s", len(skills_df), SILVER_SKILLS_PATH)
            
    else:
        logger.warning("No valid records to write to Silver across all sources.")

    # GOLD AGGREGATION
    logger.info("=" * 60)
    logger.info("GOLD AGGREGATION")
    if os.path.exists(SILVER_JOBS_PATH):
        try:
            conn = duckdb.connect(':memory:')
            
            # Gold Role Demand (Active jobs only)
            gold_role_demand = conn.execute(f"""
                SELECT 
                    role_category, 
                    COUNT(*) as job_count, 
                    COUNT(DISTINCT company) as unique_companies,
                    '{now_iso}' as calculated_at,
                    COUNT(DISTINCT source) as source_count,
                    '{now_iso}' as period_start,
                    '{now_iso}' as period_end,
                    'Sri Lanka' as country
                FROM read_parquet('{SILVER_JOBS_PATH}')
                WHERE status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL
                GROUP BY role_category
                ORDER BY job_count DESC
            """).df()
            
            total_active_sl_it_jobs = max(1, gold_role_demand['job_count'].sum())
            gold_role_demand['job_percentage'] = (gold_role_demand['job_count'] / total_active_sl_it_jobs) * 100
            
            gold_role_path = os.path.join(GOLD_DIR, "gold_role_demand.parquet")
            pq.write_table(pa.Table.from_pandas(gold_role_demand), gold_role_path)
            logger.info("Gold Role Demand written to %s", gold_role_path)
            
            # Gold Skill Demand (Active Sri Lankan IT jobs only)
            if os.path.exists(SILVER_SKILLS_PATH):
                gold_skill_demand = conn.execute(f"""
                    SELECT 
                        s.skill_id,
                        s.canonical_skill as skill_name,
                        s.skill_category,
                        COUNT(DISTINCT j.job_id) as job_count,
                        COUNT(DISTINCT j.company) as unique_companies,
                        COUNT(DISTINCT j.source) as source_count,
                        '{now_iso}' as calculated_at,
                        '{now_iso}' as period_start,
                        '{now_iso}' as period_end,
                        'Sri Lanka' as country
                    FROM read_parquet('{SILVER_SKILLS_PATH}') s
                    JOIN read_parquet('{SILVER_JOBS_PATH}') j ON s.job_id = j.job_id
                    WHERE j.status = 'active' AND j.country = 'Sri Lanka' AND j.role_category IS NOT NULL
                    GROUP BY s.skill_id, s.canonical_skill, s.skill_category
                    ORDER BY job_count DESC
                """).df()
                
                gold_skill_demand['job_percentage'] = (gold_skill_demand['job_count'] / total_active_sl_it_jobs) * 100
                gold_skill_path = os.path.join(GOLD_DIR, "gold_skill_demand.parquet")
                pq.write_table(pa.Table.from_pandas(gold_skill_demand), gold_skill_path)
                logger.info("Gold Skill Demand written to %s", gold_skill_path)

            # Market Coverage Metrics
            market_summary = conn.execute(f"""
                SELECT 
                    COUNT(*) as total_observed_jobs,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as total_active_jobs,
                    SUM(CASE WHEN status = 'active' AND country = 'Sri Lanka' THEN 1 ELSE 0 END) as total_sri_lankan_jobs,
                    SUM(CASE WHEN status = 'active' AND country = 'Sri Lanka' AND role_category IS NOT NULL THEN 1 ELSE 0 END) as total_sri_lankan_it_jobs,
                    COUNT(DISTINCT company) as unique_companies,
                    COUNT(DISTINCT source) as unique_sources,
                    MAX(ingested_at) as latest_ingestion,
                    MIN(first_seen_at) as oldest_observation
                FROM read_parquet('{SILVER_JOBS_PATH}')
            """).df()
            market_path = os.path.join(GOLD_DIR, "gold_market_summary.parquet")
            pq.write_table(pa.Table.from_pandas(market_summary), market_path)
            logger.info("Market Summary written to %s", market_path)
            
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
