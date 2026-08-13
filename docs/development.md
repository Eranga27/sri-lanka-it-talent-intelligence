# Development Guide

## Project Setup
Ensure you have Node.js and Python installed.

1. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

2. Run the FastAPI server:
```bash
cd apps/api
uvicorn app.main:app --reload
```

3. Run the Next.js frontend:
```bash
cd apps/web
npm install
npm run dev
```

## Adding a New Connector
1. Create a new class inheriting from `BaseConnector` in `pipelines/connectors/`.
2. Implement `fetch`, `validate`, `normalize`, and `persist`.
3. Add the connector to the pipeline orchestration script.
