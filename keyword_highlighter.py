"""
keyword_highlighter.py
Wraps matched/missing keywords in HTML <mark> tags so Streamlit can render
them in color via st.markdown(..., unsafe_allow_html=True).
"""

import re


def highlight_keywords(text: str, matched: list, missing: list) -> str:
    """
    Returns an HTML string:
      - matched keywords highlighted in green
      - missing keywords appended in a red "missing" list (since they don't
        appear in the resume text, they can't be highlighted in-place)
    """
    highlighted = text

    for keyword in sorted(matched, key=len, reverse=True):
        pattern = re.compile(rf"(?i)\b({re.escape(keyword)})\b")
        highlighted = pattern.sub(
            r'<mark style="background-color:#b6f2b6;">\1</mark>', highlighted
        )

    missing_html = ""
    if missing:
        chips = " ".join(
            f'<span style="background-color:#f8b6b6;padding:2px 8px;'
            f'border-radius:10px;margin:2px;display:inline-block;">{kw}</span>'
            for kw in missing
        )
        missing_html = f"<br><br><b>Missing skills:</b><br>{chips}"

    return highlighted + missing_html
