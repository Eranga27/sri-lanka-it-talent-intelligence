import pytest
from pipelines.skills.extractor import extract_skills_from_job

def test_extract_exact_match():
    job = {"job_id": "1", "title": "Software Engineer", "description": "Looking for someone with Python and React skills."}
    skills = extract_skills_from_job(job)
    skill_names = {s["canonical_skill"] for s in skills}
    assert "Python" in skill_names
    assert "React" in skill_names

def test_extract_aliases():
    job = {"job_id": "1", "description": "Experience with React JS, golang, and AWS cloud."}
    skills = extract_skills_from_job(job)
    skill_names = {s["canonical_skill"] for s in skills}
    assert "React" in skill_names
    assert "Go" in skill_names
    assert "AWS" in skill_names

def test_extract_word_boundaries():
    job = {"job_id": "1", "description": "Good going, we love Google."}
    skills = extract_skills_from_job(job)
    skill_names = {s["canonical_skill"] for s in skills}
    assert "Go" not in skill_names

def test_extract_case_normalization():
    job = {"job_id": "1", "description": "We need pYThon and jAvA"}
    skills = extract_skills_from_job(job)
    skill_names = {s["canonical_skill"] for s in skills}
    assert "Python" in skill_names
    assert "Java" in skill_names

def test_extract_csharp_cpp_dotnet():
    job = {"job_id": "1", "description": "Experience in C++, C#, and .NET core"}
    skills = extract_skills_from_job(job)
    skill_names = {s["canonical_skill"] for s in skills}
    assert "C++" in skill_names
    assert "C#" in skill_names
    assert ".NET" in skill_names

def test_extract_empty_job():
    job = {"job_id": "1"}
    skills = extract_skills_from_job(job)
    assert len(skills) == 0

def test_extract_multiple_skills_deduplication():
    # It should only return a skill once even if multiple aliases match
    job = {"job_id": "1", "description": "NodeJS developer needed for node development in node.js"}
    skills = extract_skills_from_job(job)
    assert len(skills) == 1
    assert skills[0]["canonical_skill"] == "Node.js"
