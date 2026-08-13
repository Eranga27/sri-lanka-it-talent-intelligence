# Sri Lanka IT Talent Intelligence

A data-driven web platform designed to analyze the relationship between IT industry demand and IT talent supply in Sri Lanka.

## Project Purpose
To provide continuously refreshed intelligence on IT job demand, vacancies, roles, technical skills, and talent supply in Sri Lanka. This is a robust data engineering and analytics project, not a static dashboard. All analytical values shown originate from actual source data and are calculated dynamically.

## Architecture & Technology Stack
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, Pydantic
- **Data Engineering**: Python, PyArrow, DuckDB, Parquet
- **Architecture**: Medallion-style architecture (Bronze -> Silver -> Gold layers)

## Zero-Cost Philosophy
This project is built using:
- Open-source software
- Free/public APIs
- Free official datasets
- Local execution & storage
- No required paid SaaS services

## Data Provenance
Every external data record retains its source, source ID, ingestion timestamps, and source-specific metadata to ensure complete traceability.

## Current Data Sources (Registered)
- Department of Census and Statistics — Sri Lanka
- ICTA — National IT-BPM Workforce Survey
- Greenhouse Job Board
- SmartRecruiters

## Limitations
- Fake analytical metrics are not used. Until data pipelines are fully hydrated, UI components will show empty states.

## Local Setup
1. Clone the repository.
2. Run `cp .env.example .env`.
3. Set up the Python virtual environment: `python -m venv .venv` and `pip install -r requirements.txt`.
4. Run FastAPI backend: `cd apps/api && uvicorn app.main:app --reload`.
5. Run Next.js frontend: `cd apps/web && npm run dev`.

## Future Roadmap
- Implementation of Bronze/Silver/Gold data pipelines.
- Data connectors for selected sources.
- Job classification and skill extraction logic.
- Advanced analytics on IT talent supply vs demand.
