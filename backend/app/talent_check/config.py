
# Skill categories used by the Talent Check module

CATEGORIES = {
    "COD": "Coding",
    "DSA": "Data Structures and Algorithms",
    "OOD": "Object-Oriented Design",
    "APTI": "Aptitude",
    "COMM": "Communication",
    "AI": "Artificial Intelligence",
    "CLOUD": "Cloud Computing",
    "SQL": "SQL and Databases",
    "SWE": "Software Engineering",
    "SYSD": "System Design",
    "NETW": "Networking",
    "OS": "Operating Systems",
}

# Confidence weights
CONFIDENCE_WEIGHTS = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.3,
}

# Scoring parameters
MULTI_SOURCE_BONUS = 1.2
STUFFING_PENALTY = 0.5
LEVEL_MULTIPLIER = 2.5
MAX_LEVEL = 10

# Readiness labels
READY_THRESHOLD = 80
ALMOST_READY_THRESHOLD = 60
