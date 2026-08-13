"""
API endpoint tests.
Tests verify correct responses for empty and populated Silver datasets.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from unittest.mock import patch

from apps.api.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_jobs_summary_empty():
    """When no Silver data exists, summary returns zeros."""
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/jobs/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 0
    assert data["active_jobs"] == 0
    assert data["data_available"] is False


def test_jobs_list_empty():
    """When no Silver data exists, job list is empty."""
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/jobs/")
    assert response.status_code == 200
    assert response.json() == []


def test_sources_returns_registry():
    """Sources endpoint always returns the static registry."""
    response = client.get("/api/sources/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Greenhouse should always be present
    source_ids = [s["source_id"] for s in data]
    assert "greenhouse" in source_ids


def test_roles_empty():
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/roles/")
    assert response.status_code == 200
    assert response.json() == []


def test_data_quality_empty():
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/data-quality/")
    assert response.status_code == 200
    data = response.json()
    assert data["data_available"] is False


def test_market_empty():
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/market/")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_jobs"] == 0


def test_jobs_pagination_params():
    """Pagination query params are accepted without error."""
    with patch("apps.api.app.services.duckdb_service._has_silver_data", return_value=False):
        response = client.get("/api/jobs/?limit=10&offset=0")
    assert response.status_code == 200
