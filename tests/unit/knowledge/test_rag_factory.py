"""Tests for the RAG factory — the retrieval stack must actually retrieve.

These guard the wiring, not the retrieval quality: the point is that a symptom
query returns grounded chunks from the bundled knowledge base through the
real fusion pipeline (BM25 → Z-score → confidence weighting).
"""

import pytest

from knowledge.factory import build_bm25, build_knowledge_graph, create_rag_query
from knowledge.rag import RAGQuery
from knowledge.source import SourceType


class TestBM25KnowledgeBase:
    def test_all_sources_indexed(self):
        bm25 = build_bm25()
        assert set(bm25.indices) == set(SourceType)
        for source, index in bm25.indices.items():
            assert index._built, f"BM25 index not built for {source}"
            assert index.N > 0

    @pytest.mark.asyncio
    async def test_query_returns_scored_chunks(self):
        bm25 = build_bm25()
        results = await bm25.search_all("发热 咳嗽", top_k_per_source=3)

        hits = [c for chunks in results.values() for c in chunks]
        assert hits, "BM25 retrieval returned nothing for a common symptom"
        assert all(c.score > 0 for c in hits)

    @pytest.mark.asyncio
    async def test_chunks_carry_confidence_weight(self):
        """Confidence weights come from the source config, per source."""
        bm25 = build_bm25()
        results = await bm25.search_all("发热", top_k_per_source=3)

        for source, chunks in results.items():
            for chunk in chunks:
                assert chunk.confidence_weight > 0
                assert chunk.source is source


class TestKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_symptom_query_returns_relations(self):
        graph = build_knowledge_graph()
        text = await graph.query("头痛")

        assert "知识图谱关联分析" in text
        assert "头痛" in text

    @pytest.mark.asyncio
    async def test_unknown_symptom_returns_empty(self):
        graph = build_knowledge_graph()
        assert await graph.query("完全没有这个症状") == ""


class TestRAGQueryWiring:
    def test_factory_returns_usable_rag_query(self):
        rag = create_rag_query()
        assert isinstance(rag, RAGQuery)
        assert rag.retriever is not None
        assert rag.retriever.bm25_fallback is not None
        assert rag.knowledge_graph is not None
        # No Qdrant in the test env, so BM25 is the intended route (not a
        # silently degraded vector route).
        assert rag.force_fallback is True

    @pytest.mark.asyncio
    async def test_query_formatted_returns_grounded_context(self):
        rag = create_rag_query()
        context = await rag.query_formatted("发热咳嗽三天", top_k=3)

        assert "知识库检索结果" in context
        assert len(context) > 100

    @pytest.mark.asyncio
    async def test_health_check_reports_bm25_available(self):
        rag = create_rag_query()
        status = await rag.health_check()

        assert status["bm25"] is True
        assert status["graph"] is True
