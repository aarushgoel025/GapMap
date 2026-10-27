"""Skill-name normalization shared by the matcher and the JSON lookup tables."""
import re

# Whitespace, dots and dashes are dropped so "Node.js", "node js" and "node-js" all collapse to "nodejs".
_STRIP = re.compile(r"[\s.\-]+")


def normalize_name(s: str) -> str:
    """Lowercase and remove spaces, dots and dashes. Symbols like '+' and '#' are kept so 'C++' != 'C'."""
    if not isinstance(s, str):
        raise TypeError(f"normalize_name expects a str, got {type(s).__name__}")
    return _STRIP.sub("", s.lower())

