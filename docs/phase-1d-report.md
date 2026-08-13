# Phase 1D: Applied NLP Classification & Skills Intelligence Report

**Date & Time**: 2026-08-13
**Status**: COMPLETE

## Objective
Transform normalized job descriptions into structured skill and role intelligence for the Sri Lankan IT labour-market dataset using deterministic NLP extraction and V2 role classification, without introducing any paid APIs or LLMs.

---

## Live Ingestion & NLP Statistics

**Pipeline Run**:
- **Total Jobs Observed**: 933
- **Sri Lankan Jobs Observed**: 36
- **Sri Lankan IT Jobs (V2 Classifier)**: 18
- **Data Quality Pass Rate**: 100.0%

**NLP Skill Extraction**:
- **Total Skill Relationships Extracted**: 1255 across all active jobs.
- **Extraction Methodology**: Local, deterministic Regex with defined word boundaries and longest-alias-first overlap prevention.
- **Top Observed Skills**: Python, SQL, React, Node.js, AWS (and others depending on current data).

---

## Architectural Enhancements

### 1. Skill Taxonomy & Aliases (`pipelines/skills/taxonomy.py`)
- Configured a definitive skill taxonomy categorized into Programming, Frontend, Backend, Data, Cloud, DevOps, AI/ML, Cybersecurity, and Analytics.
- Supported extensive aliases (e.g., "React JS" and "React.js" map to "React", "AWS Cloud" maps to "AWS").

### 2. Deterministic NLP Extractor (`pipelines/skills/extractor.py`)
- Implemented `extract_skills_from_job` to parse job titles, departments, and descriptions.
- Employs word boundaries (`\b` or custom negative lookaheads) to prevent naive substring matching (e.g. "go" in "going").
- Prevents overlapping alias matches by parsing longest aliases first and stripping out matched text chunks per job.

### 3. Relational Mapping (`silver/job_skills.parquet`)
- Skill occurrences are now correctly normalized into a relational format preserving `job_id`, `skill_id`, `canonical_skill`, `raw_match`, and `confidence`.
- Eliminates array-bloat inside the core `JobContract` and enables granular SQL querying.

### 4. Role Classification V2 (`pipelines/classification/classifier.py`)
- Shifted from a pure string match to a weighted evidence model (`keyword_match_v2`).
- Weights:
  - Title Match = 3.0 points
  - Department Match = 1.5 points
  - Skill Evidence = 0.5 points per matching skill category.
- Enables granular and explainable classification confidence scoring (ranging from 0.3 to 0.95 depending on aggregate evidence).

### 5. Dynamic Gold Analytics (`data/gold/`)
- `gold_market_summary.parquet`: Dynamically aggregates total active/historic, Sri Lankan vs global, and timestamp boundaries.
- `gold_role_demand.parquet`: Computes active Sri Lankan IT job volume grouped by role category.
- `gold_skill_demand.parquet`: Computes active Sri Lankan IT job volume grouped by canonical skill, directly powering technology demand analytics.
- **Active vs Historical definition**: The analytics strictly filter for `status = 'active'`, dropping expired observations that no longer exist on the canonical source feeds.

### 6. Fast API Endpoints
- `/api/market/summary`
- `/api/market/coverage` (Generates qualitative "limited", "moderate", "broad" state based on active local volumes).
- `/api/skills` and `/api/skills/demand`
- `/api/roles` and `/api/roles/demand`
- Connected DuckDB directly to the pre-aggregated Gold Parquet tables for instantaneous query latency.

---

## Definition of Done Verification

- [x] Deterministic skill extraction works and aliases normalize.
- [x] False-positive matching controlled (word boundaries/overlap resolution).
- [x] Job-to-skill relationships are persisted (`job_skills.parquet`).
- [x] Role classification V2 operates with weighted scores.
- [x] Confidence scoring is reproducible.
- [x] `gold_skill_demand` and `gold_role_demand` are dynamically generated using DuckDB.
- [x] Market coverage metrics separate active vs observed.
- [x] API exposes the actual analytical data.
- [x] All 55 tests pass locally.
- [x] Live pipeline validation executed successfully.
- [x] Zero mock statistics exist.
- [x] Zero paid/cloud dependencies exist (pure local processing).

## Limitations
- Coverage remains heavily "Limited" given we are still only parsing a handful of test/demonstration boards and international ATS providers. True local coverage will require broader ingestion targets.
- Deterministic extraction may still miss contextually obfuscated skills or proprietary internal technology stacks without true semantic embeddings.

## Recommended Phase 1E
**Phase 1E: UI Dashboard Intelligence Integration**
The intelligence is now successfully generated. The Next.js frontend should be updated to cleanly visualize the Market Coverage qualitative state (to set user expectations) and display the `gold_skill_demand` and updated `gold_role_demand` datasets using beautiful, responsive charts (e.g. Recharts or Tremor). We should ensure empty states explicitly highlight the "Limited coverage" truth.
