# Phase 1C: Multi-Source Sri Lankan IT Market Ingestion Report

**Date & Time**: 2026-08-13
**Status**: COMPLETE

## Objective
Expand the Phase 1B ingestion pipeline to include multiple public ATS sources (Greenhouse, Workable, Lever) while maintaining strict adherence to the zero-cost architecture and deterministic methodology.

---

## Live Validation Results

### 1. Greenhouse Connector (Existing & Refactored)
* **Target Boards**: canonical, gitlab
* **Timestamp**: 2026-08-13T18:08:40Z
* **HTTP Status**: 200 OK
* **Records Retrieved**: 497 total (Canonical: 302, GitLab: 195)
* **Sri Lankan Records**: 0
* **IT Records (Role Category Assigned)**: 184 (Based on deterministic rules)
* **Rejected Records**: 0
* **Validation Score**: 100.0%
* **Output Location**: `data/bronze/greenhouse/greenhouse_20260813_180840.parquet`
* **Source Health**: Healthy

### 2. Workable Connector (New)
* **Target Accounts**: homey, international-water-management-institute, orfium, unison, inivos
* **Timestamp**: 2026-08-13T18:08:44Z
* **HTTP Status**: 200 OK (following 302 redirects)
* **Records Retrieved**: 48 total
    - homey: 11
    - international-water-management-institute: 6
    - orfium: 22
    - unison: 0
    - inivos: 9
* **Sri Lankan Records**: 36
* **IT Records**: 21 (Based on deterministic rules)
* **Rejected Records**: 0
* **Validation Score**: 100.0%
* **Output Location**: `data/bronze/workable/workable_20260813_180840.parquet`
* **Source Health**: Healthy

### 3. Lever Connector (New)
* **Target Accounts**: leverdemo
* **Timestamp**: 2026-08-13T18:08:48Z
* **HTTP Status**: 200 OK
* **Records Retrieved**: 388 total
* **Sri Lankan Records**: 0 (Non-Sri Lankan fixture)
* **IT Records**: 160 (Based on deterministic rules)
* **Rejected Records**: 0
* **Validation Score**: 100.0%
* **Output Location**: `data/bronze/lever/lever_20260813_180840.parquet`
* **Source Health**: Healthy

### 4. Ashby Connector (Evaluation)
* **Status**: Excluded due to cost/auth constraints.
* **Findings**: The Ashby public jobs API does not offer a free, documented REST endpoint for fetching bulk public jobs without authentication credentials or unreliable GraphQL extraction. Kept out of scope for Phase 1C to adhere to the zero-cost requirement.

---

## Pipeline Statistics

* **Total Jobs Ingested**: 933 new records fetched across all sources.
* **Total Silver Output**: 938 records (including 5 expired jobs from previous runs).
* **Silver Location**: `data/silver/jobs.parquet`
* **Gold Location**: `data/gold/gold_role_demand.parquet` (Foundational aggregation for Sri Lankan market demand)

---

## Architectural Enhancements

1. **Connector Abstraction**: Expanded `BaseConnector` pattern. All connectors (Greenhouse, Workable, Lever) implement a unified interface `fetch()`, `validate()`, `normalize()`, `persist()`.
2. **Hierarchical Location Normalization**: Implemented `pipelines/transformations/location.py`. Now processes structured geographic data (Country, Region, City) with intelligent text fallback logic to deterministically identify Sri Lankan positions while preventing false positives.
3. **Partitioned Bronze Layer**: Raw JSON payloads are now securely stored per-source and per-timestamp, e.g., `data/bronze/{source}/{source}_{timestamp}.parquet`.
4. **Source Health Framework**: Augmented `SourceRegistryEntry` with health fields (`last_attempted_at`, `http_status`, `consecutive_failures`, `records_last_fetch`) to track reliability across different ATS platforms.

---

## Definition of Done Verification

- [x] Existing Greenhouse connector remains functional.
- [x] Workable connector is implemented.
- [x] Verified Workable accounts successfully returned live data.
- [x] Sri Lankan Workable records identified (36 found).
- [x] Bronze and Silver contain real multi-source observations.
- [x] Location normalization is improved.
- [x] Source health metadata tracked in domain model.
- [x] Gold market table foundations (e.g., `gold_role_demand.parquet`) dynamically built using DuckDB SQL.
- [x] FastAPI can query the expanded Silver layer.
- [x] Existing tests still pass.
- [x] New connector tests pass.
- [x] No fake statistics exist.
- [x] No paid services or proxies introduced.
- [x] No prohibited scraping logic used.
- [x] Documented in `docs/phase-1c-report.md`.

## Recommended Phase 1D

**Phase 1D: Applied NLP Classification & Skills Extraction**
With a robust multi-source data pipeline in place, the application must now process unstructured job descriptions to generate highly specific intelligence on exactly *what* technologies the Sri Lankan market is demanding.
1. Implement local, deterministic NLP parsing in `pipelines/skills` to extract granular technical keywords from job descriptions.
2. Advance `pipelines/classification` to assign "Unclassified" jobs to proper Role Categories using deeper linguistic heuristics, increasing classification yield.
3. Build `gold_skill_demand` for visualization of the most requested technologies in the local market.
