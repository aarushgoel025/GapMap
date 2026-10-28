"""Privacy filtering module for resume parsing.

Before sending any resume text to external services, databases, or LLMs, all
Personally Identifiable Information (PII) including email addresses, phone
numbers, and street addresses must be redacted.
"""

import re
from typing import Pattern

# ---------------------------------------------------------------------------
# Regular Expressions for PII Detection
# ---------------------------------------------------------------------------

# Matches standard email addresses (e.g., candidate.name@domain.com)
EMAIL_PATTERN: Pattern[str] = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Matches international and domestic phone number formats:
# - +1 (555) 123-4567
# - +91 98765 43210 or +91-9876543210
# - +44 20 7946 0958
# - (555) 123-4567
# - 555-123-4567 or 555.123.4567
# - 98765 43210 (10-digit 5+5 format)
# Avoids matching simple 4-digit year ranges (e.g., 2020 - 2024) or GPA 3.8 / 4.0.
PHONE_PATTERN: Pattern[str] = re.compile(
    r"(?:"
    # Optional country code: +1, +91, +44, 001, etc.
    r"(?:(?:\+|00)\d{1,3}[\s.-]*)?"
    r"(?:"
    # Format 1: 3-part numbers: (555) 123-4567, 555-123-4567, 20 7946 0958
    r"(?:\(\d{2,5}\)|\b\d{2,5}\b)[\s.-]+\d{2,4}[\s.-]+\d{3,5}\b"
    r"|"
    # Format 2: 5+5 format commonly used in India/international: 98765 43210 or 98765-43210
    r"\b\d{5}[\s.-]+\d{5}\b"
    r"|"
    # Format 3: 7-digit local US number: 123-4567 or 123.4567 (must use - or .)
    r"\b\d{3}[-.]\d{4}\b"
    r"|"
    # Format 4: Continuous 10-11 digit numbers: 9876543210
    r"\b\d{10,11}\b"
    r")"
    r")"
)

# Matches street address patterns such as:
# - 123 Main Street, Apt 4B
# - 742 Evergreen Terrace, Suite 100
# - 1600 Pennsylvania Ave. NW
# - P.O. Box 456
STREET_ADDRESS_PATTERN: Pattern[str] = re.compile(
    r"(?:"
    # Standard street addresses: number + street name + street type suffix
    r"\b\d{1,5}\s+[A-Za-z0-9\s.,#-]+?\s+"
    r"(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|"
    r"Drive|Dr\.?|Way|Court|Ct\.?|Terrace|Ter\.?|Place|Pl\.?|Parkway|Pkwy\.?|"
    r"Highway|Hwy\.?|Circle|Cir\.?)"
    r"(?:[,\s]+(?:Apt|Suite|Ste|Unit|#|Floor|Fl|Room|Rm)\.?\s*[A-Za-z0-9#-]+)?"
    r"|"
    # P.O. Box variants
    r"\b(?:P\.?O\.?\s*Box\s+\d+)\b"
    r")",
    re.IGNORECASE,
)

# Redaction placeholder tokens
REDACTED_EMAIL: str = "[REDACTED_EMAIL]"
REDACTED_PHONE: str = "[REDACTED_PHONE]"
REDACTED_ADDRESS: str = "[REDACTED_ADDRESS]"


def scrub_pii(text: str) -> str:
    """Scrub personally identifiable information (PII) from resume text.

    Removes emails, phone numbers, and street address lines, replacing them
    with standardized redaction placeholders.

    Args:
        text: The raw resume text to be sanitized.

    Returns:
        The sanitized text with sensitive personal information redacted.
    """
    if not text:
        return ""

    sanitized = text

    # Step 1: Redact street addresses first (can contain numbers that phone patterns might touch)
    sanitized = STREET_ADDRESS_PATTERN.sub(REDACTED_ADDRESS, sanitized)

    # Step 2: Redact email addresses
    sanitized = EMAIL_PATTERN.sub(REDACTED_EMAIL, sanitized)

    # Step 3: Redact phone numbers
    sanitized = PHONE_PATTERN.sub(REDACTED_PHONE, sanitized)

    return sanitized
