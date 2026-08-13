"""
Canonical domain models for the Sri Lanka IT Talent Intelligence platform.

All analytical values shown by the application must originate from
actual source data — never hardcoded.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class JobContract(BaseModel):
    """
    Canonical job vacancy record.

    Fields the source does not provide must be set to None.
    Values must never be fabricated.
    """
    job_id: str
    source: str
    source_job_id: str
    company: Optional[str] = None
    title: str
    description: Optional[str] = None
    location_raw: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    location_detection_method: Optional[str] = None
    location_confidence: Optional[float] = None
    employment_type: Optional[str] = None
    department: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills_raw: Optional[List[str]] = None
    role_category: Optional[str] = None
    classification_method: Optional[str] = None
    classification_confidence: Optional[float] = None
    posted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    application_url: Optional[str] = None
    source_url: Optional[str] = None
    first_seen_at: datetime
    last_seen_at: datetime
    status: str
    ingested_at: datetime


class SourceRegistryEntry(BaseModel):
    """Registered data source with provenance and integration metadata."""
    source_id: str
    source_name: str
    owner: str
    source_type: str
    domain: str
    geographic_scope: str
    access_method: str
    api_available: bool
    authentication_required: bool
    refresh_frequency: str
    historical_depth: str
    terms_status: str
    reliability_score: float
    integration_status: str
    last_attempted_at: Optional[datetime] = None
    last_successful_fetch: Optional[datetime] = None
    last_error: Optional[str] = None
    http_status: Optional[int] = None
    records_last_fetch: Optional[int] = None
    consecutive_failures: int = 0
    source_health: str = "not_configured"
    notes: Optional[str] = None


class SkillTaxonomyEntry(BaseModel):
    """Canonical skill entry. Demand percentages are never stored here."""
    skill_id: str
    canonical_name: str
    category: str
    aliases: List[str]
    technology_family: Optional[str] = None
    active: bool = True


class DataQualityReport(BaseModel):
    """Result of a single pipeline quality run."""
    run_id: str
    source: str
    timestamp: datetime
    records_fetched: int
    records_accepted: int
    records_rejected: int
    duplicates_detected: int
    validation_errors: dict
    processing_time_ms: float
    data_quality_score: float
    output_bronze_path: Optional[str] = None
    output_silver_path: Optional[str] = None
