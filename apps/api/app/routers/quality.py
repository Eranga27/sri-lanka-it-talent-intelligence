"""Data quality router — reflects actual Silver data quality metrics."""
from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()


@router.get("/")
async def get_data_quality():
    """Return data quality metrics computed from the current Silver dataset."""
    return duckdb_service.get_data_quality_info()
