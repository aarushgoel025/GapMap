
import json
import re
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "company"
    / "talent_check_company_skillsets.json"
)

# Maps source JSON column names to the project's category codes.
CATEGORY_COLUMN_MAP = {
    "coding": "COD",
    "data_structures_and_algorithms": "DSA",
    "object_oriented_programming_and_design": "OOD",
    "aptitude_and_problem_solving": "APTI",
    "communication_skills": "COMM",
    "ai_native_engineering": "AI",
    "devops_and_cloud": "CLOUD",
    "sql_and_design": "SQL",
    "software_engineering": "SWE",
    "system_design_and_architecture": "SYSD",
    "computer_networking": "NETW",
    "operating_system": "OS",
}


def parse_level(value) -> int:
    """Extract the numeric level from values such as '5-AP' or '4-CU'."""

    if isinstance(value, bool):
        raise ValueError(f"Invalid skill level: {value!r}")

    if isinstance(value, int):
        level = value
    elif isinstance(value, str):
        match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*.*)?", value)
        if not match:
            raise ValueError(f"Unrecognized skill level: {value!r}")
        level = int(match.group(1))
    else:
        raise ValueError(f"Invalid skill level: {value!r}")

    if not 0 <= level <= 10:
        raise ValueError(f"Skill level must be between 0 and 10: {level}")

    return level


def load_raw_companies() -> list[dict]:
    """Load original company records without changing their values."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Company data file not found: {DATA_FILE}")

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("Expected a JSON object containing a records list.")

    for record in data["records"]:
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("company"), str)
            or not record["company"].strip()
            or not isinstance(record.get("skill_levels_raw"), dict)
        ):
            raise ValueError(f"Invalid company record: {record!r}")

    return data["records"]


def load_companies() -> dict[str, dict[str, int]]:
    """
    Return {company_name: {category_code: required_level}}.

    Duplicate company records are merged using the maximum numeric
    level for each category. Original JSON records remain unchanged.
    """

    companies = {}

    for record in load_raw_companies():
        company_name = record["company"].strip()
        raw_levels = record["skill_levels_raw"]

        if company_name not in companies:
            companies[company_name] = {
                code: 0 for code in CATEGORY_COLUMN_MAP.values()
            }

        for source_column, category_code in CATEGORY_COLUMN_MAP.items():
            value = raw_levels.get(source_column)

            # Missing values do not override an existing requirement.
            if value is None or (isinstance(value, str) and not value.strip()):
                continue

            level = parse_level(value)

            companies[company_name][category_code] = max(
                companies[company_name][category_code],
                level,
            )

    return companies
