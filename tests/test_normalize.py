import json
from pathlib import Path

import pytest

from app.skill_matching.normalize import normalize_name

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "app" / "skill_matching"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parents[1] / "skill_matching"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Node.js", "nodejs"),
        ("node js", "nodejs"),
        ("Node-JS", "nodejs"),
        ("  Machine Learning ", "machinelearning"),
        ("C++", "c++"),  # '+' is kept so C and C++ stay different
        ("C#", "c#"),
        ("", ""),
    ],
)
def test_normalize_name(raw: str, expected: str) -> None:
    assert normalize_name(raw) == expected


def test_normalize_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        normalize_name(None)  # type: ignore[arg-type]


def test_normalize_is_idempotent() -> None:
    assert normalize_name(normalize_name("Spring Boot")) == "springboot"


def test_data_files_use_normalized_keys() -> None:
    # Lookups compare normalized names, so every key and value must already be normalized.
    aliases = json.loads((DATA_DIR / "aliases.json").read_text())
    prereqs = json.loads((DATA_DIR / "prereqs.json").read_text())
    for alias, canonical in aliases.items():
        assert alias == normalize_name(alias), f"alias key not normalized: {alias}"
        assert canonical == normalize_name(canonical), f"alias value not normalized: {canonical}"
    for skill, needs in prereqs.items():
        assert skill == normalize_name(skill), f"prereq key not normalized: {skill}"
        assert all(p == normalize_name(p) for p in needs), f"prereq not normalized for {skill}"


def test_prereqs_have_no_self_loops() -> None:
    prereqs = json.loads((DATA_DIR / "prereqs.json").read_text())
    for skill, needs in prereqs.items():
        assert skill not in needs

