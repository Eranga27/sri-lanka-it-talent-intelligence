from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()

@router.get("/")
async def get_roles():
    """
    Stub for canonical roles.
    """
    from pipelines.classification.classifier import _ROLE_TAXONOMY
    return list(_ROLE_TAXONOMY.keys())

@router.get("/demand")
async def get_roles_demand():
    """
    Returns actual gold_role_demand dynamically computed.
    """
    return duckdb_service.get_role_demand()
