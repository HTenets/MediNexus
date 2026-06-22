"""PII sanitization — regex-based detection, masking, and sanitization."""

import re
from typing import Any


class PIISanitizer:
    """Detect and sanitize personally identifiable information."""

    # Chinese mobile: 1[3-9]\d{9}
    PHONE_PATTERN = re.compile(r"1[3-9]\d{9}")
    # Chinese landline: 0\d{2,3}-?\d{7,8}
    LANDLINE_PATTERN = re.compile(r"0\d{2,3}-?\d{7,8}")
    # Chinese ID: 18 digits (17 + check digit)
    ID_PATTERN = re.compile(r"\b\d{17}[\dXx]\b")
    # Email
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

    def sanitize_text(self, text: str) -> str:
        """Replace all PII with placeholder tags."""
        result = self.EMAIL_PATTERN.sub("[邮箱]", text)
        result = self.ID_PATTERN.sub("[身份证号]", result)
        result = self.LANDLINE_PATTERN.sub("[座机号]", result)
        result = self.PHONE_PATTERN.sub("[手机号]", result)
        return result

    def has_pii(self, text: str) -> bool:
        """Check if text contains any PII."""
        if self.PHONE_PATTERN.search(text):
            return True
        if self.LANDLINE_PATTERN.search(text):
            return True
        if self.ID_PATTERN.search(text):
            return True
        if self.EMAIL_PATTERN.search(text):
            return True
        return False

    def mask_pii(self, text: str) -> str:
        """Mask PII with partial visibility."""
        def mask_phone(m: re.Match) -> str:
            num = m.group()
            return num[:3] + "****" + num[-4:]

        def mask_id(m: re.Match) -> str:
            num = m.group()
            return num[:4] + "**********" + num[-4:]

        def mask_email(m: re.Match) -> str:
            email = m.group()
            at_idx = email.index("@")
            local = email[:at_idx]
            domain = email[at_idx:]
            if len(local) <= 2:
                masked_local = local[0] + "***"
            else:
                masked_local = local[0] + "***" + local[-1]
            return masked_local + domain

        result = self.EMAIL_PATTERN.sub(mask_email, text)
        result = self.ID_PATTERN.sub(mask_id, result)
        result = self.PHONE_PATTERN.sub(mask_phone, result)
        return result

    def detect_pii(self, text: str) -> list[dict[str, Any]]:
        """Return list of detected PII findings."""
        findings: list[dict[str, Any]] = []

        for match in self.PHONE_PATTERN.finditer(text):
            findings.append({
                "type": "phone",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
            })

        for match in self.EMAIL_PATTERN.finditer(text):
            findings.append({
                "type": "email",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
            })

        for match in self.ID_PATTERN.finditer(text):
            findings.append({
                "type": "id_number",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
            })

        return findings
