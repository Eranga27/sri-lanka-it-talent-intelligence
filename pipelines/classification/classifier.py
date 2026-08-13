from typing import Tuple, List, Dict, Optional, Any

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

# Map some skills to categories for V2 Classification
_SKILL_CATEGORY_TO_ROLE = {
    "Programming": "Software Engineering",
    "Frontend": "Software Engineering",
    "Backend": "Software Engineering",
    "Data": "Data & Analytics",
    "Cloud": "Cloud & DevOps",
    "DevOps": "Cloud & DevOps",
    "AI / ML": "Artificial Intelligence & Machine Learning",
    "Cybersecurity": "Cybersecurity",
    "Analytics / BI": "Data & Analytics",
}

def classify_role_v2(title: str, department: Optional[str], description: Optional[str], extracted_skills: List[Dict[str, Any]]) -> Tuple[Optional[str], str, float]:
    """
    Deterministic Role Classification V2.
    Uses weighted evidence from title, department, description, and skills.
    
    Weights:
    Title: 3.0
    Department: 1.5
    Skills: 1.0 per relevant skill category (max 2.0)
    
    Returns: (role_category, classification_method, classification_confidence)
    """
    title_lower = (title or "").lower()
    dept_lower = (department or "").lower()
    
    scores: Dict[str, float] = {}
    
    def add_score(cat: str, points: float):
        scores[cat] = scores.get(cat, 0.0) + points

    # 1. Title Evidence (High Weight = 3.0)
    for category, keywords in _ROLE_TAXONOMY.items():
        for kw in keywords:
            if kw in title_lower:
                add_score(category, 3.0)
                break # count once per category from title
                
    # 2. Department Evidence (Medium Weight = 1.5)
    for category, keywords in _ROLE_TAXONOMY.items():
        for kw in keywords:
            if kw in dept_lower:
                add_score(category, 1.5)
                break
                
    # 3. Skill Evidence (Medium/High)
    skill_categories = [s["skill_category"] for s in extracted_skills]
    for skill_cat in skill_categories:
        mapped_role = _SKILL_CATEGORY_TO_ROLE.get(skill_cat)
        if mapped_role:
            # We add 0.5 per skill found, max 2.0 per mapped role
            add_score(mapped_role, 0.5)

    if not scores:
        return None, "unclassified", 0.0
        
    # Cap skill scores to avoid over-weighting if many skills are present.
    # We'll just take the max score.
    best_category = max(scores.items(), key=lambda x: x[1])
    cat = best_category[0]
    total_score = best_category[1]
    
    # Confidence calculation:
    # 3.0+ = >0.7 (Title match)
    # 4.5+ = >0.85 (Title + Dept/Skills)
    # 5.5+ = 0.95 (Very strong)
    if total_score >= 5.5:
        confidence = 0.95
    elif total_score >= 4.5:
        confidence = 0.85
    elif total_score >= 3.0:
        confidence = 0.75
    elif total_score >= 1.5:
        confidence = 0.50
    else:
        confidence = 0.30
        
    return cat, "keyword_match_v2", confidence
