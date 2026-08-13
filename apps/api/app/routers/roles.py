"""Roles router — job counts by IT role category from Silver."""
from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()


@router.get("/")
async def get_roles():
    """Distribution of active jobs by IT role category."""
    return duckdb_service.get_role_distribution()
