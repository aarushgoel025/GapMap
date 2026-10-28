"""Skill-stuffing detection module.

Identifies skills listed in a candidate's resume that lack supporting evidence
in the 'Projects' and 'Experience' sections. When a skill has zero mentions
in both sections, it is flagged as stuffed (stuffing_flag = True) and its
confidence is downgraded by one level.

Note:
This helper is standalone and uses provisional data structures until the
official backend/app/shared/schemas.py contract is provided.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Pattern

# Provisional default confidence tiers ordered from highest to lowest.
# Configurable to align with schemas.py once available.
DEFAULT_CONFIDENCE_TIERS: List[str] = ["HIGH", "MEDIUM", "LOW"]


@dataclass
class SkillEvidenceCheck:
    """Provisional representation of a skill's stuffing check and evidence counts.

    Attributes:
        name: Name of the skill.
        stuffing_flag: True if the skill has zero mentions in Projects and Experience.
        confidence: Confidence level after applying stuffing penalties.
        support_count: Total non-overlapping mentions across Projects and Experience.
        matched_sections: List of sections where mentions were identified.
    """

    name: str
    stuffing_flag: bool
    confidence: str
    support_count: int
    matched_sections: List[str] = field(default_factory=list)


def build_skill_pattern(skill_name: str) -> Pattern[str]:
    """Compile a regex pattern with strict word and symbol boundaries for a skill.

    Ensures:
      - Case-insensitive matching.
      - "Java" does not match "JavaScript".
      - "Go" does not match "Google" or "Django".
      - Skills containing symbols like "C++", "C#", and "Node.js" match accurately
        without causing regex syntax errors or boundary false-positives.

    Args:
        skill_name: The raw skill name (e.g. 'Python', 'Go', 'C++', 'Node.js').

    Returns:
        A compiled regular expression Pattern.
    """
    stripped = skill_name.strip()
    if not stripped:
        # Match nothing for empty skill names
        return re.compile(r"(?!)")

    escaped = re.escape(stripped)

    # Determine leading boundary:
    # If the skill starts with an alphanumeric char, ensure no word char precedes it.
    # If it starts with a symbol (e.g. '.NET'), ensure no word char or that same symbol precedes it.
    first_char = stripped[0]
    if first_char.isalnum():
        prefix = r"(?<!\w)"
    else:
        prefix = rf"(?<![\w{re.escape(first_char)}])"

    # Determine trailing boundary:
    # If the skill ends with an alphanumeric char, ensure no word char follows it.
    # If it ends with a symbol (e.g. 'C++', 'C#'), ensure no word char or that same symbol follows it.
    last_char = stripped[-1]
    if last_char.isalnum():
        suffix = r"(?!\w)"
    else:
        suffix = rf"(?![\w{re.escape(last_char)}])"

    return re.compile(rf"{prefix}{escaped}{suffix}", re.IGNORECASE)


def count_skill_mentions(skill_name: str, text: str) -> int:
    """Count non-overlapping occurrences of a skill in text using boundary rules.

    Args:
        skill_name: Name of the skill to search for.
        text: Text to search within (e.g., section body).

    Returns:
        The total count of valid occurrences found.
    """
    if not skill_name or not text:
        return 0

    pattern = build_skill_pattern(skill_name)
    return len(pattern.findall(text))


def lower_confidence_level(
    current_confidence: str,
    tiers: Optional[List[str]] = None,
) -> str:
    """Reduce confidence by one level without going below the minimum tier.

    Example (using DEFAULT_CONFIDENCE_TIERS):
        'HIGH'   -> 'MEDIUM'
        'MEDIUM' -> 'LOW'
        'LOW'    -> 'LOW' (bounded at minimum tier)

    Args:
        current_confidence: The current confidence tier string.
        tiers: Optional custom ordered list of tiers (highest to lowest).

    Returns:
        The updated confidence tier string.
    """
    active_tiers = tiers if tiers is not None else DEFAULT_CONFIDENCE_TIERS
    if not active_tiers:
        return current_confidence

    normalized_tiers = [t.upper() for t in active_tiers]
    curr_upper = current_confidence.strip().upper()

    if curr_upper in normalized_tiers:
        idx = normalized_tiers.index(curr_upper)
        # Advance index by 1, capped at the lowest tier index
        next_idx = min(idx + 1, len(active_tiers) - 1)
        return active_tiers[next_idx]

    # If current_confidence is unrecognized, return it unchanged
    return current_confidence


def _extract_section_text(sections: Dict[str, str], target_canonical: str) -> str:
    """Extract content for a target section handling case variations in keys.

    Handles keys like 'Projects', 'PROJECTS', 'projects', 'work experience', etc.
    """
    target = target_canonical.strip().lower()
    matching_contents: List[str] = []

    for key, content in sections.items():
        if not key or not content:
            continue
        normalized_key = key.strip().lower()
        if normalized_key == target or normalized_key.endswith(f" {target}"):
            matching_contents.append(content)

    return "\n\n".join(matching_contents)


def detect_skill_stuffing(
    skills: List[str],
    sections: Dict[str, str],
    initial_confidence: str = "HIGH",
    confidence_tiers: Optional[List[str]] = None,
) -> List[SkillEvidenceCheck]:
    """Check each skill for supporting evidence in Projects and Experience sections.

    Rules:
      - Only 'projects' and 'experience' sections are inspected for evidence.
      - Section name matching is case-insensitive ('Projects', 'PROJECTS', etc.).
      - If support_count == 0 across both sections:
          stuffing_flag = True
          confidence = lower_confidence_level(initial_confidence)
      - If support_count > 0:
          stuffing_flag = False
          confidence = initial_confidence

    Args:
        skills: List of skill names extracted or listed.
        sections: Dictionary of resume sections (e.g., from split_resume_sections).
        initial_confidence: Starting confidence before penalty (default: 'HIGH').
        confidence_tiers: Configurable list of tiers (default: ['HIGH', 'MEDIUM', 'LOW']).

    Returns:
        List of SkillEvidenceCheck instances for each skill in input order.
    """
    active_tiers = confidence_tiers if confidence_tiers is not None else DEFAULT_CONFIDENCE_TIERS

    # Retrieve projects and experience text case-insensitively
    projects_text = _extract_section_text(sections, "projects")
    experience_text = _extract_section_text(sections, "experience")

    results: List[SkillEvidenceCheck] = []

    for skill in skills:
        cleaned_skill = skill.strip()
        if not cleaned_skill:
            continue

        proj_count = count_skill_mentions(cleaned_skill, projects_text)
        exp_count = count_skill_mentions(cleaned_skill, experience_text)
        total_count = proj_count + exp_count

        matched_sections: List[str] = []
        if proj_count > 0:
            matched_sections.append("projects")
        if exp_count > 0:
            matched_sections.append("experience")

        if total_count == 0:
            # Skill is stuffed (listed but zero evidence in Projects and Experience)
            flag = True
            final_conf = lower_confidence_level(initial_confidence, active_tiers)
        else:
            # Skill has supporting evidence
            flag = False
            final_conf = initial_confidence

        results.append(
            SkillEvidenceCheck(
                name=cleaned_skill,
                stuffing_flag=flag,
                confidence=final_conf,
                support_count=total_count,
                matched_sections=matched_sections,
            )
        )

    return results
