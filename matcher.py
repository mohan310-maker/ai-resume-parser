"""
matcher.py
Compares a resume against a job description:
1) Overall similarity/match score (TF-IDF + cosine similarity)
2) Which JD skill keywords are present vs missing in the resume
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import SKILL_KEYWORDS


def _skills_mentioned_in(text: str) -> set:
    """Word-boundary skill detection (avoids 'c' matching inside 'Science')."""
    text_lower = text.lower()
    found = set()
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def _tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Raw TF-IDF cosine similarity (0-1) between the two full texts."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]


def compute_match_score(resume_text: str, resume_skills: list, jd_text: str) -> float:
    """
    Returns a 0-100 match score between resume and job description.

    Pure TF-IDF similarity on full documents tends to score low even for a
    genuinely strong match (resumes and JDs are written in very different
    styles/lengths). So we blend two signals:
      - skill overlap ratio (60%): how many of the JD's required skills the
        candidate actually has - the most interpretable/explainable signal
      - TF-IDF text similarity (40%): captures broader contextual overlap
        (responsibilities, domain terms) beyond just the skill keyword list
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    jd_skills = _skills_mentioned_in(jd_text)
    if jd_skills:
        resume_skills_set = {s.lower() for s in resume_skills}
        skill_overlap_ratio = len(jd_skills & resume_skills_set) / len(jd_skills)
    else:
        # JD didn't mention any keywords from our skill list — fall back to
        # text similarity alone so the score isn't unfairly zeroed out.
        skill_overlap_ratio = None

    text_sim = _tfidf_similarity(resume_text, jd_text)

    if skill_overlap_ratio is None:
        final_score = text_sim
    else:
        final_score = (0.6 * skill_overlap_ratio) + (0.4 * text_sim)

    return round(float(final_score) * 100, 2)


def get_missing_skills(resume_skills: list, jd_text: str) -> list:
    """
    Skills mentioned in the job description but NOT found in the resume.
    Uses the same SKILL_KEYWORDS list as parser.py to stay consistent.
    """
    jd_skills = _skills_mentioned_in(jd_text)
    resume_skills_set = {s.lower() for s in resume_skills}
    missing = jd_skills - resume_skills_set
    return sorted(missing)


def get_matched_skills(resume_skills: list, jd_text: str) -> list:
    """Skills that appear in BOTH the resume and the job description."""
    jd_skills = _skills_mentioned_in(jd_text)
    resume_skills_set = {s.lower() for s in resume_skills}
    return sorted(jd_skills & resume_skills_set)


def match_resume_to_jd(resume_text: str, resume_skills: list, jd_text: str) -> dict:
    """Convenience wrapper returning all matching info in one dict."""
    return {
        "match_score": compute_match_score(resume_text, resume_skills, jd_text),
        "matched_skills": get_matched_skills(resume_skills, jd_text),
        "missing_skills": get_missing_skills(resume_skills, jd_text),
    }
