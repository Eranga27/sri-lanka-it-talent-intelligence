"""Jobs router — queries actual Silver Parquet via DuckDB."""
from fastapi import APIRouter, Query
from ..services import duckdb_service

router = APIRouter()


@router.get("/")
async def get_jobs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Paginated list of job records from Silver layer."""
    return duckdb_service.get_jobs(limit=limit, offset=offset)


@router.get("/summary")
async def get_jobs_summary():
    """Aggregate counts: total, active, Sri Lankan jobs."""
    return duckdb_service.get_jobs_summary()
