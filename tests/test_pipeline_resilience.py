"""
Automated Pipeline Resilience & Idempotency Tests.
Verifies pipeline stability under source failures and repeated runs.
"""
import pytest
from unittest.mock import patch, MagicMock

from pipelines.connectors.greenhouse import GreenhouseConnector
from pipelines.connectors.workable import WorkableConnector
from pipelines.connectors.lever import LeverConnector


def test_greenhouse_idempotency_normalization():
    """
    Normalizing the same job record twice produces identical, stable records with unchanged job_id.
    """
    raw_job = {
        "id": 998877,
        "title": "Backend Engineer",
        "location": {"name": "Colombo, Sri Lanka"},
        "updated_at": "2026-08-01T10:00:00Z",
        "absolute_url": "https://boards.greenhouse.io/canonical/jobs/998877",
    }
    conn = GreenhouseConnector(source_id="greenhouse_test")
    norm1 = conn.normalize([raw_job])
    norm2 = conn.normalize([raw_job])

    assert len(norm1) == 1
    assert len(norm2) == 1
    assert norm1[0]["job_id"] == norm2[0]["job_id"]
    assert norm1[0]["source_job_id"] == norm2[0]["source_job_id"] == "998877"
    assert norm1[0]["country"] == "Sri Lanka"


def test_source_failure_resilience_greenhouse_error():
    """
    When Greenhouse API returns a network error, fetch returns an empty list without raising an unhandled exception.
    """
    conn = GreenhouseConnector(source_id="greenhouse_test", config={"boards": ["testboard"]})
    with patch("httpx.Client.get", side_effect=Exception("Connection refused")):
        results = conn.fetch()

    # Must return empty list gracefully
    assert results == []


def test_source_failure_resilience_workable_error():
    """
    When Workable API returns HTTP 500, fetch handles error and returns empty list.
    """
    conn = WorkableConnector(source_id="workable_test", config={"boards": ["testboard"]})
    mock_resp = MagicMock()
    mock_resp.status_code = 500

    with patch("httpx.Client.get", return_value=mock_resp):
        results = conn.fetch()

    assert results == []


def test_source_failure_resilience_lever_error():
    """
    When Lever API returns HTTP 404, fetch returns empty list without crashing.
    """
    conn = LeverConnector(source_id="lever_test", config={"boards": ["testboard"]})
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    with patch("httpx.Client.get", return_value=mock_resp):
        results = conn.fetch()

    assert results == []
