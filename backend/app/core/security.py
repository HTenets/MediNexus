"""PII detection and sanitization utilities."""

SENSITIVE_FIELDS = {"name", "id_number", "phone", "address", "email"}


def sanitize(text: str) -> str:
    for field in SENSITIVE_FIELDS:
        text = text.replace(field, "[REDACTED]")
    return text


def restore(text: str, original: str) -> str:
    return original  # Stub
