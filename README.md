# AI Resume Parser — Setup Instructions

## 1. Install dependencies
```
pip install -r requirements.txt
```
(On some systems you may need: `pip install -r requirements.txt --break-system-packages`)

## 2. Download the spaCy language model (one-time, needed for name extraction)
```
python -m spacy download en_core_web_sm
```

## 3. Run the app
```
streamlit run app.py
```

## Project structure
- `app.py` — Streamlit UI (3 tabs: single resume, JD match, multi-resume ranking)
- `extractor.py` — PDF/DOCX text extraction (PyMuPDF + python-docx)
- `parser.py` — extracts name, email, phone, education, experience, skills, projects
- `matcher.py` — TF-IDF cosine similarity match score + missing/matched skills
- `scorer.py` — resume quality score (0-100) based on completeness
- `summarizer.py` — offline extractive summary (no API key needed)
- `keyword_highlighter.py` — highlights matched/missing skills in HTML
- `compare.py` — ranks multiple resumes against a job description
- `utils.py` — shared skill keyword list + regex helpers

## What's already working
All modules have been tested end-to-end with sample data (see test output).
The core logic works. What's left for you to do (this is intentional — it's
your project, and your evaluator will likely ask you to explain the code):

1. Download the spaCy model locally (couldn't be done in this sandboxed
   environment due to network restrictions — see error notes).
2. Test with REAL resume PDFs/DOCX files (sample_resumes/ folder is empty —
   add a few of your own to test extraction quality).
3. Expand SKILL_KEYWORDS in utils.py with more skills relevant to your
   target job roles.
4. Tune the section-header detection in utils.py's find_section_block() if
   your test resumes use different headings than "Education"/"Experience"/etc.
5. Polish the Streamlit UI styling (colors, layout) to make it presentation-ready.

## Suggested timeline to July 30

| Week | Dates | Focus |
|---|---|---|
| 1 | Jul 1 – Jul 7 | Environment setup, spaCy model download, run app.py locally, collect 10-15 sample resumes + 3-4 sample JDs to test with |
| 2 | Jul 8 – Jul 14 | Debug extraction on real resumes (names/emails/phones/sections) — this is where most bugs will surface; expand SKILL_KEYWORDS list |
| 3 | Jul 15 – Jul 21 | Test matcher.py + scorer.py + compare.py with multiple resumes against a JD; verify ranking makes sense; add plotly charts to app.py (score comparison bar chart) |
| 4 | Jul 22 – Jul 26 | UI polish, error handling (empty uploads, corrupted PDFs), write your project report/documentation, prepare slides |
| 5 | Jul 27 – Jul 29 | Full dry-run demo, fix last-minute bugs, backup everything |
| — | Jul 30 | Submission day — buffer, don't code anything new |

Come back anytime if a specific module breaks on your real resumes — extraction
bugs (weird PDF layouts, multi-column resumes, etc.) are the most common issue
and usually need small regex/heuristic tweaks rather than a rewrite.
