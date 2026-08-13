"""Market intelligence router — Phase 1B returns system status only."""
from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()


@router.get("/")
async def get_market():
    """
    Market intelligence endpoint.
    Returns summary + role distribution for Phase 1B.
    """
    summary = duckdb_service.get_jobs_summary()
    roles = duckdb_service.get_role_distribution()
    return {
        "summary": summary,
        "role_distribution": roles,
        "note": (
            "Skills and talent pipeline analytics will be added in Phase 1C "
            "once classification and skill-extraction pipelines are complete."
        ),
    }
