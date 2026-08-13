from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()

@router.get("/")
async def get_skills():
    """
    Stub for getting all canonical skills from taxonomy.
    """
    from pipelines.skills.taxonomy import TAXONOMY
    return TAXONOMY

@router.get("/demand")
async def get_skills_demand():
    """
    Returns actual gold_skill_demand dynamically computed.
    """
    return duckdb_service.get_skill_demand()
