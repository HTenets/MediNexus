"""Tests for knowledge source definitions."""

from knowledge.source import (
    SourceType, SourceConfig, RetrievedChunk, FusionResult,
    SOURCE_CONFIGS, CLINICAL_CASES_CONFIG, MEDICAL_THEORY_CONFIG, LATEST_PAPERS_CONFIG,
)


class TestSourceConfigs:
    """Source configurations should be correctly defined."""

    def test_three_sources_registered(self):
        assert len(SOURCE_CONFIGS) == 3
        assert SourceType.CLINICAL_CASES in SOURCE_CONFIGS
        assert SourceType.MEDICAL_THEORY in SOURCE_CONFIGS
        assert SourceType.LATEST_PAPERS in SOURCE_CONFIGS

    def test_confidence_weights(self):
        assert CLINICAL_CASES_CONFIG.confidence_weight == 0.8
        assert MEDICAL_THEORY_CONFIG.confidence_weight == 0.6
        assert LATEST_PAPERS_CONFIG.confidence_weight == 0.3

    def test_hierarchical_chunk_size(self):
        """Theory source uses hierarchical (parent=768)."""
        assert MEDICAL_THEORY_CONFIG.chunk_strategy == "hierarchical"
        assert MEDICAL_THEORY_CONFIG.chunk_size == 768

    def test_semantic_chunk_size(self):
        """Cases source uses semantic."""
        assert CLINICAL_CASES_CONFIG.chunk_strategy == "semantic"

    def test_recursive_chunk_size(self):
        """Papers source uses recursive."""
        assert LATEST_PAPERS_CONFIG.chunk_strategy == "recursive"
        assert LATEST_PAPERS_CONFIG.top_k_initial == 5  # less recall for low confidence

    def test_display_names(self):
        assert CLINICAL_CASES_CONFIG.display_name == "临床病例"
        assert MEDICAL_THEORY_CONFIG.display_name == "医学理论"
        assert LATEST_PAPERS_CONFIG.display_name == "最新论文"


class TestRetrievedChunk:
    """RetrievedChunk data class."""

    def test_confidence_weight_set_automatically(self):
        chunk = RetrievedChunk(text="test", source=SourceType.CLINICAL_CASES, score=0.8)
        assert chunk.confidence_weight == 0.8

    def test_final_score_default_zero(self):
        chunk = RetrievedChunk(text="test", source=SourceType.MEDICAL_THEORY, score=0.5)
        assert chunk.final_score == 0.0

    def test_latest_papers_weight(self):
        chunk = RetrievedChunk(text="test", source=SourceType.LATEST_PAPERS, score=0.3)
        assert chunk.confidence_weight == 0.3


class TestFusionResult:
    """FusionResult data class."""

    def test_empty_initialization(self):
        result = FusionResult(chunks=[], source_counts={}, query="test",
                              activated_sources=[])
        assert result.query == "test"
        assert len(result.chunks) == 0
