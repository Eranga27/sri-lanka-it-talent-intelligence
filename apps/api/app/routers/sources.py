"""Sources router — returns registered source metadata and ingestion stats."""
from fastapi import APIRouter
from ..services import duckdb_service

router = APIRouter()

# Static source registry — provenance metadata, not analytical results
_SOURCE_REGISTRY = [
    {
        "source_id": "greenhouse",
        "source_name": "Greenhouse Job Board",
        "owner": "Greenhouse Software Inc.",
        "source_type": "ATS / Job Board API",
        "domain": "Employment",
        "geographic_scope": "Global",
        "access_method": "Public REST API",
        "api_available": True,
        "authentication_required": False,
        "refresh_frequency": "Daily",
        "historical_depth": "Current listings only",
        "terms_status": "Public API — no authentication required for public boards",
        "reliability_score": 0.95,
        "integration_status": "ACTIVE",
        "notes": "Uses boards-api.greenhouse.io/v1/boards/{board}/jobs",
    },
    {
        "source_id": "dept_census_statistics_lk",
        "source_name": "Department of Census and Statistics — Sri Lanka",
        "owner": "Government of Sri Lanka",
        "source_type": "Official Statistical Publication",
        "domain": "Labour / Education / Workforce Statistics",
        "geographic_scope": "Sri Lanka",
        "access_method": "Manual download / web scrape",
        "api_available": False,
        "authentication_required": False,
        "refresh_frequency": "Annual / Ad hoc",
        "historical_depth": "Multi-year historical",
        "terms_status": "Public government data",
        "reliability_score": 0.90,
        "integration_status": "REGISTERED_NOT_INTEGRATED",
        "notes": "Official reference/benchmark source for labour statistics.",
    },
    {
        "source_id": "icta_itbpm_survey",
        "source_name": "ICTA — National IT-BPM Workforce Survey",
        "owner": "ICTA Sri Lanka",
        "source_type": "Official Survey Report",
        "domain": "IT/BPM Workforce Demand and Supply",
        "geographic_scope": "Sri Lanka",
        "access_method": "Manual download",
        "api_available": False,
        "authentication_required": False,
        "refresh_frequency": "Periodic (survey-based)",
        "historical_depth": "Survey editions",
        "terms_status": "Public report",
        "reliability_score": 0.88,
        "integration_status": "REGISTERED_NOT_INTEGRATED",
        "notes": "Official IT-BPM industry benchmark survey.",
    },
    {
        "source_id": "smartrecruiters",
        "source_name": "SmartRecruiters",
        "owner": "SmartRecruiters Inc.",
        "source_type": "ATS / Job Board API",
        "domain": "Employment",
        "geographic_scope": "Global",
        "access_method": "API (credentials required)",
        "api_available": True,
        "authentication_required": True,
        "refresh_frequency": "Daily (when integrated)",
        "historical_depth": "Current listings",
        "terms_status": "Requires API credentials per employer",
        "reliability_score": 0.85,
        "integration_status": "CANDIDATE_NOT_INTEGRATED",
        "notes": "Secondary connector candidate. Requires per-employer API credentials.",
    },
    {
        "source_id": "xpressjobs",
        "source_name": "XpressJobs",
        "owner": "XpressJobs (Pvt) Ltd",
        "source_type": "Job Board",
        "domain": "Sri Lankan Employment",
        "geographic_scope": "Sri Lanka",
        "access_method": "Potential future official partnership/API",
        "api_available": False,
        "authentication_required": False,
        "refresh_frequency": "N/A",
        "historical_depth": "N/A",
        "terms_status": "Do not scrape. Future official partnership only.",
        "reliability_score": None,
        "integration_status": "RESTRICTED",
        "notes": "Do not scrape without explicit permission.",
    },
    {
        "source_id": "ikman",
        "source_name": "ikman Jobs",
        "owner": "ikman (Pvt) Ltd",
        "source_type": "Classifieds / Job Board",
        "domain": "Sri Lankan Employment",
        "geographic_scope": "Sri Lanka",
        "access_method": "API (permission required)",
        "api_available": False,
        "authentication_required": True,
        "refresh_frequency": "N/A",
        "historical_depth": "N/A",
        "terms_status": "Do not scrape without appropriate permission/API.",
        "reliability_score": None,
        "integration_status": "RESTRICTED",
        "notes": "Do not scrape without explicit permission or API agreement.",
    },
]


@router.get("/")
async def get_sources():
    """Return all registered data sources with ingestion stats where available."""
    ingestion_stats = duckdb_service.get_sources_summary()
    stats_by_source = {s["source"]: s for s in ingestion_stats}

    enriched = []
    for src in _SOURCE_REGISTRY:
        entry = dict(src)
        source_name = src.get("source_name", "")
        # Match ingestion stats by source name
        stats = stats_by_source.get(source_name)
        if stats:
            entry["last_ingested_at"] = stats.get("last_ingested_at")
            entry["total_records_ingested"] = stats.get("total_records")
            entry["active_records"] = stats.get("active_records")
        else:
            entry["last_ingested_at"] = None
            entry["total_records_ingested"] = 0
            entry["active_records"] = 0
        enriched.append(entry)

    return enriched
