"""Tests for ReviewAgent with independent RAG verification."""

import pytest
from agents.review.agent import ReviewAgent
from app.schemas.agent import HandoverManifest


class MockRAG:
    """Mock RAGQuery for testing ReviewAgent."""

    async def query_formatted(self, text: str, top_k: int = 5, format: str = "llm_context") -> str:
        return "【知识库检索结果】\n- 感冒: 发热咳嗽常见病\n- 治疗: 对症治疗"

    async def query(self, text: str, top_k: int = 5, use_fallback: bool = False, include_graph: bool = True):
        from knowledge.source import FusionResult, RetrievedChunk, SourceType
        return FusionResult(
            chunks=[RetrievedChunk(text="感冒", source=SourceType.CLINICAL_CASES, score=0.8)],
            source_counts={"clinical_cases": 1},
            query=text,
            activated_sources=[SourceType.CLINICAL_CASES],
        )


class TestReviewAgent:
    """ReviewAgent with RAG verification."""

    def setup_method(self):
        self.agent = ReviewAgent(rag_query=MockRAG())

    @pytest.mark.asyncio
    async def test_review_with_rag(self):
        """Review should query RAG independently."""
        manifest = await self.agent.run({
            "symptoms": "fever and cough",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "感冒", "likelihood": "高"}]},
            "doctor_facts": ["诊断: 感冒"],
        })
        assert manifest is not None
        assert len(manifest.facts) > 0
        facts_text = " ".join(manifest.facts)
        assert "知识库" in facts_text
        assert "diagnosis" in facts_text.lower() or "诊断" in facts_text

    @pytest.mark.asyncio
    async def test_review_no_symptoms(self):
        """Empty symptoms should return empty review."""
        manifest = await self.agent.run({"symptoms": ""})
        assert manifest is not None
        assert len(manifest.facts) > 0

    @pytest.mark.asyncio
    async def test_review_evidence_level(self):
        """Evidence level C should trigger pending question."""
        manifest = await self.agent.run({
            "symptoms": "cough",
            "evidence_level": "C",
        })
        questions = " ".join(manifest.pending_questions)
        assert "证据等级" in questions or "建议" in questions

    @pytest.mark.asyncio
    async def test_review_risk_flags_preserved(self):
        """Risk flags from Doctor should be preserved in review."""
        manifest = await self.agent.run({
            "symptoms": "chest pain",
            "risk_flags": ["EMERGENCY_DETECTED"],
        })
        assert "EMERGENCY_DETECTED" in manifest.risk_flags

    @pytest.mark.asyncio
    async def test_review_no_rag(self):
        """Review without RAG should still return rules-based review."""
        agent = ReviewAgent()  # no rag_query
        manifest = await agent.run({
            "symptoms": "cough",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "感冒"}]},
        })
        assert manifest is not None
        assert len(manifest.facts) > 0

    @pytest.mark.asyncio
    async def test_review_single_diagnosis_flagged(self):
        """Single diagnosis should trigger a suggestion to consider differential."""
        manifest = await self.agent.run({
            "symptoms": "fever",
            "diagnosis": {"possible_diagnoses": [{"diagnosis": "感冒", "likelihood": "高"}]},
        })
        facts_text = " ".join(manifest.facts)
        assert "鉴别" in facts_text or "differential" in facts_text.lower()
