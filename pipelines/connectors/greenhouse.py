"""
Greenhouse Job Board Connector

Fetches job listings from Greenhouse public job board API.
No authentication required for public boards.
API reference: https://developers.greenhouse.io/job-board.html
"""
import httpx
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from .base import BaseConnector

logger = logging.getLogger(__name__)

# Sri Lanka location signals — deterministic keyword matching
_SL_KEYWORDS = [
    "sri lanka",
    "srilanka",
    "colombo",
    "kandy",
    "galle",
    "negombo",
    "dehiwala",
    "moratuwa",
    "kotte",
    "nugegoda",
    "battaramulla",
    "malabe",
    "kaduwela",
    "lk",       # country code (only trusted as LK if isolated or suffix)
]

# Role taxonomy — Phase 1B deterministic title/dept keyword classifier
_ROLE_TAXONOMY = {
    "Software Engineering": [
        "software engineer", "software developer", "backend", "frontend", "full stack",
        "fullstack", "mobile developer", "ios developer", "android developer",
        "java developer", "python developer", ".net developer", "golang",
    ],
    "Data & Analytics": [
        "data engineer", "data analyst", "analytics engineer", "bi developer",
        "business intelligence", "etl", "data pipeline", "data platform",
    ],
    "Artificial Intelligence & Machine Learning": [
        "machine learning", "ml engineer", "ai engineer", "deep learning",
        "nlp", "computer vision", "data scientist",
    ],
    "Cloud & DevOps": [
        "devops", "platform engineer", "sre", "site reliability", "cloud engineer",
        "infrastructure engineer", "aws", "gcp", "azure", "kubernetes", "terraform",
        "devsecops",
    ],
    "Cybersecurity": [
        "security engineer", "information security", "cybersecurity", "penetration",
        "soc analyst", "threat", "vulnerability",
    ],
    "QA & Testing": [
        "qa engineer", "quality assurance", "test engineer", "automation engineer",
        "sdet", "quality engineer",
    ],
    "UI/UX": [
        "ux designer", "ui designer", "product designer", "interaction designer",
        "ux researcher", "user experience",
    ],
    "IT Infrastructure": [
        "network engineer", "systems administrator", "sysadmin", "it support",
        "linux administrator", "windows administrator",
    ],
    "Business Analysis": [
        "business analyst", "systems analyst", "product analyst", "requirements",
    ],
    "Product Management": [
        "product manager", "product owner", "technical product",
    ],
    "IT Support": [
        "helpdesk", "help desk", "desktop support", "it support", "service desk",
    ],
    "Database & Data Administration": [
        "dba", "database administrator", "database engineer", "sql developer",
    ],
}


def _classify_role(title: str, department: Optional[str]) -> Tuple[Optional[str], str, float]:
    """
    Deterministic role classification against the IT taxonomy.

    Returns:
        (role_category, classification_method, confidence)
    """
    text = " ".join(filter(None, [title, department])).lower()

    for category, keywords in _ROLE_TAXONOMY.items():
        for kw in keywords:
            if kw in text:
                return category, "keyword_match_v1", 0.7

    # Could not confidently classify
    return None, "unclassified", 0.0


from pipelines.transformations.location import normalize_location


