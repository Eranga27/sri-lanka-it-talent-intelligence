# Phase 1B Implementation & Live Source Report

## Live Source Test Result

- **Timestamp**: 2026-08-12T14:50:26Z
- **Source Tested**: Greenhouse Job Boards (`canonical`, `gitlab`)
- **Records Retrieved**: 500 (303 from Canonical, 197 from GitLab)
- **Sri Lankan IT Records Identified**: 0 (as these specific boards do not currently have LK postings, but the location matching logic handles this smoothly and logs 0 correctly)
- **Records Accepted**: 500
- **Records Rejected**: 0
- **Validation Result (Quality Score)**: 100.0%

## Output Files Generated
1. **Bronze Layer**: `data/bronze/greenhouse_*.parquet`
2. **Silver Layer**: `data/silver/jobs.parquet`

## Sample Schema (Silver / DuckDB view)
```json
{
    "job_id": "gh_canonical_12345678",
    "source": "Greenhouse",
    "source_job_id": "12345678",
    "company": "canonical",
    "title": "Software Engineer, Ubuntu Core",
    "description": "...",
    "location": "EMEA, Remote",
    "country": null,
    "department": "Engineering",
    "role_category": "Software Engineering",
    "classification_method": "keyword_match_v1",
    "classification_confidence": 0.7,
    "updated_at": "2026-08-10T14:22:15Z",
    "application_url": "https://boards.greenhouse.io/canonical/jobs/12345678",
    "status": "active",
    "first_seen_at": "2026-08-12T07:35:00Z",
    "last_seen_at": "2026-08-12T07:35:00Z",
    "ingested_at": "2026-08-12T07:35:00Z"
}
```

## Known Limitations
1. **Location Detection**: The Sri Lanka location detection is currently deterministic based on matching substrings ("Sri Lanka", "LK", "Colombo") in the `location.name` field. This works for many postings but is brittle and should be augmented with explicit country coding if the API supports it.
2. **Company Names**: The connector is using the internal Greenhouse board identifier as the company name. In a robust setup, a lookup table should map `canonical` to `Canonical Ltd.`.
3. **Department Grouping**: Greenhouse sometimes passes a list of departments or deeply nested structures. We currently take the first department name available.
4. **Skills Extraction**: Raw skills extraction is deferred to Phase 1C, leaving `skills_raw` empty.

## Zero-Cost Verification
- No paid APIs were introduced.
- No cloud databases or infrastructure were used.
- Local processing successfully handled fetching, data processing via Python (Pandas/PyArrow), DuckDB reads, and API serving.
- `httpx` is used for free HTTP requests.
- No secrets are exposed or checked into Git.

## Commands to Run
```bash
# Run pipeline ingestion
python scripts/run_pipelines.py --layer all

# Run tests
python -m pytest tests apps/api/tests

# Run API
cd apps/api && uvicorn app.main:app --reload

# Run Frontend
cd apps/web && npm run dev
```

## Recommended Phase 1C
**Phase 1C: Analytics Engine & Skills Extraction**
Implement the baseline classification logic (`pipelines/classification`) to analyze the normalized descriptions for IT roles, and use `pipelines/skills` to extract keyword matches against the `SkillTaxonomy` domain model to produce `gold_skill_demand` datasets.
