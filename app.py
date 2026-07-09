"""
app.py
Main Streamlit entry point for the AI Resume Parser.

Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from extractor import extract_text
from parser import parse_resume, nlp
from matcher import match_resume_to_jd
from scorer import compute_quality_score
from summarizer import extractive_summary
from keyword_highlighter import highlight_keywords
from compare import rank_resumes
from report_generator import generate_ranking_report_pdf
from ui_helpers import get_score_tier, score_badge_html, section_header_html

st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="wide")

# ---------- Global custom styling ----------
st.markdown("""
<style>
    .block-container { padding-top: 2rem; max-width: 1150px; }

    /* Header banner */
    .app-header {
        background: linear-gradient(135deg, #D8B4E2 0%, #C084C7 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        color: #3B0764;
    }
    .app-header h1 { margin: 0; font-size: 28px; font-weight: 800; }
    .app-header p { margin: 6px 0 0 0; opacity: 0.85; font-size: 14px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        font-weight: 600;
    }

    /* Cards - white for contrast against the lilac page background */
    .card {
        background: #FFFFFF;
        border: 1px solid #E9D5F5;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    /* Buttons */
    .stDownloadButton button, .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>📄 AI Resume Parser</h1>
    <p>Upload resumes, extract candidate info, match against a job description, and rank candidates.</p>
</div>
""", unsafe_allow_html=True)

if nlp is None:
    st.error(
        "spaCy model 'en_core_web_sm' is not installed. Run this once in your terminal:\n\n"
        "`python -m spacy download en_core_web_sm`"
    )
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 📄 AI Resume Parser")
    st.caption("An NLP-powered resume screening tool")
    st.markdown("---")
    st.markdown(
        "**How it works**\n\n"
        "1. 🔍 **Single Resume Analysis** — extract candidate details from one resume\n\n"
        "2. 🎯 **Match Against JD** — compare one resume to a job description\n\n"
        "3. 🏆 **Rank Multiple Resumes** — screen and rank several candidates at once"
    )
    st.markdown("---")
    st.markdown("**Built with**")
    st.caption("Python · Streamlit · spaCy · scikit-learn · PyMuPDF")

tab1, tab2, tab3 = st.tabs(
    ["🔍 Single Resume Analysis", "🎯 Match Against Job Description", "🏆 Rank Multiple Resumes"]
)

# ---------- TAB 1: Single Resume Analysis ----------
with tab1:
    st.markdown(section_header_html("🔍", "Upload a resume to extract candidate details"), unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], key="single")

    if uploaded:
        raw_text = extract_text(uploaded)
        data = parse_resume(raw_text)
        quality = compute_quality_score(data)
        tier = get_score_tier(quality["total_score"])

        col1, col2 = st.columns([1.3, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
                <p style="margin:4px 0;"><b>Name:</b> {data['name']}</p>
                <p style="margin:4px 0;"><b>Email:</b> {data['email']}</p>
                <p style="margin:4px 0;"><b>Phone:</b> {data['phone']}</p>
                <p style="margin:4px 0;"><b>Skills found:</b> {', '.join(data['skills']) or 'None detected'}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=quality["total_score"],
                title={"text": "Resume Quality Score"},
                number={"suffix": "", "font": {"color": tier["color"]}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": tier["color"]},
                    "steps": [
                        {"range": [0, 50], "color": "#FEE2E2"},
                        {"range": [50, 70], "color": "#FEF3C7"},
                        {"range": [70, 100], "color": "#DCFCE7"},
                    ],
                },
            ))
            fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("🎓 Education"):
            st.write(data["education"] or "Not found")
        with st.expander("💼 Experience"):
            st.write(data["experience"] or "Not found")
        with st.expander("🚀 Projects"):
            st.write(data["projects"] or "Not found")
        with st.expander("📝 AI Summary"):
            st.write(extractive_summary(data["cleaned_text"], num_sentences=3))

# ---------- TAB 2: Match Against Job Description ----------
with tab2:
    st.markdown(section_header_html("🎯", "Compare one resume against a job description"), unsafe_allow_html=True)
    uploaded_jd = st.file_uploader("Upload resume (PDF or DOCX)", type=["pdf", "docx"], key="jd_resume")
    jd_text_input = st.text_area("Paste the job description here", height=200)

    if uploaded_jd and jd_text_input.strip():
        raw_text = extract_text(uploaded_jd)
        data = parse_resume(raw_text)
        result = match_resume_to_jd(data["cleaned_text"], data["skills"], jd_text_input)

        st.markdown(
            score_badge_html(result["match_score"], "Match Score"),
            unsafe_allow_html=True,
        )

        st.markdown("### Highlighted Resume")
        html = highlight_keywords(data["cleaned_text"], result["matched_skills"], result["missing_skills"])
        st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)

# ---------- TAB 3: Rank Multiple Resumes ----------
with tab3:
    st.markdown(section_header_html("🏆", "Rank multiple candidates against a job description"), unsafe_allow_html=True)

    with st.expander("ℹ️ How are these scores calculated?"):
        st.markdown("""
**Quality Score (0–100)** — how complete and well-written the resume is, independent of any job description:
| Component | Points | Logic |
|---|---|---|
| Contact info | 20 | +10 if email found, +10 if phone found |
| Sections present | 40 | +10 each for Education, Experience, Skills, Projects being non-empty |
| Skill coverage | 20 | `min(skills found, 10) × 2` |
| Length & detail | 20 | Best score for a 300–800 word resume; penalized if too short or too long |

**Match Score (0–100)** — how well the resume fits *this specific* job description:
```
Match Score = (0.6 × skill overlap ratio) + (0.4 × TF-IDF text similarity)
```
- *Skill overlap*: % of the JD's required skills the candidate actually has
- *Text similarity*: broader contextual overlap between resume and JD wording (via TF-IDF + cosine similarity)

**Final Score (0–100)** — the ranking score, combining both:
```
Final Score = (Match Score × 0.7) + (Quality Score × 0.3)
```
Match score is weighted higher since job fit matters more than general resume polish for a hiring decision.
        """)

    uploaded_multi = st.file_uploader(
        "Upload multiple resumes", type=["pdf", "docx"], accept_multiple_files=True, key="multi"
    )
    jd_text_multi = st.text_area("Paste the job description here", height=200, key="jd_multi")

    if uploaded_multi and jd_text_multi.strip():
        candidates = [parse_resume(extract_text(f)) for f in uploaded_multi]
        ranked_df = rank_resumes(candidates, jd_text_multi)

        def _highlight_final_score(row):
            tier = get_score_tier(row["Final Score"])
            return [f"background-color: {tier['bg']}" if col == "Final Score" else "" for col in row.index]

        styled_df = ranked_df.style.apply(_highlight_final_score, axis=1).format({
            "Match Score (%)": "{:.2f}",
            "Quality Score": "{:.0f}",
            "Final Score": "{:.2f}",
        })
        st.dataframe(styled_df, use_container_width=True)

        bar_colors = [get_score_tier(s)["color"] for s in ranked_df["Final Score"]]
        fig = go.Figure(go.Bar(x=ranked_df["Name"], y=ranked_df["Final Score"], marker_color=bar_colors))
        fig.update_layout(title="Candidate Ranking", xaxis_title="Candidate", yaxis_title="Final Score")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        report_pdf = generate_ranking_report_pdf(ranked_df, jd_text_multi)
        st.download_button(
            label="📥 Download Analysis Report (PDF)",
            data=report_pdf,
            file_name=f"resume_screening_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )
