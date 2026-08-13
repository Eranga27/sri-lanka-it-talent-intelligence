# Architecture

The Sri Lanka IT Talent Intelligence platform uses a modern, lightweight, Medallion-style data architecture, optimized for local execution without requiring paid cloud infrastructure.

## System Components

### Frontend (Next.js)
A Next.js based web application providing a premium, data-centric interface. It consumes the FastAPI endpoints to render live analytics on the IT talent market.

### Backend (FastAPI)
A Python-based REST API that serves analytical datasets to the frontend. It queries the Gold layer datasets and applies business logic for the UI.

### Data Pipelines (Python)
ETL pipelines that ingest, validate, and normalize data from various ATS systems and official statistical sources.
- **Connectors**: Abstractions to pull data from sources (e.g., Greenhouse).
- **Ingestion**: Raw data is saved to the Bronze layer.
- **Transformations**: Normalization to canonical schema into the Silver layer.
- **Classification & Skills**: Data enrichment applied to create the Gold analytical datasets.

### Data Storage (Local)
- **DuckDB**: Used for fast analytical queries over the data layers.
- **Parquet**: Used for storing Bronze, Silver, and Gold datasets efficiently on disk.

## Medallion Architecture

1. **Bronze Layer**: Raw source data with ingestion timestamps and source metadata. Data here is immutable.
2. **Silver Layer**: Normalized data conforming to the `JobContract` and canonical schemas. Basic data quality rules have been applied.
3. **Gold Layer**: Aggregated, analytics-ready datasets (e.g., skill demand metrics, weekly vacancy volume).
