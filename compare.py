"""
compare.py
Ranks multiple candidates against one job description by combining
match score (JD relevance) and quality score (resume completeness)
into a single weighted final score.
"""

import pandas as pd
from matcher import match_resume_to_jd
from scorer import compute_quality_score

# Tune these weights based on what your evaluator/HR use case cares about more.
MATCH_WEIGHT = 0.7
QUALITY_WEIGHT = 0.3


def rank_resumes(candidates: list, jd_text: str) -> pd.DataFrame:
    """
    candidates: list of parsed_data dicts (output of parser.parse_resume)
    jd_text: the job description text to compare against

    Returns a DataFrame sorted by final_score, descending.
    """
    rows = []
    for candidate in candidates:
        match_info = match_resume_to_jd(
            candidate["cleaned_text"], candidate["skills"], jd_text
        )
        quality_info = compute_quality_score(candidate)

        final_score = round(
            match_info["match_score"] * MATCH_WEIGHT
            + quality_info["total_score"] * QUALITY_WEIGHT,
            2,
        )

        rows.append({
            "Name": candidate["name"],
            "Email": candidate["email"],
            "Match Score (%)": match_info["match_score"],
            "Quality Score": quality_info["total_score"],
            "Final Score": final_score,
            "Matched Skills": ", ".join(match_info["matched_skills"]) or "None",
            "Missing Skills": ", ".join(match_info["missing_skills"]) or "None",
        })

    df = pd.DataFrame(rows).sort_values("Final Score", ascending=False).reset_index(drop=True)
    df.index += 1  # rank starts at 1, not 0
    df.index.name = "Rank"
    return df
