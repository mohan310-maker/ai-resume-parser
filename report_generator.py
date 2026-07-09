"""
report_generator.py
Builds a downloadable PDF report summarizing a multi-resume ranking run
(job description used + the ranked candidate table). Used by the
"Rank Multiple Resumes" tab's Download Analysis Report button.
"""

import io
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _build_recommendation(top_candidate: pd.Series) -> str:
    """
    Turns the top-ranked candidate's scores into a plain-language
    recommendation sentence, with the assessment language scaled to how
    strong the match actually is (rather than always sounding equally
    positive regardless of whether that top score is actually good).
    """
    name = top_candidate["Name"]
    final_score = top_candidate["Final Score"]

    if final_score >= 70:
        assessment = (
            "demonstrates strong alignment with the required technical skills "
            "and should be shortlisted for the next recruitment stage."
        )
    elif final_score >= 50:
        assessment = (
            "demonstrates reasonable alignment with the job requirements. "
            "Consider a further screening call to confirm fit before shortlisting."
        )
    else:
        assessment = (
            "shows only limited alignment with the core requirements of this role. "
            "None of the evaluated candidates are a strong match — consider broadening "
            "the candidate pool or revisiting the job description's required skills."
        )

    return (
        f"Recommendation: {name} is the best match for the job description with a "
        f"Final Score of {final_score}. The candidate {assessment}"
    )


def generate_ranking_report_pdf(ranked_df: pd.DataFrame, jd_text: str) -> bytes:
    """
    Builds a PDF report from the ranked candidates DataFrame (as produced by
    compare.rank_resumes) and the job description text used to rank them.
    Returns the PDF as raw bytes, ready for st.download_button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter),
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=4)
    meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, textColor=colors.grey, spaceAfter=14)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, leading=13)
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.5, leading=11)

    story = []

    # --- Header ---
    story.append(Paragraph("Resume Screening — Analysis Report", title_style))
    generated_on = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {generated_on} · {len(ranked_df)} candidate(s) evaluated", meta_style))

    # --- Job description used ---
    story.append(Paragraph("Job Description", heading_style))
    jd_display = jd_text.strip().replace("\n", "<br/>")
    if len(jd_display) > 1200:
        jd_display = jd_display[:1200] + "…"
    story.append(Paragraph(jd_display, body_style))
    story.append(Spacer(1, 12))

    # --- Summary / recommendation ---
    top_candidate = ranked_df.iloc[0]
    avg_match = round(ranked_df["Match Score (%)"].mean(), 2)
    story.append(Paragraph("Summary & Recommendation", heading_style))
    story.append(Paragraph(_build_recommendation(top_candidate), body_style))
    story.append(Paragraph(
        f"Average match score across all {len(ranked_df)} evaluated candidate(s): {avg_match}%",
        body_style,
    ))
    story.append(Spacer(1, 14))

    # --- Ranking table ---
    story.append(Paragraph("Candidate Rankings", heading_style))

    header = ["Rank", "Name", "Email", "Match %", "Quality", "Final", "Matched Skills", "Missing Skills"]
    table_data = [header]
    for rank, row in ranked_df.iterrows():
        table_data.append([
            str(rank),
            Paragraph(str(row["Name"]), cell_style),
            Paragraph(str(row["Email"]), cell_style),
            str(row["Match Score (%)"]),
            str(row["Quality Score"]),
            str(row["Final Score"]),
            Paragraph(str(row["Matched Skills"]), cell_style),
            Paragraph(str(row["Missing Skills"]), cell_style),
        ])

    col_widths = [
        0.35 * inch, 1.0 * inch, 2.15 * inch, 0.55 * inch, 0.55 * inch,
        0.5 * inch, 2.325 * inch, 2.325 * inch,
    ]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (5, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
