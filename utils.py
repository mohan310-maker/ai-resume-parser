"""
utils.py
Shared helper functions and reference data used by other modules.
"""

import re

# A starter list of common tech/soft skills. Extend this freely —
# the bigger this list, the better your skill-matching will be.
SKILL_KEYWORDS = [
    # Programming languages
    "python", "java", "c++", "c", "javascript", "typescript", "sql", "r", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala",
    # Web / frameworks
    "streamlit", "flask", "django", "react", "node.js", "fastapi", "html", "css",
    "angular", "vue", "spring boot", ".net", "express.js", "next.js",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
    "spacy", "nltk", "opencv", "matplotlib", "seaborn", "plotly",
    # PDF / NLP
    "pymupdf", "fitz", "pdfplumber", "nlp", "machine learning", "deep learning",
    "natural language processing", "computer vision",
    # Databases / tools
    "mysql", "postgresql", "mongodb", "redis", "firebase", "oracle", "git", "github",
    "gitlab", "bitbucket", "docker", "kubernetes", "linux", "aws", "azure", "gcp",
    "jenkins", "terraform", "ci/cd",
    # Testing
    "selenium", "junit", "pytest",
    # BI / data tools
    "excel", "power bi", "tableau", "looker", "qlik", "alteryx", "spss", "sas",
    "power query", "a/b testing", "statistics",
    # Product management
    "product strategy", "product roadmap", "user research", "product management",
    "agile", "scrum", "kanban", "jira", "confluence", "trello", "asana",
    # Design
    "figma", "sketch", "adobe xd", "canva", "wireframing", "prototyping", "ui/ux",
    # Marketing
    "seo", "sem", "google analytics", "content marketing", "social media marketing",
    "email marketing", "digital marketing",
    # Business / office tools
    "powerpoint", "salesforce", "sap", "quickbooks", "erp",
    # Soft / general
    "communication", "leadership", "teamwork", "problem solving", "project management",
    "critical thinking", "time management", "adaptability", "presentation",
    "negotiation", "stakeholder management", "cross-functional collaboration",
]

SECTION_HEADERS = {
    "education": [
        "education", "academic background", "academic qualification",
        "academic qualifications", "qualification", "qualifications",
        "academic details", "educational qualification", "educational details",
        "academic profile",
    ],
    "experience": [
        "experience", "work experience", "employment", "professional experience",
        "employment history", "work history", "career history",
        "internships", "internship", "internship experience", "training",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "technical proficiencies",
        "key skills", "core skills", "skill set", "other skills", "additional skills",
    ],
    "projects": [
        "projects", "academic projects", "personal projects", "key projects",
        "notable projects", "academic personal work", "academic and personal work",
    ],
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Matches phone-like digit groups (with optional +, spaces, dashes, dots,
# parentheses) of varying formats: "+91 98765 43210", "(080)-2345-6789",
# "9876543210", "+1-415-555-2671", etc. We deliberately over-match here and
# validate the digit COUNT afterwards in extract_phone() to avoid false
# positives from dates/pin-codes while still catching real numbers.
PHONE_REGEX = re.compile(r"\(?\+?\d{1,3}\)?[-.\s]?\(?\d{2,5}\)?[-.\s]?\d{2,5}[-.\s]?\d{2,5}[-.\s]?\d{0,5}")


def clean_text(text: str) -> str:
    """Collapse extra whitespace/newlines for easier regex + NLP processing."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_heading(line: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace - for heading comparison."""
    normalized = re.sub(r"[^a-z0-9\s]", " ", line.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _is_heading_match(line: str, headers: list) -> bool:
    """
    A line counts as matching one of `headers` if, once normalized, it
    CONTAINS one of the header phrases AND is short (<=6 words) - real
    section headings are short standalone lines, so the word-count cap
    prevents accidentally matching a header phrase inside a body sentence.
    """
    normalized = _normalize_heading(line)
    if not normalized or len(normalized.split()) > 6:
        return False
    return any(h in normalized for h in headers)


def find_section_block(raw_text: str, section_key: str, all_headers=SECTION_HEADERS) -> str:
    """
    Very simple section extractor: finds a heading like 'Skills' and grabs the
    text until the next known heading. Works on most single-column resumes,
    including ones that use slightly different heading names/punctuation
    (e.g. "Academic Qualification", "Academic & Personal Work").
    """
    lines = raw_text.split("\n")
    headers_flat = [h for headers in all_headers.values() for h in headers]
    target_headers = all_headers.get(section_key, [])

    start_idx = None
    for i, line in enumerate(lines):
        if _is_heading_match(line, target_headers):
            start_idx = i + 1
            break

    if start_idx is None:
        return ""

    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        if _is_heading_match(lines[j], headers_flat) and not _is_heading_match(lines[j], target_headers):
            end_idx = j
            break

    return "\n".join(lines[start_idx:end_idx]).strip()
