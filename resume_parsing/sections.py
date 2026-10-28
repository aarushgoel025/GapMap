"""Resume section splitting module.

Divides resume text into recognized standard sections (Skills, Projects,
Experience, Education, Certifications, Achievements) while handling
variations in capitalization, formatting markers, colons, and edge cases.
"""

import re
from typing import Dict, List, Optional, Tuple

# Canonical section keys
SECTION_SKILLS: str = "skills"
SECTION_PROJECTS: str = "projects"
SECTION_EXPERIENCE: str = "experience"
SECTION_EDUCATION: str = "education"
SECTION_CERTIFICATIONS: str = "certifications"
SECTION_ACHIEVEMENTS: str = "achievements"
SECTION_HEADER: str = "header"
SECTION_FULL_TEXT: str = "full_text"

# Recognized heading keywords mapped to their canonical section name
HEADING_MAP: Dict[str, str] = {
    # Skills
    "skills": SECTION_SKILLS,
    "skill": SECTION_SKILLS,
    "technical skills": SECTION_SKILLS,
    "core skills": SECTION_SKILLS,
    "key skills": SECTION_SKILLS,
    "skills & proficiencies": SECTION_SKILLS,
    "skills and proficiencies": SECTION_SKILLS,
    "technologies": SECTION_SKILLS,
    "technical proficiencies": SECTION_SKILLS,
    # Projects
    "projects": SECTION_PROJECTS,
    "project": SECTION_PROJECTS,
    "key projects": SECTION_PROJECTS,
    "personal projects": SECTION_PROJECTS,
    "academic projects": SECTION_PROJECTS,
    "notable projects": SECTION_PROJECTS,
    # Experience
    "experience": SECTION_EXPERIENCE,
    "work experience": SECTION_EXPERIENCE,
    "professional experience": SECTION_EXPERIENCE,
    "employment history": SECTION_EXPERIENCE,
    "work history": SECTION_EXPERIENCE,
    "relevant experience": SECTION_EXPERIENCE,
    "hackathons / internships": SECTION_EXPERIENCE,
    "hackathons and internships": SECTION_EXPERIENCE,
    "internships": SECTION_EXPERIENCE,
    # Education
    "education": SECTION_EDUCATION,
    "educational background": SECTION_EDUCATION,
    "academic background": SECTION_EDUCATION,
    "academic qualifications": SECTION_EDUCATION,
    "academics": SECTION_EDUCATION,
    # Certifications
    "certifications": SECTION_CERTIFICATIONS,
    "certification": SECTION_CERTIFICATIONS,
    "certificates": SECTION_CERTIFICATIONS,
    "licenses & certifications": SECTION_CERTIFICATIONS,
    "licenses and certifications": SECTION_CERTIFICATIONS,
    # Achievements
    "achievements": SECTION_ACHIEVEMENTS,
    "achievement": SECTION_ACHIEVEMENTS,
    "honors & awards": SECTION_ACHIEVEMENTS,
    "honors and awards": SECTION_ACHIEVEMENTS,
    "awards & achievements": SECTION_ACHIEVEMENTS,
    "awards and achievements": SECTION_ACHIEVEMENTS,
    "key achievements": SECTION_ACHIEVEMENTS,
}


def _clean_heading_candidate(line: str) -> str:
    """Normalize a candidate line by removing markdown symbols and trailing punctuation."""
    # Strip markdown headers (e.g. "### Skills" -> "Skills")
    cleaned = re.sub(r"^[\s#*_-]+", "", line)
    # Strip markdown bold/italic tags and trailing punctuation like ":" or " -"
    cleaned = re.sub(r"[*_:]+$", "", cleaned)
    # Remove extra spaces
    cleaned = cleaned.strip()
    return cleaned.lower()


def _is_section_heading(line: str) -> Optional[str]:
    """Check if a line matches any recognized resume section heading.

    Args:
        line: A single line of resume text.

    Returns:
        The canonical section name (e.g. 'skills') if recognized, else None.
    """
    stripped = line.strip()
    # Resume headings are typically short headers (under 60 characters)
    if not stripped or len(stripped) > 60:
        return None

    normalized = _clean_heading_candidate(stripped)
    return HEADING_MAP.get(normalized)


def split_resume_sections(text: str) -> Dict[str, str]:
    """Split resume text into recognized standard sections.

    Recognized sections:
      - skills
      - projects
      - experience
      - education
      - certifications
      - achievements

    Behavior:
      - Case-insensitive heading recognition (e.g., SKILLS, Skills, skills).
      - Strips Markdown symbols (`##`, `**`) and trailing colons (`Skills:`).
      - Captures pre-heading text (such as candidate contact info/summary) under 'header'.
      - If no recognized headings are found, returns the entire resume text under 'full_text'.
      - Handles empty or whitespace-only text gracefully by returning an empty dictionary.

    Args:
        text: The raw resume string.

    Returns:
        A dictionary mapping section names to their respective content strings.
    """
    if not text or not text.strip():
        return {}

    lines = text.splitlines()
    detected_sections: List[Tuple[str, int]] = []

    # Step 1: Scan for recognized headings and record their line index
    for idx, line in enumerate(lines):
        canonical_name = _is_section_heading(line)
        if canonical_name:
            detected_sections.append((canonical_name, idx))

    # Fallback: If no recognized headings exist, treat entire text as one section
    if not detected_sections:
        return {SECTION_FULL_TEXT: text.strip()}

    result: Dict[str, str] = {}

    # Step 2: Extract preamble / header before the first heading if present
    first_heading_line = detected_sections[0][1]
    if first_heading_line > 0:
        header_text = "\n".join(lines[:first_heading_line]).strip()
        if header_text:
            result[SECTION_HEADER] = header_text

    # Step 3: Extract the content of each recognized section
    for i, (section_name, line_idx) in enumerate(detected_sections):
        start_line = line_idx + 1
        end_line = detected_sections[i + 1][1] if i + 1 < len(detected_sections) else len(lines)

        section_body = "\n".join(lines[start_line:end_line]).strip()
        if section_body:
            if section_name in result:
                result[section_name] = f"{result[section_name]}\n\n{section_body}"
            else:
                result[section_name] = section_body

    return result
