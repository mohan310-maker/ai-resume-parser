"""
scorer.py
Computes an overall "resume quality" score (0-100) independent of any job
description. Judges completeness of sections, length, and skill count.
"""


def compute_quality_score(parsed_data: dict) -> dict:
    """
    Returns a dict with a total score (0-100) and a breakdown, so the UI
    can show *why* a resume scored what it scored.
    """
    breakdown = {}

    # 1) Contact info present (20 pts)
    contact_score = 0
    if parsed_data.get("email") != "Not found":
        contact_score += 10
    if parsed_data.get("phone") != "Not found":
        contact_score += 10
    breakdown["Contact Info"] = contact_score

    # 2) Core sections present (40 pts total, 10 each)
    sections_score = 0
    for field in ["education", "experience", "skills", "projects"]:
        value = parsed_data.get(field)
        has_content = value and value != "Not found" and len(value) > 0
        if has_content:
            sections_score += 10
    breakdown["Sections Present"] = sections_score

    # 3) Skill count (20 pts) — more relevant skills listed = better, capped at 10 skills
    skill_count = len(parsed_data.get("skills", []))
    skills_score = min(skill_count, 10) * 2
    breakdown["Skill Coverage"] = skills_score

    # 4) Resume length / detail (20 pts) — too short is bad, sweet spot ~300-800 words
    word_count = parsed_data.get("word_count", 0)
    if word_count < 100:
        length_score = 5
    elif word_count < 300:
        length_score = 12
    elif word_count <= 800:
        length_score = 20
    else:
        length_score = 15  # too long / unfocused
    breakdown["Length & Detail"] = length_score

    total = contact_score + sections_score + skills_score + length_score
    return {"total_score": total, "breakdown": breakdown}
