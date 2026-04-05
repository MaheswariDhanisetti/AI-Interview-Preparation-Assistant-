"""
AI Interview Preparation Assistant
===================================
Powered by Google Gemini API.

Features:
  1. Resume Analysis  – AI-driven strengths / skill-gap report.
  2. Interview Questions – Personalised, difficulty-tiered question bank.
  3. Preparation Plan   – Week-by-week study roadmap.
  4. Answer Evaluator   – Real-time feedback on practice answers.
  5. ATS Resume Builder – Downloadable, ATS-optimised PDF resume.
"""

import streamlit as st
import html as _html

from utils.gemini_helper import (
    analyze_resume,
    configure_gemini,
    create_preparation_plan,
    evaluate_answer,
    generate_ats_resume,
    generate_interview_questions,
)
from utils.pdf_generator import generate_pdf
from utils.resume_parser import extract_resume_text

# ── page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Preparation Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* hero gradient header */
    .hero-header {
        background: linear-gradient(135deg, #1a3c5e 0%, #2e6da4 50%, #4a90d9 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    .hero-header h1 { font-size: 2.2rem; margin-bottom: 0.4rem; }
    .hero-header p  { font-size: 1.05rem; opacity: 0.9; margin: 0; }

    /* feature cards */
    .feature-card {
        background: #f8f9fa;
        border-left: 4px solid #2e6da4;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }

    /* result boxes */
    .result-box {
        background: #f0f7ff;
        border: 1px solid #b3d4f5;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        line-height: 1.7;
    }

    /* metric pill */
    .pill {
        display: inline-block;
        background: #2e6da4;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
    }

    /* tab styling */
    div[data-testid="stTabs"] button {
        font-weight: 600;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/artificial-intelligence.png",
        width=80,
    )
    st.title("AI Interview Assistant")
    st.markdown("---")

    st.subheader("🔑 Gemini API Key")
    api_key = st.text_input(
        "Enter your Google Gemini API key",
        type="password",
        placeholder="AIza...",
        help="Get a free key at https://aistudio.google.com/app/apikey",
    )

    st.markdown("---")
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        help="Your resume is processed locally and never stored.",
    )

    st.markdown("---")
    st.subheader("🎯 Target Job Role")
    job_role = st.text_input(
        "e.g. Senior Python Developer",
        placeholder="Enter the role you are applying for",
    )

    st.markdown("---")
    st.markdown(
        """
        <small>
        ✅ Your data is only sent to the Gemini API while you use the app.<br>
        ✅ Nothing is stored on any server.
        </small>
        """,
        unsafe_allow_html=True,
    )

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <h1>🎯 AI Interview Preparation Assistant</h1>
        <p>Powered by Google Gemini • Personalised questions • ATS-optimised resumes • Real-time feedback</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── guard: require API key ────────────────────────────────────────────────────
if not api_key:
    st.info(
        "👈 **Get started** – enter your **Gemini API key** in the sidebar.  "
        "You can obtain a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).",
        icon="ℹ️",
    )
    st.stop()

configure_gemini(api_key)

# ── extract resume text (cached per file) ─────────────────────────────────────
resume_text: str = ""
if uploaded_file:
    uploaded_file.seek(0)
    resume_text = extract_resume_text(uploaded_file)

# ── guard: require resume + job role for most features ───────────────────────
def _require_inputs(label: str = "") -> bool:
    """Return True if both resume and job role are provided."""
    missing = []
    if not resume_text:
        missing.append("📄 **Upload your resume** (sidebar)")
    if not job_role:
        missing.append("🎯 **Enter the target job role** (sidebar)")
    if missing:
        st.warning(
            ("Please provide the following to use the **{}** feature:\n\n".format(label) if label else "")
            + "\n".join(f"- {m}" for m in missing)
        )
        return False
    return True


# ── tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(
    [
        "📊 Resume Analysis",
        "❓ Interview Questions",
        "📅 Preparation Plan",
        "💬 Answer Evaluator",
        "📄 ATS Resume Builder",
    ]
)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – RESUME ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.header("📊 Resume Analysis")
    st.markdown(
        "Upload your resume and target role to receive an AI-powered analysis of your "
        "**strengths**, **skill gaps**, and **ATS compatibility**."
    )

    if resume_text and job_role:
        with st.expander("📋 Extracted Resume Text", expanded=False):
            st.text_area(
                "Raw extracted text (read-only)",
                value=resume_text,
                height=200,
                disabled=True,
            )

    if st.button("🔍 Analyse Resume", key="btn_analyse", type="primary"):
        if _require_inputs("Resume Analysis"):
            with st.spinner("Analysing your resume with Gemini…"):
                analysis = analyze_resume(resume_text, job_role)
            st.markdown(
                f'<div class="result-box">{_html.escape(analysis).replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            st.success("✅ Analysis complete!")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – INTERVIEW QUESTIONS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.header("❓ Personalised Interview Questions")
    st.markdown(
        "Generate a tailored set of interview questions based on your resume and the "
        "target role – complete with interviewer notes."
    )

    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy", "Medium", "Hard"],
            value="Medium",
        )
    with col2:
        num_questions = st.slider(
            "Number of questions",
            min_value=5,
            max_value=20,
            value=10,
            step=5,
        )

    if st.button("⚡ Generate Questions", key="btn_questions", type="primary"):
        if _require_inputs("Interview Questions"):
            with st.spinner("Generating personalised questions…"):
                questions = generate_interview_questions(
                    resume_text, job_role, difficulty, num_questions
                )
            st.markdown(
                f'<div class="result-box">{_html.escape(questions).replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                label="⬇️ Download Questions (.txt)",
                data=questions,
                file_name=f"interview_questions_{job_role.replace(' ', '_')}.txt",
                mime="text/plain",
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 – PREPARATION PLAN
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.header("📅 4-Week Interview Preparation Plan")
    st.markdown(
        "Get a personalised, week-by-week study roadmap that covers technical skill "
        "building, behavioural prep, and mock interview practice."
    )

    if st.button("🗺️ Create My Plan", key="btn_plan", type="primary"):
        if _require_inputs("Preparation Plan"):
            with st.spinner("Building your personalised preparation plan…"):
                plan = create_preparation_plan(resume_text, job_role)
            st.markdown(
                f'<div class="result-box">{_html.escape(plan).replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                label="⬇️ Download Plan (.txt)",
                data=plan,
                file_name=f"prep_plan_{job_role.replace(' ', '_')}.txt",
                mime="text/plain",
            )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 – ANSWER EVALUATOR
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.header("💬 Practice Answer Evaluator")
    st.markdown(
        "Type an interview question and your practice answer to receive instant, "
        "AI-driven feedback including a score and model answer outline."
    )

    if not job_role:
        st.info("Enter the target job role in the sidebar to enable this feature.")
    else:
        practice_question = st.text_area(
            "Interview Question",
            placeholder="e.g. Tell me about a time you resolved a production incident under pressure.",
            height=100,
        )
        practice_answer = st.text_area(
            "Your Practice Answer",
            placeholder="Type your answer here…",
            height=180,
        )

        if st.button("📝 Get Feedback", key="btn_feedback", type="primary"):
            if not practice_question.strip():
                st.warning("Please enter an interview question.")
            elif not practice_answer.strip():
                st.warning("Please type your practice answer.")
            else:
                with st.spinner("Evaluating your answer…"):
                    feedback = evaluate_answer(
                        practice_question, practice_answer, job_role
                    )
                st.markdown(
                    f'<div class="result-box">{_html.escape(feedback).replace(chr(10), "<br>")}</div>',
                    unsafe_allow_html=True,
                )

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 – ATS RESUME BUILDER
# ════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.header("📄 ATS-Friendly Resume Builder")
    st.markdown(
        "Instantly rewrite your resume to be **ATS-optimised** and tailored to your "
        "target role, then download it as a clean, professional PDF."
    )

    candidate_name = st.text_input(
        "Your Full Name (for the PDF header)",
        placeholder="e.g. Jane Smith",
    )

    if st.button("✨ Generate ATS Resume", key="btn_ats", type="primary"):
        if _require_inputs("ATS Resume Builder"):
            with st.spinner("Generating ATS-optimised resume…"):
                ats_content = generate_ats_resume(resume_text, job_role)

            st.subheader("Preview")
            st.text_area(
                "ATS-optimised resume content",
                value=ats_content,
                height=400,
                disabled=False,
                key="ats_preview",
            )

            # Generate PDF
            with st.spinner("Creating downloadable PDF…"):
                pdf_bytes = generate_pdf(
                    ats_content,
                    candidate_name=candidate_name.strip(),
                )

            st.download_button(
                label="⬇️ Download ATS Resume (PDF)",
                data=pdf_bytes,
                file_name=f"ATS_Resume_{candidate_name.replace(' ', '_') or 'Candidate'}.pdf",
                mime="application/pdf",
            )
            st.success(
                "✅ ATS resume generated! Click the button above to download your PDF."
            )

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:0.85rem;'>"
    "🎯 AI Interview Preparation Assistant • Powered by Google Gemini API"
    "</p>",
    unsafe_allow_html=True,
)
