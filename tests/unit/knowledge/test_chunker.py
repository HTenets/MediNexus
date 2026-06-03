"""Tests for chunking strategies."""

from knowledge.chunker import SemanticChunker, HierarchicalChunker, RecursiveChunker, get_chunker
from knowledge.source import SourceType


class TestSemanticChunker:
    """SemanticChunker — preserves paragraph boundaries."""

    def setup_method(self):
        self.chunker = SemanticChunker(chunk_size=200, overlap=20)

    def test_empty_text(self):
        chunks = self.chunker.chunk("")
        assert len(chunks) == 0

    def test_single_paragraph(self):
        chunks = self.chunker.chunk("Hello world. This is a single paragraph.")
        assert len(chunks) >= 1
        assert "Hello world" in chunks[0]["text"]

    def test_paragraph_splitting(self):
        text = "Paragraph one. More text.\n\nParagraph two.\n\nParagraph three."
        chunks = self.chunker.chunk(text)
        # With chunk_size=200, each paragraph should fit separately
        assert len(chunks) >= 1

    def test_metadata_preserved(self):
        chunks = self.chunker.chunk("Test text", metadata={"source": "test"})
        assert chunks[0]["metadata"]["source"] == "test"

    def test_long_paragraph_split(self):
        """If a single paragraph exceeds chunk_size, split it."""
        long_text = "word " * 500
        chunks = self.chunker.chunk(long_text)
        assert len(chunks) > 1

    def test_chunk_strategy_metadata(self):
        chunks = self.chunker.chunk("Test")
        assert chunks[0]["metadata"]["chunk_strategy"] == "semantic"


class TestHierarchicalChunker:
    """HierarchicalChunker — parent-child chunking."""

    def setup_method(self):
        self.chunker = HierarchicalChunker(chunk_size=300, overlap=30, child_size=100)

    def test_parent_child_ratio(self):
        text = "# Section 1\n\nLots of content here. " * 20
        chunks = self.chunker.chunk(text)
        # Should have both parent and child chunks
        types = [c["metadata"]["type"] for c in chunks]
        assert "parent" in types
        assert "child" in types

    def test_children_have_parent_text(self):
        text = "# Title\n\nContent paragraph.\n\nMore content." * 10
        chunks = self.chunker.chunk(text)
        children = [c for c in chunks if c["metadata"]["type"] == "child"]
        if children:
            assert "parent_text" in children[0]["metadata"]

    def test_metadata_preserved(self):
        chunks = self.chunker.chunk("Test", metadata={"source": "theory"})
        assert chunks[0]["metadata"]["source"] == "theory"


class TestRecursiveChunker:
    """RecursiveChunker — separator-priority splitting."""

    def setup_method(self):
        self.chunker = RecursiveChunker(chunk_size=200, overlap=20)

    def test_section_aware_split(self):
        text = "## Abstract\n\nThis is the abstract.\n\n## Introduction\n\nBackground info.\n\n## Conclusion\n\nSummary."
        chunks = self.chunker.chunk(text)
        assert len(chunks) >= 1

    def test_recursive_fallback(self):
        text = "word " * 50
        chunks = self.chunker.chunk(text)
        assert len(chunks) >= 1

    def test_empty_text(self):
        chunks = self.chunker.chunk("")
        assert len(chunks) == 0


class TestChunkerFactory:
    """get_chunker factory function."""

    def test_semantic_for_cases(self):
        chunker = get_chunker(SourceType.CLINICAL_CASES, 384, 40)
        assert isinstance(chunker, SemanticChunker)

    def test_hierarchical_for_theory(self):
        chunker = get_chunker(SourceType.MEDICAL_THEORY, 768, 80)
        assert isinstance(chunker, HierarchicalChunker)

    def test_recursive_for_papers(self):
        chunker = get_chunker(SourceType.LATEST_PAPERS, 512, 50)
        assert isinstance(chunker, RecursiveChunker)
