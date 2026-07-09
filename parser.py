"""
parser.py
Extracts structured candidate info (name, email, phone, education, skills,
experience, projects) from raw resume text using spaCy + regex.
"""

import re
import spacy
from utils import SKILL_KEYWORDS, EMAIL_REGEX, PHONE_REGEX, find_section_block, clean_text

# Load once at import time (loading per-call is slow).
# Run: python -m spacy download en_core_web_sm  (one-time setup)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None  # app.py will show a friendly error if this happens


def extract_name(raw_text: str) -> str:
    """
    Heuristic: the candidate's name is usually the first PERSON entity spaCy
    finds, OR simply the first non-empty line of the resume (common fallback).

    NOTE: we run spaCy on just the FIRST LINE (not the first 500 chars).
    spaCy's NER treats newlines as ordinary whitespace, not sentence
    boundaries, so on resumes with no punctuation between the name and the
    line below it (e.g. name directly followed by an email line), spaCy can
    merge them into one PERSON entity like "Arjun Mehta arjunmehta@x.com".
    Restricting to the first line prevents that merge entirely.
    """
    first_line = ""
    for line in raw_text.split("\n"):
        line = line.strip()
        if line:
            first_line = line
            break

    if not first_line:
        return "Not found"

    candidate = first_line
    if nlp:
        doc = nlp(first_line)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                candidate = ent.text.strip()
                break

    # Safety net: even a clean first line can occasionally include trailing
    # contact info if a resume template puts name + email + phone all on one
    # line (e.g. "Rohan Verma | rohan.verma@email.com | +91 99887 76655").
    # Cut the line at whichever comes first: a '|' separator, an '@', or a
    # run of 7+ digits (a phone number).
    cut_points = []
    pipe_idx = candidate.find("|")
    if pipe_idx != -1:
        cut_points.append(pipe_idx)
    comma_idx = candidate.find(",")
    if comma_idx != -1:
        cut_points.append(comma_idx)
    at_idx = candidate.find("@")
    if at_idx != -1:
        cut_points.append(at_idx)
    digit_match = re.search(r"\d{7,}", candidate)
    if digit_match:
        cut_points.append(digit_match.start())

    if cut_points:
        candidate = candidate[: min(cut_points)]

    candidate = candidate.rstrip("|,-").strip()

    return candidate if candidate else "Not found"


def extract_email(raw_text: str) -> str:
    match = EMAIL_REGEX.search(raw_text)
    return match.group(0) if match else "Not found"


def extract_phone(raw_text: str) -> str:
    """
    PHONE_REGEX over-matches on purpose (dates, pin codes, etc. can look
    phone-shaped). We validate by counting actual digits: valid phone
    numbers are 10-13 digits long.
    """
    for match in PHONE_REGEX.finditer(raw_text):
        candidate = match.group(0).strip()
        digit_count = sum(c.isdigit() for c in candidate)
        if 10 <= digit_count <= 13:
            return candidate
    return "Not found"


def extract_skills(raw_text: str) -> list:
    text_lower = raw_text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # \b word-boundary avoids false positives (e.g. "c" matching inside "Science").
        # re.escape handles skills with special regex chars like "c++" or "node.js".
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(raw_text: str) -> str:
    block = find_section_block(raw_text, "education")
    return block if block else "Not found"


def extract_experience(raw_text: str) -> str:
    block = find_section_block(raw_text, "experience")
    return block if block else "Not found"


def extract_projects(raw_text: str) -> str:
    block = find_section_block(raw_text, "projects")
    return block if block else "Not found"


def parse_resume(raw_text: str) -> dict:
    """Main entry point: returns a dict with all extracted fields."""
    cleaned = clean_text(raw_text)
    return {
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "experience": extract_experience(raw_text),
        "projects": extract_projects(raw_text),
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "word_count": len(cleaned.split()),
    }
