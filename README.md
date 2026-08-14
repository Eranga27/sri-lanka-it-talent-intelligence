# Sri Lanka IT Talent Intelligence

A data-driven, zero-cost IT job-market intelligence platform designed to observe, analyze, and visualize Sri Lankan IT industry demand and technology skill trends in real time.

---

## Architecture & Data Pipeline

The platform adheres strictly to a **Medallion Architecture (Bronze → Silver → Gold)** backed by local Parquet storage and DuckDB in-memory analytical querying:

```text
       PUBLIC ATS SOURCES (Greenhouse, Workable, Lever)
                             │
                             ▼
                    [ BRONZE LAYER ]
           Raw API payloads with audit provenance
                             │
                             ▼
                    [ SILVER LAYER ]
      Sri Lanka location filter + NLP Skill Extraction 
            + Deterministic V2 Role Classifier
                             │
                             ▼
                     [ GOLD LAYER ]
        Aggregated demand metrics (Parquet/DuckDB)
                             │
                             ▼
             [ FASTAPI ANALYTICAL BACKEND ]
                             │
                             ▼
          [ NEXT.JS INTELLIGENCE DASHBOARD UI ]
```

---

## Core Capabilities (Phases 1A – 1F Verified)

- **Multi-Source ATS Ingestion**: Ingests public vacancies from Greenhouse, Workable, and Lever.
- **Location Normalization**: Sri Lankan region and city parsing with strict non-LK filtering.
- **Deterministic Skill Extraction**: Word-boundary keyword & alias matching across 40+ technology categories.
- **V2 Role Classification**: Hybrid title, department, and extracted skill evidence scoring into 12 canonical IT role categories.
- **Gold Analytical Engine**: Aggregates role demand, skill demand, and market summary stats into Parquet/DuckDB.
- **FastAPI Endpoints**: High-performance REST endpoints backed by DuckDB SQL over Parquet.
- **Intelligence Dashboard**: Premium Next.js frontend with live market pulse, interactive skill filters, KPI cards, and methodology disclaimers.
- **Production Hardening**: Full automated test suite (67 pytest unit & data integrity tests), Playwright E2E test suite, Docker containerization, and GitHub Actions CI workflow.

---

## Local Setup & Quickstart

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional for containerized run)

### 1. Environment Configuration
```powershell
copy .env.example .env
```

### 2. Ingest Data & Execute Pipeline
Run the multi-source pipeline to fetch live vacancies, apply NLP skill extraction, role classification, and generate Gold datasets:
```powershell
python scripts/run_pipelines.py --layer all
```

### 3. Start FastAPI Backend API
```powershell
python -m uvicorn apps.api.app.main:app --reload --port 8000
```
- API Base: `http://localhost:8000/api/health`
- Swagger Docs: `http://localhost:8000/docs`

### 4. Start Next.js Frontend Dashboard
```powershell
cd apps/web
npm run dev
```
- Web Dashboard: `http://localhost:3000`

---

## Automated Testing

### Backend & Data Integrity Tests
Run all 67 Python unit, API, data integrity, and pipeline resilience tests:
```powershell
python -m pytest tests apps/api/tests -v
```

### Playwright End-to-End (E2E) Tests
Run browser tests across Desktop, Tablet, Mobile, and Reduced Motion viewports:
```powershell
cd apps/web
npm run test:e2e
```

---

## Docker Reproducibility

To launch the complete platform locally using Docker Compose:

```powershell
docker compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI Backend API**: `http://localhost:8000`

---

## GitHub Actions CI Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically runs on every push and pull request:
1. Pytest suite execution for unit, API, data integrity, and resilience tests.
2. Next.js production build validation (`npm run build`).
3. Playwright E2E testing using deterministic API contract mocking (no external network calls during CI).

---

## Security & Zero-Cost Philosophy

- **Zero Paid Dependencies**: Built entirely with open-source software (Python, Next.js, DuckDB, Parquet, Playwright, Docker).
- **No Mock Production Stats**: Every KPI displayed on the UI originates strictly from observed ATS vacancy data.
- **Security Hardened**: Configurable CORS origins, sanitized API error responses (preventing stack trace leakage), and isolated Docker execution.
