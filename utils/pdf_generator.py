"""ATS-friendly PDF resume generator using ReportLab."""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── color palette ───────────────────────────────────────────────────────────
HEADING_COLOR = colors.HexColor("#1a3c5e")   # dark navy
SECTION_COLOR = colors.HexColor("#2e6da4")   # medium blue
BODY_COLOR = colors.HexColor("#333333")      # near-black


def _build_styles() -> dict:
    """Return a dictionary of custom ParagraphStyles."""
    base = getSampleStyleSheet()

    styles = {
        "name": ParagraphStyle(
            "CandidateName",
            parent=base["Normal"],
            fontSize=20,
            textColor=HEADING_COLOR,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=base["Normal"],
            fontSize=9,
            textColor=BODY_COLOR,
            spaceAfter=8,
            alignment=TA_CENTER,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Normal"],
            fontSize=11,
            textColor=SECTION_COLOR,
            spaceBefore=10,
            spaceAfter=2,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=9,
            textColor=BODY_COLOR,
            spaceAfter=3,
            leading=13,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=9,
            textColor=BODY_COLOR,
            spaceAfter=2,
            leading=13,
            leftIndent=12,
            bulletIndent=0,
        ),
    }
    return styles


_SECTION_KEYWORDS = {
    "summary", "objective", "profile",
    "skills", "technical skills", "core competencies",
    "experience", "work experience", "employment", "professional experience",
    "education", "academic background",
    "projects", "key projects",
    "certifications", "certificates", "achievements", "awards",
    "languages", "interests", "volunteer",
}


def _is_section_heading(line: str) -> bool:
    """Heuristic: a line is a section heading if it matches known keywords."""
    stripped = line.strip().rstrip(":").lower()
    return stripped in _SECTION_KEYWORDS


def generate_pdf(resume_text: str, candidate_name: str = "") -> bytes:
    """
    Convert plain-text resume content into an ATS-friendly PDF.

    Parameters
    ----------
    resume_text : str
        The plain-text resume (e.g. output from ``gemini_helper.generate_ats_resume``).
    candidate_name : str
        Optional candidate name to display as the document title.

    Returns
    -------
    bytes
        Raw PDF bytes ready for download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"{candidate_name} – Resume" if candidate_name else "Resume",
        author=candidate_name or "Candidate",
        subject="ATS-Optimised Resume",
    )

    styles = _build_styles()
    story = []

    # ── name / title block ────────────────────────────────────────────────
    if candidate_name:
        story.append(Paragraph(candidate_name, styles["name"]))
        story.append(
            HRFlowable(
                width="100%", thickness=1.5, color=HEADING_COLOR, spaceAfter=4
            )
        )

    # ── parse resume text into flowables ─────────────────────────────────
    lines = resume_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            story.append(Spacer(1, 4))
            i += 1
            continue

        if _is_section_heading(stripped):
            story.append(Spacer(1, 6))
            story.append(
                Paragraph(stripped.upper(), styles["section_heading"])
            )
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=SECTION_COLOR,
                    spaceAfter=2,
                )
            )
            i += 1
            continue

        # Bullet lines (starting with -, *, •, or numbers like "1.")
        if stripped and stripped[0] in ("-", "*", "•"):
            bullet_text = stripped.lstrip("-*• ").strip()
            # Escape any raw ampersands / angle brackets for ReportLab XML
            bullet_text = (
                bullet_text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            story.append(
                Paragraph(f"• {bullet_text}", styles["bullet"])
            )
            i += 1
            continue

        # Regular body line
        safe = (
            stripped
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        story.append(Paragraph(safe, styles["body"]))
        i += 1

    doc.build(story)
    return buffer.getvalue()
