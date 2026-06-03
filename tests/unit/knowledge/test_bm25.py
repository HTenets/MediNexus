"""Tests for BM25 fallback index and search."""

import pytest
from knowledge.bm25_fallback import BM25Index, BM25Fallback
from knowledge.source import SourceType


class TestBM25Index:
    """BM25Okapi index implementation."""

    def setup_method(self):
        self.index = BM25Index()

    def test_empty_search(self):
        results = self.index.search("test")
        assert results == []

    def test_build_and_search(self):
        docs = [
            "Patient presents with fever and cough for 3 days",
            "Rash on arms, itchy, possible contact dermatitis",
            "Chest pain with sweating, suspect myocardial infarction",
        ]
        self.index.build(docs)
        results = self.index.search("fever cough", top_k=2)
        assert len(results) > 0
        assert results[0]["score"] > 0

    def test_chinese_tokenizer(self):
        index = BM25Index()
        docs = ["头痛发热", "咳嗽咳痰"]
        index.build(docs)
        results = index.search("头痛", top_k=2)
        assert len(results) >= 1

    def test_relevance_ranking(self):
        docs = [
            "Chest pain from heart disease, chest discomfort, severe chest pressure",
            "Skin rash from allergic reaction",
        ]
        self.index.build(docs)
        results = self.index.search("chest pain", top_k=3)
        assert len(results) >= 1
        # The first doc has "chest" 3 times, pain once — much more relevant than rash
        assert results[0]["score"] > 0

    def test_metadata_preserved(self):
        docs = ["Test document"]
        metas = [{"source": "test_source"}]
        self.index.build(docs, metas)
        results = self.index.search("test", top_k=1)
        assert results[0]["metadata"]["source"] == "test_source"

    def test_large_document(self):
        docs = [("word " * 1000)]  # single large document
        self.index.build(docs)
        results = self.index.search("word", top_k=1)
        assert len(results) == 1


class TestBM25Fallback:
    """BM25Fallback manager for multiple sources."""

    def setup_method(self):
        self.fallback = BM25Fallback()

    def test_index_and_search(self):
        self.fallback.index_documents(
            SourceType.CLINICAL_CASES,
            ["Fever and cough case", "Skin rash case"],
        )
        assert SourceType.CLINICAL_CASES in self.fallback.indices

    @pytest.mark.asyncio
    async def test_search_unindexed_source(self):
        results = await self.fallback.search(SourceType.MEDICAL_THEORY, "test")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_all_sources(self):
        self.fallback.index_documents(
            SourceType.CLINICAL_CASES,
            ["Clinical: fever and cough"],
            [{"source": "cases"}],
        )
        self.fallback.index_documents(
            SourceType.MEDICAL_THEORY,
            ["Theory: hypertension guidelines"],
            [{"source": "theory"}],
        )
        results = await self.fallback.search_all("fever")
        assert SourceType.CLINICAL_CASES in results
        assert SourceType.MEDICAL_THEORY in results
        assert len(results[SourceType.CLINICAL_CASES]) > 0
        # fever shouldn't match theory doc
        assert len(results[SourceType.MEDICAL_THEORY]) == 0
