"""Configuration parameters for the Skill Matching module."""
from pathlib import Path

# Base directories
MODULE_DIR = Path(__file__).resolve().parent

# Locate backend/data dynamically
DATA_DIR = None
for candidate in [
    MODULE_DIR.parent.parent / "data",       # from backend/app/skill_matching -> backend/data
    MODULE_DIR.parent / "backend" / "data",  # from skill_matching -> backend/data
    MODULE_DIR.parent / "data",
]:
    if candidate.exists():
        DATA_DIR = candidate
        break

if DATA_DIR is None:
    DATA_DIR = MODULE_DIR.parent.parent / "data"

CACHE_DIR = DATA_DIR / "cache"

# Lookup table paths
ALIASES_PATH = MODULE_DIR / "aliases.json"
if not ALIASES_PATH.exists():
    for alt in [
        MODULE_DIR.parent / "backend" / "app" / "skill_matching" / "aliases.json",
        MODULE_DIR.parent / "skill_matching" / "aliases.json",
    ]:
        if alt.exists():
            ALIASES_PATH = alt
            break

PREREQS_PATH = MODULE_DIR / "prereqs.json"
if not PREREQS_PATH.exists():
    for alt in [
        MODULE_DIR.parent / "backend" / "app" / "skill_matching" / "prereqs.json",
        MODULE_DIR.parent / "skill_matching" / "prereqs.json",
    ]:
        if alt.exists():
            PREREQS_PATH = alt
            break

# Matching credits & thresholds
EXACT_CREDIT: float = 1.0
ALIAS_CREDIT: float = 0.9
SEMANTIC_MULTIPLIER: float = 0.8
SEMANTIC_THRESHOLD: float = 0.75

# Scoring weights
WEIGHT_MUST_HAVE: float = 2.0
WEIGHT_NICE_TO_HAVE: float = 1.0
WEIGHT_UNKNOWN: float = 1.0
MISSING_THRESHOLD: float = 0.5
