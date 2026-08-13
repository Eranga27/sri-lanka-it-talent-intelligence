"""Skills router — Phase 1C placeholder."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_skills():
    """
    Skill demand data.
    Will be populated after Phase 1C skill-extraction pipeline is complete.
    """
    return {
        "data": [],
        "message": (
            "Skill extraction pipeline not yet active. "
            "Run Phase 1C to populate skill demand data."
        ),
    }
