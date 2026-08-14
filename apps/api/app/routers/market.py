from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()

@router.get("/")
async def get_market():
    """
    Market intelligence root endpoint.
    """
    summary = duckdb_service.get_jobs_summary()
    roles = duckdb_service.get_role_distribution()
    return {
        "summary": summary,
        "role_distribution": roles,
    }

@router.get("/summary")
async def get_market_summary():
    """
    Market intelligence summary.
    """
    return duckdb_service.get_market_summary()

@router.get("/coverage")
async def get_market_coverage():
    """
    Market coverage metrics.
    """
    return duckdb_service.get_coverage_metrics()

