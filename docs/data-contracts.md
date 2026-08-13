# Data Contracts

This document defines the core data contracts used in the platform.

## JobContract
The `JobContract` is the canonical schema for a job vacancy. All connectors must map source-specific representations to this contract in the Silver layer.
Fields:
- `job_id`: Unique identifier across the platform
- `source`: The origin of the data (e.g., "Greenhouse")
- `source_job_id`: The ID of the job in the source platform
- `title`, `company`, `location`, `description`
- `first_seen_at`, `last_seen_at`, `ingested_at`
- `status`: e.g., "active", "expired"

## SourceRegistry
Defines metadata about data sources to ensure provenance and tracking.
- `source_id`, `source_name`, `reliability_score`, `integration_status`

## SkillTaxonomy
Canonical representation of IT skills.
- `skill_id`, `canonical_name`, `category`, `aliases`
