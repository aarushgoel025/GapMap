
"""Local-only resume parser for GapMap."""

import re
from pathlib import Path
from typing import Any

from shared.docreader import read_document
from shared.schemas import ExtractionResult, Skill

from .privacy import scrub_pii
from .sections import split_resume_sections
from .stuffing import detect_skill_stuffing
from .ai_extractor import extract_resume_with_ai


SKILL_CATEGORIES = {
    "python": "COD",
    "java": "COD",
    "c++": "COD",
    "c#": "COD",
    "javascript": "COD",
    "typescript": "COD",
    "data structures": "DSA",
    "algorithms": "DSA",
    "dsa": "DSA",
    "object oriented programming": "OOD",
    "oop": "OOD",
    "aptitude": "APTI",
    "problem solving": "APTI",
    "communication": "COMM",
    "machine learning": "AI",
    "deep learning": "AI",
    "natural language processing": "AI",
    "nlp": "AI",
    "pandas": "AI",
    "numpy": "AI",
    "tensorflow": "AI",
    "pytorch": "AI",
    "aws": "CLOUD",
    "azure": "CLOUD",
    "docker": "CLOUD",
    "kubernetes": "CLOUD",
    "sql": "SQL",
    "mysql": "SQL",
    "postgresql": "SQL",
    "mongodb": "SQL",
    "html": "SWE",
    "css": "SWE",
    "react": "SWE",
    "node.js": "SWE",
    "fastapi": "SWE",
    "django": "SWE",
    "flask": "SWE",
    "git": "SWE",
    "github": "SWE",
    "testing": "SWE",
    "system design": "SYSD",
    "computer networks": "NETW",
    "networking": "NETW",
    "operating systems": "OS",
    "linux": "OS",
}


def _skill_pattern(name: str) -> re.Pattern:
    """Match a complete skill name, not a substring of another word."""
    return re.compile(
        rf"(?<!\w){re.escape(name)}(?!\w)",
        re.IGNORECASE,
    )


def _find_evidence(
    skill_name: str,
    sections: dict[str, str],
) -> tuple[str, str | None]:
    """Find a sentence or line that mentions a skill."""
    pattern = _skill_pattern(skill_name)

    for section_name in ("projects", "experience"):
        content = sections.get(section_name, "")
        for sentence in re.split(r"[\n.!?;]+", content):
            sentence = sentence.strip()
            if sentence and pattern.search(sentence):
                return sentence[:500], section_name

    for line in sections.get("skills", "").splitlines():
        line = line.strip()
        if line and pattern.search(line):
            return line[:500], "skills"

    return "", None



def _extract_extras(sections: dict[str, str]) -> dict[str, Any]:
    """Extract basic resume section content, including internship details."""
    certifications = [
        line.strip(" •\t-")
        for line in sections.get("certifications", "").splitlines()
        if line.strip(" •\t-")
    ]

    projects = [
        {
            "title": line.strip(" •\t-"),
            "description": line.strip(" •\t-"),
            "tech": [],
        }
        for line in sections.get("projects", "").splitlines()
        if line.strip(" •\t-")
    ]

    experience = []

    for line in sections.get("experience", "").splitlines():
        summary = line.strip(" •\t-")
        if not summary:
            continue

        # Skip awards and competition results; they are not work experience.
        if re.search(
            r"\b(finalist|runner[- ]up|winner|non-finalist|participated)\b",
            summary,
            re.IGNORECASE,
        ):
            continue

        role = ""
        company = ""
        duration = ""

        # Split the description from the role/company part at a dash.
        parts = re.split(r"\s+[—–-]\s+", summary, maxsplit=1)
        heading = parts[0].strip()

        # Capture a duration only when one is explicitly written.
        duration_match = re.search(
            r"\b(?:\d+\s*(?:months?|weeks?|years?)|"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\.?\s+\d{4}\s*[-–]\s*(?:present|\w+\.?\s+\d{4}))\b",
            heading,
            re.IGNORECASE,
        )
        if duration_match:
            duration = duration_match.group(0)

        # Recognize common internship and engineering role descriptions.
        role_match = re.search(
            r"\b((?:summer\s+)?intern(?:ship)?|"
            r"software engineer|software engineering intern|"
            r"data analytics intern|IT support(?: desk)?|"
            r"backend engineer|backend developer|"
            r"data analyst)\b",
            heading,
            re.IGNORECASE,
        )
        if role_match:
            role = role_match.group(0).strip()

        # Extract a company description following "at".
        company_match = re.search(
            r"\bat\s+(.+)$",
            heading,
            re.IGNORECASE,
        )
        if company_match:
            company = company_match.group(1).strip(" ,.")

        # For descriptions like "Summer intern, backend team at ...",
        # include the team in the role when appropriate.
        if role and re.search(r"\bteam\b", heading, re.IGNORECASE):
            team_match = re.search(
                r",\s*([^,]+team)\s+at\b",
                heading,
                re.IGNORECASE,
            )
            if team_match:
                role = f"{role}, {team_match.group(1).strip()}"

        experience.append(
            {
                "company": company,
                "role": role,
                "duration": duration,
                "summary": summary,
            }
        )

    return {
        "education": sections.get("education", "").strip(),
        "projects": projects,
        "experience": experience,
        "certifications": certifications,
    }

def parse_resume(path: str | Path) -> ExtractionResult:
    """Parse a PDF or DOCX resume into GapMap's ExtractionResult schema."""
    resume_path = Path(path)

    if not resume_path.is_file():
        raise FileNotFoundError(f"Resume file not found: {resume_path.name}")

    raw_text = read_document(resume_path)

    if not raw_text or not raw_text.strip():
        raise ValueError("The resume contains no readable text.")

    # Redact personal information before processing resume content.
    safe_text = scrub_pii(raw_text)
    sections = split_resume_sections(safe_text)

    try:
        ai_result = extract_resume_with_ai(
            resume_text=safe_text,
            source_file=resume_path.name,
            provider="gemini",
        )
        if ai_result.skills:
            return ai_result
    except Exception as exc:
        print(f"Gemini extraction failed; using rule-based parser: {exc}")

    combined_text = "\n".join(sections.values()) or safe_text

    skill_names = [
        name
        for name in SKILL_CATEGORIES
        if _skill_pattern(name).search(combined_text)
    ]

    # The stuffing detector checks whether skills are supported by
    # project or experience evidence.
    checks = detect_skill_stuffing(
        skills=skill_names,
        sections=sections,
        initial_confidence="HIGH",
    )

    stuffing_results = {
        result.name.casefold(): result
        for result in checks
    }

    skills = []

    for name in skill_names:
        evidence, evidence_section = _find_evidence(name, sections)
        check = stuffing_results.get(name.casefold())

        confidence = str(
            getattr(check, "confidence", "MEDIUM") or "MEDIUM"
        ).lower()

        if confidence not in {"high", "medium", "low"}:
            confidence = "medium"

        skills.append(
            Skill(
                skill_name=name,
                category_code=SKILL_CATEGORIES[name],
                evidence=evidence,
                confidence=confidence,
                level_estimate=None,
                source_section=evidence_section or "skills",
                verified_by=["resume"],
                stuffing_flag=bool(
                    getattr(check, "stuffing_flag", False)
                ),
            )
        )

    return ExtractionResult(
        source_type="resume",
        source_file=resume_path.name,
        skills=skills,
        extras=_extract_extras(sections),
    )
