"""Gemini API helper functions for the AI Interview Preparation Assistant."""

from google import genai
from google.genai import types

_MODEL_ID = "gemini-2.0-flash"
_client: "genai.Client | None" = None


def configure_gemini(api_key: str) -> None:
    """Configure the Gemini client with the provided API key."""
    global _client
    _client = genai.Client(api_key=api_key)


def _generate(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text."""
    if _client is None:
        raise RuntimeError(
            "Gemini client is not configured. Call configure_gemini() first."
        )
    response = _client.models.generate_content(
        model=_MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4096,
        ),
    )
    return response.text


def analyze_resume(resume_text: str, job_role: str) -> str:
    """
    Analyse a resume against a target job role.

    Returns a structured report covering:
    - Key strengths
    - Identified skill gaps
    - Actionable improvement suggestions
    """
    prompt = f"""You are an expert career coach and technical recruiter.

Analyse the following resume for a candidate applying for the role of **{job_role}**.

Resume:
\"\"\"
{resume_text}
\"\"\"

Provide a detailed, structured analysis with these sections:
1. **Overall Assessment** - a brief summary of the candidate's profile.
2. **Key Strengths** - bullet points highlighting the strongest skills and experiences.
3. **Skill Gaps** - specific technical or soft skills missing for the {job_role} role.
4. **ATS Compatibility** - whether the resume uses keywords likely to pass Applicant Tracking Systems for {job_role}.
5. **Actionable Recommendations** - concrete steps the candidate should take to strengthen their profile.

Be specific and constructive."""

    return _generate(prompt)


def generate_interview_questions(
    resume_text: str,
    job_role: str,
    difficulty: str = "Medium",
    num_questions: int = 10,
) -> str:
    """
    Generate personalised interview questions based on resume and job role.

    Parameters
    ----------
    resume_text : str
        The extracted text of the candidate's resume.
    job_role : str
        The target job role / position.
    difficulty : str
        One of "Easy", "Medium", or "Hard".
    num_questions : int
        Number of questions to generate.

    Returns
    -------
    str
        Numbered list of interview questions with brief guidance notes.
    """
    prompt = f"""You are a senior technical interviewer.

Based on the resume and target role provided, generate {num_questions} personalised interview questions.

Target Role: {job_role}
Difficulty Level: {difficulty}

Resume:
\"\"\"
{resume_text}
\"\"\"

Requirements:
- Mix of technical questions specific to the skills on the resume, behavioural (STAR-format) questions, and role-specific scenario questions.
- Each question should reference details from the resume where relevant (e.g. a project or technology mentioned).
- For each question, add a short Interviewer Note explaining what the interviewer is trying to assess.
- Format each entry as:

Q<number>. <Question>
Interviewer Note: <note>

Generate exactly {num_questions} questions."""

    return _generate(prompt)


def create_preparation_plan(resume_text: str, job_role: str) -> str:
    """
    Create a personalised interview preparation plan.

    Returns a week-by-week study plan tailored to the candidate's gaps.
    """
    prompt = f"""You are an expert career coach.

Create a detailed, personalised 4-week interview preparation plan for a candidate applying for **{job_role}**.

Resume:
\"\"\"
{resume_text}
\"\"\"

The plan should:
- Be structured week-by-week (Week 1 to Week 4).
- Cover technical skill building, behavioural interview prep, company/industry research, and mock interviews.
- Suggest specific resources (online courses, documentation, practice platforms) for each gap identified.
- Be realistic and actionable, with daily time estimates.

Format each week clearly with sub-tasks and time estimates."""

    return _generate(prompt)


def evaluate_answer(question: str, answer: str, job_role: str) -> str:
    """
    Evaluate a candidate's answer to an interview question.

    Returns structured feedback with a score and improvement tips.
    """
    prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

Job Role: {job_role}

Interview Question:
"{question}"

Candidate's Answer:
"{answer}"

Provide structured feedback with:
1. Score - rate the answer out of 10.
2. What Was Good - specific positive aspects of the answer.
3. Areas for Improvement - what was missing or could be stronger.
4. Model Answer Outline - a brief outline of an ideal answer.
5. Tips - two or three actionable tips for delivering a better answer.

Be honest, constructive, and specific."""

    return _generate(prompt)


def generate_ats_resume(resume_text: str, job_role: str) -> str:
    """
    Generate ATS-optimised resume content tailored to the target job role.

    Returns a structured plain-text resume ready for PDF rendering.
    """
    prompt = f"""You are a professional resume writer specialising in ATS (Applicant Tracking System) optimisation.

Rewrite the following resume to be fully ATS-friendly and tailored for the role of **{job_role}**.

Original Resume:
\"\"\"
{resume_text}
\"\"\"

Requirements:
- Use standard section headings: Summary, Skills, Work Experience, Education, Projects, Certifications.
- Incorporate relevant keywords for {job_role} naturally throughout the resume.
- Use clear, concise bullet points beginning with strong action verbs.
- Quantify achievements wherever possible (e.g. "Improved performance by 30%").
- Remove graphics, tables, and special characters that confuse ATS parsers.
- Keep the tone professional and confident.

Return ONLY the resume content in plain text, structured with clear section headings followed by content.
Do not include any commentary or meta-text outside the resume itself."""

    return _generate(prompt)
