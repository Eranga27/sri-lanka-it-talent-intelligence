"""
DuckDB service — queries Silver/Gold Parquet files via DuckDB in-memory engine.

All results reflect actual ingested data. Empty datasets return genuine empty responses.
"""
import logging
import os
from typing import Any, Dict, List, Optional

import duckdb

logger = logging.getLogger(__name__)

# Resolve paths relative to the project root (two levels up from this file)
_HERE = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))

SILVER_LAKE_PATH = os.getenv(
    "SILVER_LAKE_PATH",
    os.path.join(_PROJECT_ROOT, "data", "silver"),
)
JOBS_PARQUET_PATH = os.path.join(SILVER_LAKE_PATH, "jobs.parquet")

# Normalise separators for DuckDB (use forward slashes everywhere)
JOBS_PARQUET_PATH_SQL = JOBS_PARQUET_PATH.replace("\\", "/")


def _has_silver_data() -> bool:
    return os.path.exists(JOBS_PARQUET_PATH)


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database=":memory:", read_only=False)


# ---------------------------------------------------------------------------
# Public query functions
# ---------------------------------------------------------------------------

def get_jobs(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Return paginated job records from Silver, ordered by first_seen_at."""
    if not _has_silver_data():
        logger.info("No Silver data at %s — returning empty list.", JOBS_PARQUET_PATH)
        return []

    con = _connect()
    try:
        query = f"""
            SELECT
                job_id, source, source_job_id, company, title,
                location, country, region, city,
                department, employment_type,
                role_category, classification_method, classification_confidence,
                application_url, source_url,
                status, first_seen_at, last_seen_at, ingested_at
            FROM read_parquet('{JOBS_PARQUET_PATH_SQL}')
            ORDER BY first_seen_at DESC
            LIMIT {int(limit)} OFFSET {int(offset)}
        """
        df = con.execute(query).fetchdf()
        return df.to_dict(orient="records")
    except Exception as exc:
        logger.error("get_jobs failed: %s", exc)
        return []
    finally:
        con.close()


def get_jobs_summary() -> Dict[str, Any]:
    """Return aggregate counts from Silver."""
    if not _has_silver_data():
        return {
            "total_jobs": 0,
            "active_jobs": 0,
            "sri_lankan_jobs": 0,
            "last_ingested_at": None,
            "data_available": False,
        }

    con = _connect()
    try:
        query = f"""
            SELECT
                COUNT(*)                                                    AS total_jobs,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END)         AS active_jobs,
                SUM(CASE WHEN country = 'Sri Lanka' THEN 1 ELSE 0 END)     AS sri_lankan_jobs,
                MAX(ingested_at)                                            AS last_ingested_at
            FROM read_parquet('{JOBS_PARQUET_PATH_SQL}')
        """
        row = con.execute(query).fetchone()
        return {
            "total_jobs": int(row[0] or 0),
            "active_jobs": int(row[1] or 0),
            "sri_lankan_jobs": int(row[2] or 0),
            "last_ingested_at": str(row[3]) if row[3] else None,
            "data_available": int(row[0] or 0) > 0,
        }
    except Exception as exc:
        logger.error("get_jobs_summary failed: %s", exc)
        return {
            "total_jobs": 0,
            "active_jobs": 0,
            "sri_lankan_jobs": 0,
            "last_ingested_at": None,
            "data_available": False,
            "error": str(exc),
        }
    finally:
        con.close()


def get_sources_summary() -> List[Dict[str, Any]]:
    """Return per-source record counts from Silver."""
    if not _has_silver_data():
        return []

    con = _connect()
    try:
        query = f"""
            SELECT
                source,
                COUNT(*)                                                    AS total_records,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END)         AS active_records,
                MIN(first_seen_at)                                          AS earliest_seen,
                MAX(last_seen_at)                                           AS latest_seen,
                MAX(ingested_at)                                            AS last_ingested_at
            FROM read_parquet('{JOBS_PARQUET_PATH_SQL}')
            GROUP BY source
            ORDER BY total_records DESC
        """
        df = con.execute(query).fetchdf()
        return df.to_dict(orient="records")
    except Exception as exc:
        logger.error("get_sources_summary failed: %s", exc)
        return []
    finally:
        con.close()


def get_role_distribution() -> List[Dict[str, Any]]:
    """Return active job counts grouped by role_category from Silver."""
    if not _has_silver_data():
        return []

    con = _connect()
    try:
        query = f"""
            SELECT
                COALESCE(role_category, 'Unclassified') AS role_category,
                COUNT(*) AS job_count
            FROM read_parquet('{JOBS_PARQUET_PATH_SQL}')
            WHERE status = 'active'
            GROUP BY role_category
            ORDER BY job_count DESC
        """
        df = con.execute(query).fetchdf()
        return df.to_dict(orient="records")
    except Exception as exc:
        logger.error("get_role_distribution failed: %s", exc)
        return []
    finally:
        con.close()


def get_data_quality_info() -> Dict[str, Any]:
    """Return basic data quality stats from Silver."""
    if not _has_silver_data():
        return {
            "data_available": False,
            "message": "No data has been ingested yet.",
        }

    con = _connect()
    try:
        query = f"""
            SELECT
                COUNT(*)                                                    AS total,
                SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END)           AS null_country,
                SUM(CASE WHEN role_category IS NULL THEN 1 ELSE 0 END)     AS unclassified,
                SUM(CASE WHEN description IS NULL THEN 1 ELSE 0 END)       AS null_description,
                MAX(ingested_at)                                            AS last_ingested_at
            FROM read_parquet('{JOBS_PARQUET_PATH_SQL}')
        """
        row = con.execute(query).fetchone()
        total = int(row[0] or 0)
        return {
            "data_available": total > 0,
            "total_records": total,
            "null_country_count": int(row[1] or 0),
            "unclassified_count": int(row[2] or 0),
            "null_description_count": int(row[3] or 0),
            "last_ingested_at": str(row[4]) if row[4] else None,
            "null_country_rate": round(int(row[1] or 0) / total * 100, 1) if total else 0,
            "unclassified_rate": round(int(row[2] or 0) / total * 100, 1) if total else 0,
        }
    except Exception as exc:
        logger.error("get_data_quality_info failed: %s", exc)
        return {"data_available": False, "error": str(exc)}
    finally:
        con.close()
