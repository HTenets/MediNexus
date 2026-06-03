"""Tests for multi-source retriever with fusion."""

import pytest
from knowledge.source import (
    SourceType, RetrievedChunk, FusionResult, SOURCE_CONFIGS,
)
from knowledge.retriever import MultiSourceRetriever


class MockVectorStore:
    """Mock vector store returning predefined results."""

    def __init__(self):
        self.results = {}

    def set_results(self, collection: str, items: list[dict]):
        self.results[collection] = items

    async def search_batch(self, collections: list[str], vector: list[float],
                           limit_per_source: int = 10):
        return {c: self.results.get(c, []) for c in collections}

    async def health_check(self):
        return True


class MockEmbedder:
    """Mock embedder returning fixed vector."""

    async def __call__(self, text: str) -> list[float]:
        return [0.1] * 128


class TestMultiSourceRetriever:
    """Retriever with RRF fusion and confidence weighting."""

    def setup_method(self):
        self.vs = MockVectorStore()
        self.embedder = MockEmbedder()
        self.retriever = MultiSourceRetriever(
            vector_store=self.vs,
            embedder=self.embedder,
        )

    @pytest.mark.asyncio
    async def test_empty_results(self):
        """No results from any source should return empty FusionResult."""
        result = await self.retriever.retrieve("test query")
        assert isinstance(result, FusionResult)
        assert len(result.chunks) == 0
        assert result.activated_sources == []

    @pytest.mark.asyncio
    async def test_single_source_results(self):
        """Single source with results should work."""
        self.vs.set_results("clinical_cases", [
            {"text": "Case 1: fever and cough", "score": 0.85, "source": "clinical_cases",
             "metadata": {}},
            {"text": "Case 2: headache", "score": 0.72, "source": "clinical_cases",
             "metadata": {}},
        ])
        result = await self.retriever.retrieve("fever", top_k=5)
        assert len(result.chunks) == 2
        assert result.chunks[0].score > result.chunks[1].score  # sorted by final_score
        assert result.chunks[0].source == SourceType.CLINICAL_CASES

    @pytest.mark.asyncio
    async def test_confidence_weighting(self):
        """Higher confidence sources should get weighted higher."""
        self.vs.set_results("clinical_cases", [
            {"text": "Case: cough", "score": 0.7, "source": "clinical_cases", "metadata": {}},
        ])
        self.vs.set_results("latest_papers", [
            {"text": "Paper: cough study", "score": 0.9, "source": "latest_papers", "metadata": {}},
        ])

        result = await self.retriever.retrieve("cough", top_k=5)

        # Find which source won
        case_chunks = [c for c in result.chunks if c.source == SourceType.CLINICAL_CASES]
        paper_chunks = [c for c in result.chunks if c.source == SourceType.LATEST_PAPERS]

        if case_chunks and paper_chunks:
            # After weighting, 0.7 * 0.8 = 0.56 vs 0.9 * 0.3 = 0.27
            assert case_chunks[0].final_score > paper_chunks[0].final_score

    @pytest.mark.asyncio
    async def test_z_score_normalization(self):
        """Z-score makes scores from different sources comparable."""
        self.vs.set_results("clinical_cases", [
            {"text": "Case A", "score": 0.9, "source": "clinical_cases", "metadata": {}},
            {"text": "Case B", "score": 0.5, "source": "clinical_cases", "metadata": {}},
            {"text": "Case C", "score": 0.4, "source": "clinical_cases", "metadata": {}},
        ])
        self.vs.set_results("medical_theory", [
            {"text": "Theory X", "score": 0.8, "source": "medical_theory", "metadata": {}},
            {"text": "Theory Y", "score": 0.6, "source": "medical_theory", "metadata": {}},
        ])

        result = await self.retriever.retrieve("test", top_k=5)
        assert len(result.chunks) >= 2

        # All chunks should have non-zero z_score
        for chunk in result.chunks:
            assert chunk.z_score != 0.0 or chunk.score == 0

    @pytest.mark.asyncio
    async def test_source_counts_tracked(self):
        """FusionResult should track how many from each source."""
        self.vs.set_results("clinical_cases", [
            {"text": "C1", "score": 0.8, "source": "clinical_cases", "metadata": {}},
            {"text": "C2", "score": 0.7, "source": "clinical_cases", "metadata": {}},
        ])
        self.vs.set_results("medical_theory", [
            {"text": "T1", "score": 0.6, "source": "medical_theory", "metadata": {}},
        ])

        result = await self.retriever.retrieve("test", top_k=5)
        assert result.source_counts.get("clinical_cases", 0) == 2
        assert result.source_counts.get("medical_theory", 0) == 1

    @pytest.mark.asyncio
    async def test_activated_sources(self):
        """Only sources with results should be in activated_sources."""
        self.vs.set_results("clinical_cases", [
            {"text": "C1", "score": 0.8, "source": "clinical_cases", "metadata": {}},
        ])
        result = await self.retriever.retrieve("test", top_k=5)
        assert SourceType.CLINICAL_CASES in result.activated_sources
        assert SourceType.LATEST_PAPERS not in result.activated_sources

    @pytest.mark.asyncio
    async def test_bm25_fallback_route(self):
        """BM25 fallback should be used when use_fallback=True."""
        from knowledge.bm25_fallback import BM25Fallback
        bm25 = BM25Fallback()
        bm25.index_documents(SourceType.CLINICAL_CASES,
                              ["fever and cough clinical case"],
                              [{"source": "cases"}])

        retriever = MultiSourceRetriever(
            vector_store=self.vs,
            bm25_fallback=bm25,
            embedder=self.embedder,
        )
        result = await retriever.retrieve("fever", use_fallback=True)
        assert len(result.chunks) > 0
