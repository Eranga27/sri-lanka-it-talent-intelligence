"""
Unit tests for the Greenhouse connector.

Uses fixtures and httpx mock transport — no live network calls.
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

import httpx

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pipelines.connectors.greenhouse import (
    GreenhouseConnector,
    _classify_role,
    _detect_sri_lanka,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_job(
    job_id=111,
    title="Software Engineer",
    board="testboard",
    location_name="Colombo, Sri Lanka",
    department="Engineering",
    updated_at="2026-08-01T10:00:00.000Z",
    absolute_url="https://boards.greenhouse.io/testboard/jobs/111",
    content="<p>Build great software.</p>",
):
    return {
        "id": job_id,
        "title": title,
        "location": {"name": location_name},
        "departments": [{"id": 1, "name": department, "child_ids": [], "parent_id": None}],
        "updated_at": updated_at,
        "absolute_url": absolute_url,
        "content": content,
        "_board_source": board,
        "_fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _greenhouse_response(jobs):
    return {"jobs": jobs, "meta": {"total": len(jobs)}}


class _MockTransport(httpx.BaseTransport):
    """Deterministic mock transport."""

    def __init__(self, responses: dict):
        self._responses = responses  # url → (status_code, json_body)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        for key, (code, body) in self._responses.items():
            if key in url:
                return httpx.Response(
                    status_code=code,
                    content=json.dumps(body).encode(),
                    headers={"content-type": "application/json"},
                )
        return httpx.Response(404, content=b'{"status":404,"error":"Not found"}')


# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------

class TestRoleClassification:
    def test_software_engineering(self):
        cat, method, conf = _classify_role("Software Engineer", "Engineering")
        assert cat == "Software Engineering"
        assert conf > 0

    def test_ml_engineer(self):
        cat, method, conf = _classify_role("Machine Learning Engineer", None)
        assert cat == "Artificial Intelligence & Machine Learning"

    def test_devops(self):
        cat, method, conf = _classify_role("DevOps Engineer", "Infrastructure")
        assert cat == "Cloud & DevOps"

    def test_unclassified(self):
        cat, method, conf = _classify_role("Office Manager", "HR")
        assert cat is None
        assert conf == 0.0


# ---------------------------------------------------------------------------
# Location detection tests
# ---------------------------------------------------------------------------

class TestSriLankaDetection:
    def test_colombo(self):
        country, is_lk = _detect_sri_lanka("Colombo, Sri Lanka")
        assert country == "Sri Lanka"
        assert is_lk is True

    def test_sri_lanka_explicit(self):
        country, is_lk = _detect_sri_lanka("Sri Lanka - Remote")
        assert is_lk is True

    def test_lk_isolated(self):
        country, is_lk = _detect_sri_lanka("Colombo, LK")
        assert is_lk is True

    def test_not_sri_lanka(self):
        country, is_lk = _detect_sri_lanka("London, United Kingdom")
        assert is_lk is False
        assert country is None

    def test_empty_location(self):
        country, is_lk = _detect_sri_lanka("")
        assert is_lk is False

    def test_none_location(self):
        country, is_lk = _detect_sri_lanka(None)
        assert is_lk is False


# ---------------------------------------------------------------------------
# Connector fetch tests
# ---------------------------------------------------------------------------

class TestGreenhouseConnectorFetch:
    def _make_connector(self, transport):
        connector = GreenhouseConnector(
            source_id="test",
            config={"boards": ["testboard"], "timeout": 5, "max_retries": 1},
        )
        return connector, transport

    def test_successful_fetch(self):
        jobs = [_make_job(111), _make_job(222)]
        transport = _MockTransport({"testboard/jobs": (200, _greenhouse_response(jobs))})

        connector = GreenhouseConnector(
            source_id="test",
            config={"boards": ["testboard"], "timeout": 5, "max_retries": 1},
        )

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = lambda s: mock_client
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = _greenhouse_response(jobs)
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response

            result = connector.fetch()
            assert len(result) == 2
            assert result[0]["_board_source"] == "testboard"

    def test_http_404_returns_empty(self):
        connector = GreenhouseConnector(
            source_id="test",
            config={"boards": ["nonexistent_board"], "timeout": 5, "max_retries": 1},
        )
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = lambda s: mock_client
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 404
            err = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)
            mock_client.get.side_effect = err

            result = connector.fetch()
            assert result == []

    def test_timeout_returns_empty(self):
        connector = GreenhouseConnector(
            source_id="test",
            config={"boards": ["slow_board"], "timeout": 1, "max_retries": 1},
        )
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = lambda s: mock_client
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("timed out")

            result = connector.fetch()
            assert result == []

    def test_no_boards_configured(self):
        connector = GreenhouseConnector(
            source_id="test",
            config={"boards": [], "timeout": 5, "max_retries": 1},
        )
        result = connector.fetch()
        assert result == []


# ---------------------------------------------------------------------------
# Connector normalization tests
# ---------------------------------------------------------------------------

class TestGreenhouseConnectorNormalize:
    def _connector(self):
        return GreenhouseConnector(
            source_id="test",
            config={"boards": ["testboard"]},
        )

    def test_valid_record(self):
        connector = self._connector()
        raw = [_make_job()]
        result = connector.normalize(raw)
        assert len(result) == 1
        r = result[0]
        assert r["source"] == "Greenhouse"
        assert r["source_job_id"] == "111"
        assert r["company"] == "testboard"
        assert r["country"] == "Sri Lanka"
        assert r["role_category"] == "Software Engineering"

    def test_missing_optional_fields(self):
        connector = self._connector()
        raw = [{
            "id": 999,
            "title": "Unknown Role",
            "location": {},
            "departments": [],
            "updated_at": None,
            "absolute_url": None,
            "content": None,
            "_board_source": "testboard",
            "_fetched_at": "2026-08-12T10:00:00Z",
        }]
        result = connector.normalize(raw)
        assert len(result) == 1
        r = result[0]
        assert r["location"] is None
        assert r["country"] is None
        assert r["department"] is None
        assert r["description"] is None

    def test_non_lk_location(self):
        connector = self._connector()
        raw = [_make_job(location_name="San Francisco, CA")]
        result = connector.normalize(raw)
        assert result[0]["country"] is None

    def test_job_id_format(self):
        connector = self._connector()
        raw = [_make_job(job_id=42, board="myboard")]
        result = connector.normalize(raw)
        assert result[0]["job_id"] == "gh_myboard_42"

    def test_empty_input(self):
        connector = self._connector()
        result = connector.normalize([])
        assert result == []


# ---------------------------------------------------------------------------
# Timestamp logic tests
# ---------------------------------------------------------------------------

class TestTimestampLogic:
    """Test first_seen_at preservation (simulated via pipeline logic)."""

    def test_first_observation(self):
        """New job gets first_seen_at == now."""
        from scripts.run_pipelines import _apply_timestamps
        now = "2026-08-12T10:00:00+00:00"
        jobs = [{"job_id": "gh_test_1", "title": "Dev"}]
        result = _apply_timestamps(jobs, existing_first_seen={}, now_iso=now)
        assert result[0]["first_seen_at"] == now
        assert result[0]["last_seen_at"] == now

    def test_repeated_observation_preserves_first_seen(self):
        """Existing job keeps original first_seen_at."""
        from scripts.run_pipelines import _apply_timestamps
        original_first = "2026-08-01T08:00:00+00:00"
        now = "2026-08-12T10:00:00+00:00"
        jobs = [{"job_id": "gh_test_1", "title": "Dev"}]
        result = _apply_timestamps(
            jobs,
            existing_first_seen={"gh_test_1": original_first},
            now_iso=now,
        )
        assert result[0]["first_seen_at"] == original_first
        assert result[0]["last_seen_at"] == now


# ---------------------------------------------------------------------------
# Duplicate detection tests
# ---------------------------------------------------------------------------

class TestDuplicateDetection:
    def test_no_duplicates(self):
        from scripts.run_pipelines import _detect_duplicates
        jobs = [
            {"source": "Greenhouse", "source_job_id": "1"},
            {"source": "Greenhouse", "source_job_id": "2"},
        ]
        unique, dups = _detect_duplicates(jobs)
        assert len(unique) == 2
        assert dups == 0

    def test_detects_duplicates(self):
        from scripts.run_pipelines import _detect_duplicates
        jobs = [
            {"source": "Greenhouse", "source_job_id": "1"},
            {"source": "Greenhouse", "source_job_id": "1"},  # duplicate
        ]
        unique, dups = _detect_duplicates(jobs)
        assert len(unique) == 1
        assert dups == 1