class GreenhouseConnector(BaseConnector):
    """
    Connector for the Greenhouse public job board API.

    Supports multiple boards configured via GREENHOUSE_BOARDS env var.
    No API credentials required for public boards.
    """

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards/"

    def __init__(self, source_id: str, config: Dict[str, Any] = None):
        super().__init__(source_id, config)
        self.api_url = self.config.get("api_url", self.BASE_URL)
        self.boards: List[str] = self.config.get("boards", [])
        self.timeout: int = self.config.get("timeout", 30)
        self.max_retries: int = self.config.get("max_retries", 3)
        self.retry_delay: float = self.config.get("retry_delay", 2.0)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw jobs from all configured Greenhouse boards."""
        all_jobs: List[Dict[str, Any]] = []
        fetch_stats: Dict[str, Any] = {}

        if not self.boards:
            logger.warning("No Greenhouse boards configured. Set GREENHOUSE_BOARDS in .env")
            return all_jobs

        with httpx.Client(timeout=self.timeout) as client:
            for board in self.boards:
                board_jobs, stats = self._fetch_board(client, board)
                all_jobs.extend(board_jobs)
                fetch_stats[board] = stats

        total = len(all_jobs)
        logger.info(
            "Greenhouse fetch complete. Total records: %d from %d board(s).",
            total,
            len(self.boards),
        )
        return all_jobs

    def validate(self, raw_data: List[Dict[str, Any]]) -> bool:
        """Basic structural validation of raw Greenhouse response."""
        if not isinstance(raw_data, list):
            logger.error("Raw data is not a list.")
            return False
        if raw_data and not isinstance(raw_data[0], dict):
            logger.error("Raw data items are not dicts.")
            return False
        return True

    def normalize(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map raw Greenhouse job records to the canonical JobContract shape.

        Every field that the source does not provide is set to None.
        No values are fabricated.
        """
        normalized: List[Dict[str, Any]] = []
        skipped = 0

        for raw_job in raw_data:
            try:
                norm = self._normalize_record(raw_job)
                normalized.append(norm)
            except Exception as exc:
                skipped += 1
                logger.warning(
                    "Failed to normalize job %s: %s",
                    raw_job.get("id", "unknown"),
                    exc,
                )

        if skipped:
            logger.warning("Skipped %d records during normalization.", skipped)

        logger.info("Normalized %d records.", len(normalized))
        return normalized

    def persist(self, normalized_data: List[Dict[str, Any]]) -> None:
        """Persistence is handled by the pipeline orchestrator."""
        pass

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_board(
        self, client: httpx.Client, board: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Fetch all jobs from a single board, with retry logic."""
        url = f"{self.api_url}{board}/jobs?content=true"
        stats = {"board": board, "records": 0, "status": "ok", "error": None}

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Fetching board '%s' — attempt %d/%d  URL: %s",
                    board,
                    attempt,
                    self.max_retries,
                    url,
                )
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                jobs = data.get("jobs", [])

                # Stamp provenance metadata
                ingested_ts = datetime.now(timezone.utc).isoformat()
                for job in jobs:
                    job["_board_source"] = board
                    job["_fetched_at"] = ingested_ts

                stats["records"] = len(jobs)
                logger.info("Board '%s': retrieved %d jobs.", board, len(jobs))
                return jobs, stats

            except httpx.HTTPStatusError as exc:
                stats["status"] = "http_error"
                stats["error"] = str(exc)
                logger.error(
                    "HTTP %s for board '%s': %s",
                    exc.response.status_code,
                    board,
                    exc,
                )
                # 404 → board does not exist; no point retrying
                if exc.response.status_code == 404:
                    logger.warning("Board '%s' not found — skipping.", board)
                    break
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

            except httpx.TimeoutException as exc:
                stats["status"] = "timeout"
                stats["error"] = str(exc)
                logger.warning("Timeout on board '%s', attempt %d.", board, attempt)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

            except httpx.RequestError as exc:
                stats["status"] = "connection_error"
                stats["error"] = str(exc)
                logger.error("Connection error for board '%s': %s", board, exc)
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

            except Exception as exc:
                stats["status"] = "unexpected_error"
                stats["error"] = str(exc)
                logger.error(
                    "Unexpected error fetching board '%s': %s", board, exc
                )
                break

        return [], stats

    def _normalize_record(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Map a single raw Greenhouse job to the canonical schema."""
        board = raw_job.get("_board_source", "unknown")
        source_job_id = str(raw_job.get("id", ""))

        # --- Location ---
        location_obj = raw_job.get("location") or {}
        location_raw = location_obj.get("name") or ""
        country, region, city, location, detection_method, confidence = normalize_location(
            raw_location_string=location_raw
        )

        # --- Department ---
        departments = raw_job.get("departments") or []
        department_name: Optional[str] = None
        if departments and isinstance(departments[0], dict):
            department_name = departments[0].get("name")

        # --- Description (HTML) ---
        content = raw_job.get("content") or ""
        description: Optional[str] = content if content else None

        # --- Dates ---
        updated_at_raw = raw_job.get("updated_at")
        updated_at: Optional[str] = updated_at_raw if updated_at_raw else None

        # --- Classification ---
        title = raw_job.get("title") or ""
        role_category, classification_method, classification_confidence = _classify_role(
            title, department_name
        )

        # --- Application URL ---
        app_url = raw_job.get("absolute_url")

        return {
            "job_id": f"gh_{board}_{source_job_id}",
            "source": "Greenhouse",
            "source_job_id": source_job_id,
            "company": board,
            "title": title,
            "description": description,
            "location_raw": location_raw or None,
            "location": location,
            "country": country,
            "region": region,
            "city": city,
            "location_detection_method": detection_method,
            "location_confidence": confidence,
            "employment_type": None,
            "department": department_name,
            "experience_min": None,
            "experience_max": None,
            "education": None,
            "salary_min": None,
            "salary_max": None,
            "skills_raw": [],    # Phase 1C: NLP skill extraction
            "role_category": role_category,
            "classification_method": classification_method,
            "classification_confidence": classification_confidence,
            "posted_at": None,
            "updated_at": updated_at,
            "application_url": app_url,
            "source_url": app_url,
            "status": "active",
            # first_seen_at / last_seen_at / ingested_at set by pipeline orchestrator
        }
