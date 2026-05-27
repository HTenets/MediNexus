"""PII sanitization based on app.core.security."""

from app.core.security import sanitize


class PIISanitizer:
    def sanitize_text(self, text: str) -> str:
        return sanitize(text)
