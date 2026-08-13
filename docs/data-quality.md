# Data Quality Framework

The platform implements automated data quality checks on ingested records to ensure reliability and trust in the analytical metrics.

## Key Metrics
- **Schema Validity**: Validation against Pydantic models.
- **Null Rates**: Acceptable missing values for non-critical fields.
- **Duplicates**: Identification of duplicate job postings across platforms.
- **Freshness**: Monitoring the `last_seen_at` field to deprecate stale postings.

## Quality Scores
Each pipeline run produces a `DataQualityReport` which includes a calculated `data_quality_score`. This score will eventually be monitored and alert maintainers if a connector starts producing degraded data.
