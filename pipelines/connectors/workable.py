"""
Workable Job Board Connector

Fetches job listings from Workable public job board API.
No authentication required for public boards.
"""
import httpx
import logging
import time
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime, timezone

from .base import BaseConnector
from .greenhouse import _classify_role
from pipelines.transformations.location import normalize_location

logger = logging.getLogger(__name__)

class WorkableConnector(BaseConnector):
    """
    Connector for the Workable public job board API.
    """

    BASE_URL = "https://www.workable.com/api/accounts/"

    def __init__(self, source_id: str, config: Dict[str, Any] = None):
        super().__init__(source_id, config)
        self.api_url = self.config.get("api_url", self.BASE_URL)
        self.boards: List[str] = self.config.get("boards", [])
        self.timeout: int = self.config.get("timeout", 30)
        self.max_retries: int = self.config.get("max_retries", 3)
        self.retry_delay: float = self.config.get("retry_delay", 2.0)

    def fetch(self) -> List[Dict[str, Any]]:
        all_jobs: List[Dict[str, Any]] = []
        
        if not self.boards:
            logger.warning("No Workable boards configured.")
            return all_jobs

        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            for board in self.boards:
                board_jobs, _stats = self._fetch_board(client, board)
                all_jobs.extend(board_jobs)

        total = len(all_jobs)
        logger.info("Workable fetch complete. Total records: %d from %d board(s).", total, len(self.boards))
        return all_jobs

    def validate(self, raw_data: List[Dict[str, Any]]) -> bool:
        if not isinstance(raw_data, list):
            return False
        if raw_data and not isinstance(raw_data[0], dict):
            return False
        return True

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        skipped = 0

        for raw_job in raw_data:
            try:
                norm = self._normalize_record(raw_job)
                normalized.append(norm)
            except Exception as exc:
                skipped += 1
                logger.warning("Failed to normalize workable job %s: %s", raw_job.get("shortcode", "unknown"), exc)

        if skipped:
            logger.warning("Skipped %d Workable records during normalization.", skipped)

        logger.info("Normalized %d Workable records.", len(normalized))
        return normalized

    def persist(self, normalized_data: List[Dict[str, Any]]) -> None:
        pass

    def _fetch_board(self, client: httpx.Client, board: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        url = f"{self.api_url}{board}?details=true"
        stats = {"board": board, "records": 0, "status": "ok", "error": None}

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Fetching Workable board '%s' — attempt %d/%d URL: %s", board, attempt, self.max_retries, url)
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])

                ingested_ts = datetime.now(timezone.utc).isoformat()
                for job in jobs:
                    job["_board_source"] = board
                    job["_fetched_at"] = ingested_ts

                stats["records"] = len(jobs)
                logger.info("Workable Board '%s': retrieved %d jobs.", board, len(jobs))
                return jobs, stats

            except httpx.HTTPStatusError as exc:
                stats["status"] = "http_error"
                stats["error"] = str(exc)
                logger.error("HTTP %s for Workable board '%s': %s", exc.response.status_code, board, exc)
                if exc.response.status_code == 404:
                    break
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

            except Exception as exc:
                stats["status"] = "unexpected_error"
                stats["error"] = str(exc)
                logger.error("Error fetching Workable board '%s': %s", board, exc)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    break

        return [], stats

    def _normalize_record(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        board = raw_job.get("_board_source", "unknown")
        source_job_id = str(raw_job.get("shortcode", ""))
        
        raw_country = raw_job.get("country")
        raw_region = raw_job.get("state")
        raw_city = raw_job.get("city")
        
        country, region, city, location, detection_method, confidence = normalize_location(
            raw_country=raw_country,
            raw_region=raw_region,
            raw_city=raw_city
        )
        
        title = raw_job.get("title") or ""
        department = raw_job.get("department")
        role_category, classification_method, classification_confidence = _classify_role(
            title, department
        )
        
        # published_on is e.g. "2026-06-10"
        published_on = raw_job.get("published_on")
        posted_at = None
        if published_on:
            posted_at = f"{published_on}T00:00:00Z"
            
        description = raw_job.get("description")
        
        return {
            "job_id": f"workable_{board}_{source_job_id}",
            "source": "Workable",
            "source_job_id": source_job_id,
            "company": board,
            "title": title,
            "description": description if description else None,
            "location_raw": f"{raw_city}, {raw_region}, {raw_country}" if raw_country else None,
            "location": location,
            "country": country,
            "region": region,
            "city": city,
            "location_detection_method": detection_method,
            "location_confidence": confidence,
            "employment_type": raw_job.get("employment_type"),
            "department": department,
            "experience_min": None,
            "experience_max": None,
            "education": raw_job.get("education"),
            "salary_min": None,
            "salary_max": None,
            "skills_raw": [],
            "role_category": role_category,
            "classification_method": classification_method,
            "classification_confidence": classification_confidence,
            "posted_at": posted_at,
            "updated_at": None,
            "application_url": raw_job.get("application_url"),
            "source_url": raw_job.get("url"),
            "status": "active",
        }
