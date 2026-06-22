"""Security utilities — PII detection, encryption, and sanitization."""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = {"name", "id_number", "phone", "address", "email"}

# ── Phone Patterns ────────────────────────────────────────────────────────── #
PHONE_PATTERN = re.compile(r"1[3-9]\d{9}")
LANDLINE_PATTERN = re.compile(r"0\d{2,3}-?\d{7,8}")
ID_PATTERN = re.compile(r"\b\d{17}[\dXx]\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def sanitize(text: str) -> str:
    """Sanitize PII from text by replacing sensitive data with placeholders."""
    result = EMAIL_PATTERN.sub("[邮箱]", text)
    result = ID_PATTERN.sub("[身份证号]", result)
    result = LANDLINE_PATTERN.sub("[座机号]", result)
    result = PHONE_PATTERN.sub("[手机号]", result)
    return result


def restore(text: str, original: str) -> str:
    """Restore sanitized text (stub — in production, use reversible encryption)."""
    return original


def has_pii(text: str) -> bool:
    """Check if text contains any sensitive information."""
    if PHONE_PATTERN.search(text):
        return True
    if ID_PATTERN.search(text):
        return True
    if EMAIL_PATTERN.search(text):
        return True
    return False


def mask_pii(text: str) -> str:
    """Mask PII with partial visibility (e.g., 138****5678)."""

    def _mask_phone(m: re.Match) -> str:
        num = m.group()
        return num[:3] + "****" + num[-4:]

    def _mask_id(m: re.Match) -> str:
        num = m.group()
        return num[:4] + "**********" + num[-4:]

    def _mask_email(m: re.Match) -> str:
        email = m.group()
        at_idx = email.index("@")
        local = email[:at_idx]
        domain = email[at_idx:]
        if len(local) <= 2:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return masked_local + domain

    result = EMAIL_PATTERN.sub(_mask_email, text)
    result = ID_PATTERN.sub(_mask_id, result)
    result = PHONE_PATTERN.sub(_mask_phone, result)
    return result


def detect_pii(text: str) -> list[dict[str, Any]]:
    """Return list of detected PII items with positions."""
    findings: list[dict[str, Any]] = []

    for match in PHONE_PATTERN.finditer(text):
        findings.append({"type": "phone", "value": match.group(), "pos": match.start()})
    for match in EMAIL_PATTERN.finditer(text):
        findings.append({"type": "email", "value": match.group(), "pos": match.start()})
    for match in ID_PATTERN.finditer(text):
        findings.append({"type": "id_number", "value": match.group(), "pos": match.start()})

    return findings
