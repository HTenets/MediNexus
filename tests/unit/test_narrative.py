"""Tests for patient-facing narration (real streaming, no simulated typing)."""

import pytest

from app.schemas.agent import HandoverManifest
from orchestration.narrative import render_manifest, stream_narrative


def _manifest() -> HandoverManifest:
    return HandoverManifest(
        facts=["可能是急性上呼吸道感染", "建议多饮水休息"],
        pending_questions=["发热多久了?"],
        risk_flags=[],
        evidence_level="C",
    )


class FakeStreamingLLM:
    """Minimal LLM double whose chat_stream yields known deltas."""

    def __init__(self, chunks=None):
        self.chunks = chunks or ["您好，", "根据您的描述，", "可能是感冒。"]
        self.seen_messages = None

    async def chat_stream(self, messages):
        self.seen_messages = messages
        for chunk in self.chunks:
            yield chunk


class FakeSilentLLM:
    """LLM whose stream yields nothing (provider stream failure)."""

    async def chat_stream(self, messages):
        if False:  # pragma: no cover - keeps this an async generator
            yield ""


class TestRenderManifest:
    def test_renders_facts_as_bullets(self):
        text = render_manifest(_manifest())

        assert "• 可能是急性上呼吸道感染" in text
        assert "需要进一步了解" in text
        assert "发热多久了?" in text

    def test_renders_risk_flags(self):
        manifest = HandoverManifest(facts=["须立即就医"], risk_flags=["EMERGENCY_DETECTED"])

        text = render_manifest(manifest)

        assert "注意" in text
        assert "EMERGENCY_DETECTED" in text


class TestStreamNarrative:
    @pytest.mark.asyncio
    async def test_streams_real_deltas_in_order(self):
        llm = FakeStreamingLLM()
        emitted: list[str] = []

        result = await stream_narrative(llm, _manifest(), emitted.append)

        assert emitted == ["您好，", "根据您的描述，", "可能是感冒。"]
        assert result == "您好，根据您的描述，可能是感冒。"

    @pytest.mark.asyncio
    async def test_sends_manifest_as_user_payload(self):
        llm = FakeStreamingLLM()
        await stream_narrative(llm, _manifest(), lambda _: None)

        system_msg, user_msg = llm.seen_messages
        assert system_msg["role"] == "system"
        assert "可能是急性上呼吸道感染" in user_msg["content"]

    @pytest.mark.asyncio
    async def test_empty_stream_returns_empty_string(self):
        """A dead stream must not fabricate text — caller falls back."""
        result = await stream_narrative(FakeSilentLLM(), _manifest(), lambda _: None)

        assert result == ""

    @pytest.mark.asyncio
    async def test_stream_failure_does_not_raise(self):
        class BrokenLLM:
            async def chat_stream(self, messages):
                raise RuntimeError("upstream exploded")
                yield  # pragma: no cover

        result = await stream_narrative(BrokenLLM(), _manifest(), lambda _: None)

        assert result == ""
