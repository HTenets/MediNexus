"""Tests for EmergencyDetector, PIISanitizer, IdentityVerifier."""

import pytest
from guardrails.emergency_detector import EmergencyDetector
from guardrails.pii_sanitizer import PIISanitizer
from guardrails.identity_verifier import IdentityVerifier


class TestEmergencyDetector:
    """Emergency keyword + semantic detection."""

    def setup_method(self):
        self.detector = EmergencyDetector()

    @pytest.mark.asyncio
    async def test_detect_suicide_english(self):
        is_em, detected, etype = await self.detector.check("I want to kill myself")
        assert is_em is True
        assert etype == "SUICIDE"

    @pytest.mark.asyncio
    async def test_detect_suicide_chinese(self):
        is_em, detected, etype = await self.detector.check("我想自杀")
        assert is_em is True
        assert "自杀" in detected

    @pytest.mark.asyncio
    async def test_detect_chest_pain(self):
        is_em, detected, etype = await self.detector.check("I have severe chest pain")
        assert is_em is True
        assert etype == "CARDIAC"

    @pytest.mark.asyncio
    async def test_detect_difficulty_breathing(self):
        is_em, detected, etype = await self.detector.check("difficulty breathing and choking")
        assert is_em is True
        assert etype in ("RESPIRATORY", "CARDIAC")

    @pytest.mark.asyncio
    async def test_detect_stroke(self):
        is_em, detected, etype = await self.detector.check("stroke symptoms")
        assert is_em is True

    @pytest.mark.asyncio
    async def test_detect_severe_bleeding(self):
        is_em, detected, etype = await self.detector.check("severe bleeding from wound")
        assert is_em is True
        assert etype == "HEMORRHAGE"

    @pytest.mark.asyncio
    async def test_no_emergency_routine(self):
        is_em, detected, _ = await self.detector.check("I have a mild headache for 2 days")
        assert is_em is False
        assert detected == []

    @pytest.mark.asyncio
    async def test_check_urgent(self):
        is_urg, detected = await self.detector.check_urgent("high fever for 3 days")
        assert is_urg is True
        assert any("fever" in kw for kw in detected)

    @pytest.mark.asyncio
    async def test_check_urgent_routine(self):
        is_urg, _ = await self.detector.check_urgent("mild cough")
        assert is_urg is False

    def test_get_emergency_response(self):
        resp = EmergencyDetector.get_emergency_response(["suicide"], "SUICIDE")
        assert resp["type"] == "emergency"
        assert resp["emergency_type"] == "SUICIDE"
        assert len(resp["actions"]) > 0
        assert len(resp["message"]) > 0

    @pytest.mark.asyncio
    async def test_regex_suicide_pattern(self):
        """Regex should catch '不想活' patterns."""
        is_em, detected, _ = await self.detector.check("我真的不想活了")
        assert is_em is True

    @pytest.mark.asyncio
    async def test_regex_mi_pattern(self):
        """Regex should catch '胸痛伴出汗'."""
        is_em, detected, _ = await self.detector.check("胸口闷痛，伴有出汗和恶心")
        assert is_em is True


class TestPIISanitizer:
    """PII detection and sanitization."""

    def setup_method(self):
        self.sanitizer = PIISanitizer()

    def test_detect_phone(self):
        text = "Phone number 13812345678 here"
        sanitized = self.sanitizer.sanitize_text(text)
        assert "13812345678" not in sanitized
        assert "[手机号]" in sanitized

    def test_detect_id_number(self):
        text = "ID 110101199001011234 here"
        sanitized = self.sanitizer.sanitize_text(text)
        assert "110101199001011234" not in sanitized
        assert "[身份证号]" in sanitized

    def test_detect_email(self):
        text = "Email test@example.com here"
        sanitized = self.sanitizer.sanitize_text(text)
        assert "test@example.com" not in sanitized
        assert "[邮箱]" in sanitized

    def test_detect_landline(self):
        text = "Tel 010-12345678 here"
        sanitized = self.sanitizer.sanitize_text(text)
        assert "010-12345678" not in sanitized

    def test_has_pii(self):
        assert self.sanitizer.has_pii("Phone 13812345678") is True
        assert self.sanitizer.has_pii("just a headache") is False

    def test_mask_phone(self):
        masked = self.sanitizer.mask_pii("Phone: 13812345678")
        assert "138****5678" in masked
        assert "13812345678" not in masked

    def test_mask_email(self):
        masked = self.sanitizer.mask_pii("Email: test@example.com")
        assert "@example.com" in masked
        assert "test@" not in masked

    def test_no_pii_normal_text(self):
        text = "我头痛两天了，有点发烧"
        assert self.sanitizer.sanitize_text(text) == text

    def test_detect_pii_returns_findings(self):
        findings = self.sanitizer.detect_pii("Phone 13812345678 Email test@example.com")
        assert len(findings) >= 2


class TestIdentityVerifier:
    """Identity verification guard."""

    def setup_method(self):
        self.verifier = IdentityVerifier()

    @pytest.mark.asyncio
    async def test_matching_ids(self):
        ok, reason = await self.verifier.verify("p1", "p1")
        assert ok is True
        assert reason == "ok"

    @pytest.mark.asyncio
    async def test_mismatched_ids(self):
        ok, reason = await self.verifier.verify("p1", "p2")
        assert ok is False
        assert "mismatch" in reason

    @pytest.mark.asyncio
    async def test_verify_session(self):
        ok = await self.verifier.verify_session("s1", "p1")
        assert ok is True  # Demo mode: always true
