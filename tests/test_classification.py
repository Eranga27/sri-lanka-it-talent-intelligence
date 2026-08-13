import pytest
from pipelines.classification.classifier import classify_role_v2

def test_title_evidence():
    cat, method, conf = classify_role_v2("Software Engineer", "", "", [])
    assert cat == "Software Engineering"
    assert method == "keyword_match_v2"
    assert conf >= 0.7

def test_department_evidence():
    cat, method, conf = classify_role_v2("Associate", "Engineering", "", [])
    # In V2, "Engineering" dept doesn't have a direct keyword in taxonomy except maybe in title, 
    # but let's test a clear department keyword like "Data & Analytics" or "Data Platform"
    cat, method, conf = classify_role_v2("Analyst", "Data Platform", "", [])
    assert cat == "Data & Analytics"
    assert conf >= 0.5

def test_skill_evidence():
    # Only skills provided
    skills = [{"skill_category": "Cloud"}]
    cat, method, conf = classify_role_v2("", "", "", skills)
    assert cat == "Cloud & DevOps"
    # only 0.5 points -> confidence 0.3
    assert conf == 0.3

def test_conflicting_evidence():
    # Title says Software Engineer (3.0 points for SE)
    # Skills say Cloud (0.5 for Cloud), Data (0.5 for Data)
    skills = [{"skill_category": "Cloud"}, {"skill_category": "Data"}]
    cat, method, conf = classify_role_v2("Software Engineer", "", "", skills)
    assert cat == "Software Engineering"
    assert conf >= 0.75

def test_high_confidence():
    # Title: Data Engineer (3.0 for Data)
    # Dept: Business Intelligence (1.5 for Data)
    # Skills: SQL (0.5), Spark (0.5)
    skills = [{"skill_category": "Data"}, {"skill_category": "Data"}]
    cat, method, conf = classify_role_v2("Data Engineer", "Business Intelligence", "", skills)
    assert cat == "Data & Analytics"
    # Total score = 3.0 + 1.5 + 1.0 = 5.5 -> 0.95 confidence
    assert conf == 0.95

def test_unclassified():
    cat, method, conf = classify_role_v2("Random Job", "Office", "Do stuff", [])
    assert cat is None
    assert method == "unclassified"
    assert conf == 0.0
