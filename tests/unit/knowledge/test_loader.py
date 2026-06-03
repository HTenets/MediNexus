"""Tests for document loader."""

from knowledge.loader import DocumentLoader, SEED_CLINICAL_CASES, SEED_MEDICAL_THEORY, SEED_PAPER_ABSTRACTS
from knowledge.source import SourceType


class TestSeedData:
    """Seed data should be correctly formatted."""

    def test_seed_cases_exist(self):
        assert len(SEED_CLINICAL_CASES) > 0
        for case in SEED_CLINICAL_CASES:
            assert "text" in case
            assert "metadata" in case
            assert len(case["text"]) > 0

    def test_seed_theory_exist(self):
        assert len(SEED_MEDICAL_THEORY) > 0
        for theory in SEED_MEDICAL_THEORY:
            assert "text" in theory
            assert "metadata" in theory
            assert "evidence" in theory["metadata"]

    def test_seed_papers_exist(self):
        assert len(SEED_PAPER_ABSTRACTS) > 0
        for paper in SEED_PAPER_ABSTRACTS:
            assert "text" in paper
            assert "metadata" in paper
            assert "year" in paper["metadata"]

    def test_seed_data_content(self):
        """Verify specific seed content exists."""
        texts = [c["text"] for c in SEED_CLINICAL_CASES]
        assert any("心肌梗死" in t for t in texts)
        assert any("接触性皮炎" in t for t in texts)
        assert any("上呼吸道感染" in t for t in texts)


class TestDocumentLoader:
    """DocumentLoader interface."""

    def setup_method(self):
        self.loader = DocumentLoader()

    def test_load_text_empty(self):
        """Loader should handle empty text gracefully."""
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                self.loader.load_text("", SourceType.CLINICAL_CASES)
            )
            assert result == 0  # No chunks from empty text
        finally:
            loop.close()
