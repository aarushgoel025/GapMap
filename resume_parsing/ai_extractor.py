
"""AI-assisted resume extraction using the shared LLM helper.

This module does not call any model unless extract_resume_with_ai()
is explicitly called.
"""

from shared.llm import call_structured, get_gemini, get_mistral
from shared.schemas import ExtractionResult


def build_resume_prompt(resume_text: str, source_file: str) -> str:
    """Build a privacy-conscious prompt for structured resume extraction."""
    return f"""
Extract structured information from the resume text below.

Rules:
- Extract only information explicitly supported by the resume.
- Do not invent skills, projects, education, employers, or experience.
- For each skill, provide a short exact evidence quote from the resume.
- Set source_section to the relevant section, such as Skills, Projects,
  Experience, Education, or Certifications.
- Use only valid category codes from the schema.
- Set confidence to high, medium, or low.
- Set level_estimate from 1 to 10 only when evidence supports an estimate.
- Set stuffing_flag to true only when a skill is listed without meaningful
  supporting evidence elsewhere in the resume.
- Put education, projects, experience, and certifications in the extras
  dictionary. Use empty values or lists when information is missing.
- Set source_type to "resume" and source_file to the provided filename.
- Do not include personal contact information in the output.

Source filename: {source_file}

Resume text:
---
{resume_text}
---
"""


def extract_resume_with_ai(
    resume_text: str,
    source_file: str,
    provider: str = "gemini",
) -> ExtractionResult:
    """Extract a resume with the selected provider.

    Calling this function makes a live model request.
    Pass already-scrubbed resume text to avoid sending contact details.
    """
    prompt = build_resume_prompt(resume_text, source_file)

    if provider == "gemini":
        model = get_gemini()
    elif provider == "mistral":
        model = get_mistral()
    else:
        raise ValueError("provider must be 'gemini' or 'mistral'")

    return call_structured(
        model=model,
        prompt=prompt,
        schema=ExtractionResult,
    )
