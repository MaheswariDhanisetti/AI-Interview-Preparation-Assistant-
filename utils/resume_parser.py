"""Resume parsing utilities for extracting text from PDF and DOCX files."""

import io
import PyPDF2
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file given its raw bytes."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file given its raw bytes."""
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def extract_resume_text(uploaded_file) -> str:
    """
    Extract text from an uploaded Streamlit file object.

    Supports .pdf, .docx, and .txt formats.  Returns an empty string if the
    file type is not recognised.
    """
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    # Plain-text fallback (.txt)
    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="replace")
    return ""
