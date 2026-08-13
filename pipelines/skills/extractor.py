import re
from typing import Dict, List, Any
from datetime import datetime, timezone

from apps.api.app.models.domain import JobSkill
from pipelines.skills.taxonomy import TAXONOMY

# Pre-compile regex patterns for efficiency
_SKILL_PATTERNS = []

for entry in TAXONOMY:
    canonical = entry["canonical_name"]
    aliases = [canonical] + entry.get("aliases", [])
    
    # Sort by length descending so longer aliases match first (e.g. "React JS" before "React")
    aliases.sort(key=len, reverse=True)
    
    for alias in aliases:
        # Escape for regex and ensure word boundaries
        escaped = re.escape(alias.lower())
        
        # Handle special cases where word boundary doesn't work well (like C++ or .NET)
        if not alias[0].isalnum():
            # E.g. .NET
            pattern = r"(?<!\w)" + escaped + r"(?!\w)"
        elif not alias[-1].isalnum():
            # E.g. C++
            pattern = r"\b" + escaped + r"(?!\w)"
        else:
            pattern = r"\b" + escaped + r"\b"
            
        _SKILL_PATTERNS.append({
            "skill_id": entry["skill_id"],
            "canonical_skill": canonical,
            "skill_category": entry["category"],
            "pattern": re.compile(pattern, re.IGNORECASE),
            "alias_str": alias
        })

# Sort ALL patterns globally by length descending so longer phrases match first
_SKILL_PATTERNS.sort(key=lambda x: len(x["alias_str"]), reverse=True)

def extract_skills_from_job(job: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Deterministically extract skills from a normalized job record.
    Returns a list of dictionaries matching JobSkill shape.
    """
    title = job.get("title") or ""
    desc = job.get("description") or ""
    dept = job.get("department") or ""
    
    text_to_search = f"{title} {dept} {desc}"
    # Remove excessive whitespace to help matching
    text_to_search = re.sub(r'\s+', ' ', text_to_search)
    
    extracted_skills = {}
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for sp in _SKILL_PATTERNS:
        # Check if we already found this canonical skill for this job
        if sp["skill_id"] in extracted_skills:
            continue
            
        match = sp["pattern"].search(text_to_search)
        if match:
            # We found a skill!
            extracted_skills[sp["skill_id"]] = {
                "job_id": job["job_id"],
                "skill_id": sp["skill_id"],
                "canonical_skill": sp["canonical_skill"],
                "raw_match": match.group(0),
                "skill_category": sp["skill_category"],
                "extraction_method": "regex_boundary_match",
                "confidence": 0.9, # High confidence for bounded exact matches
                "extracted_at": now_iso
            }
            # Remove the matched text to prevent shorter patterns from overlapping
            # We replace it with spaces so boundaries aren't messed up for surrounding text
            text_to_search = sp["pattern"].sub(" " * len(match.group(0)), text_to_search)
            
    return list(extracted_skills.values())
