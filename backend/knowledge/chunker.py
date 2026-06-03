"""Chunking strategies for different knowledge source types.

Three strategies:
  - semantic:    Split by semantic boundaries (paragraphs/sections), preserve entity integrity
  - hierarchical: Parent-child chunking (big for context, small for retrieval)
  - recursive:   Recursive character splitting with prioritized separators
"""

import re
from typing import Any

from knowledge.source import SourceType


class BaseChunker:
    """Base chunker interface."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Split text into chunks, each with metadata."""
        raise NotImplementedError


class SemanticChunker(BaseChunker):
    """Semantic boundary chunking — preserves paragraph/section integrity.

    Used for: Clinical Cases (源A)
    Strategy: Split at paragraph boundaries (double newlines), then merge small
    paragraphs up to chunk_size. Preserve case structure (主诉/检查/诊断/治疗).

    策略：在段落边界（双换行）处拆分，然后将小段落合并直到达到 chunk_size。
    保留case结构（主诉/检查/诊断/治疗）

    """

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        metadata = metadata or {}
        paragraphs = re.split(r'\n\s*\n', text.strip())
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += ("\n\n" + para) if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(self._make_chunk(current_chunk, metadata))
                # If a single paragraph exceeds chunk_size, split it
                if len(para) > self.chunk_size:
                    for i in range(0, len(para), self.chunk_size - self.overlap):
                        sub_para = para[i:i + self.chunk_size]
                        chunks.append(self._make_chunk(sub_para, metadata))
                else:
                    current_chunk = para
        # 保存最后一个未完成的chunk
        if current_chunk:
            chunks.append(self._make_chunk(current_chunk, metadata))

        return chunks

    def _make_chunk(self, text: str, metadata: dict) -> dict[str, Any]:
        return {"text": text, "metadata": {**metadata, "chunk_strategy": "semantic"}}


class HierarchicalChunker(BaseChunker):
    """Parent-child hierarchical chunking.

    Used for: Medical Theory (源B)
    Parent chunks (768 tokens) carry full context.
    Child chunks (192 tokens) are precise targets for retrieval.
    When a child matches, its parent is returned to the LLM.
    """

    def __init__(self, chunk_size: int = 768, overlap: int = 80, child_size: int = 192):
        super().__init__(chunk_size, overlap)
        self.child_size = child_size

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        metadata = metadata or {}

        # Split by Markdown headers to preserve document structure
        sections = re.split(r'(^#+ .+$)', text.strip(), flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        # Group sections into parent chunks
        parent_chunks = self._build_parents(sections)

        result = []
        for parent_text in parent_chunks:
            parent_meta = {**metadata, "chunk_strategy": "hierarchical", "type": "parent"}
            result.append({"text": parent_text, "metadata": parent_meta})

            # Generate child chunks from parent
            child_meta = {**metadata, "chunk_strategy": "hierarchical", "type": "child", "parent_text": parent_text}
            children = self._split_children(parent_text)
            for child in children:
                result.append({"text": child, "metadata": child_meta})

        return result

    def _build_parents(self, sections: list[str]) -> list[str]:
        """Group sections into parent-size chunks."""
        parents = []
        current = ""
        for sec in sections:
            if len(current) + len(sec) > self.chunk_size and current:
                parents.append(current.strip())
                if len(sec) > self.chunk_size:
                    # Oversized section becomes its own parent
                    parents.append(sec)
                    current = ""
                else:
                    current = sec
            else:
                current += "\n\n" + sec if current else sec
        if current:
            parents.append(current.strip())
        return parents

    def _split_children(self, text: str) -> list[str]:
        """Split parent text into overlapping child chunks."""
        children = []
        start = 0
        while start < len(text):
            end = min(start + self.child_size, len(text))
            children.append(text[start:end])
            start += self.child_size - self.overlap
        return children


class RecursiveChunker(BaseChunker):
    """Recursive character splitting with prioritized separators.
    带有优先分隔符的递归字符拆分

    Used for: Latest Papers (源C)
    Separator priority: "\n\n" > "\n" > ". " > " " > character
    Preserves abstract and conclusion sections.
    """

    SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not text or not text.strip():
            return []
        metadata = metadata or {}

        # First, extract abstract and conclusion if present
        abstract = ""
        conclusion = ""
        parts = re.split(r'(##?\s*(?:Abstract|摘要|Conclusion|结论|Background|背景))', text, flags=re.IGNORECASE)
        if len(parts) > 1:
            # Has section headers — use them
            return self._section_aware_chunk(text, metadata)
        else:
            # No clear sections — use recursive split
            return self._recursive_split(text, metadata)

    def _section_aware_chunk(self, text: str, metadata: dict) -> list[dict[str, Any]]:
        """Split by sections, keep each section as a chunk."""
        sections = re.split(r'(^#+ .+$)', text.strip(), flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        chunks = []
        current_section = "introduction"
        buffer = ""
        for sec in sections:
            if sec.startswith("#"):
                if buffer:
                    chunks.append(self._make_chunk(buffer, {**metadata, "section": current_section}))
                current_section = sec.lstrip("#").strip()
                buffer = sec + "\n"
            else:
                buffer += sec + "\n"
                if len(buffer) >= self.chunk_size:
                    chunks.append(self._make_chunk(buffer, {**metadata, "section": current_section}))
                    buffer = ""

        if buffer:
            chunks.append(self._make_chunk(buffer, {**metadata, "section": current_section}))
        return chunks

    def _recursive_split(self, text: str, metadata: dict) -> list[dict[str, Any]]:
        """Recursive character splitting with separator priority."""
        chunks = []
        self._split_recursive(text, self.SEPARATORS, 0, chunks, metadata)
        return chunks

    def _split_recursive(self, text: str, separators: list[str], depth: int,
                         chunks: list[dict], metadata: dict):
        if len(text) <= self.chunk_size or depth >= len(separators):
            chunks.append(self._make_chunk(text, metadata))
            return

        sep = separators[depth]
        if sep:
            parts = text.split(sep)
        else:
            parts = list(text)  # fallback: character-level

        current = ""
        for part in parts:
            if not part.strip():
                continue
            if len(current) + len(part) + len(sep) <= self.chunk_size:
                current += (sep + part) if current else part
            else:
                if current:
                    chunks.append(self._make_chunk(current.strip(), metadata))
                current = part

        if current:
            # If a single part is still too long, recurse with next separator
            if len(current) > self.chunk_size:
                self._split_recursive(current, separators, depth + 1, chunks, metadata)
            else:
                chunks.append(self._make_chunk(current.strip(), metadata))

    def _make_chunk(self, text: str, metadata: dict) -> dict[str, Any]:
        return {"text": text, "metadata": {**metadata, "chunk_strategy": "recursive"}}


# ── Factory ─────────────────────────────────────────────────────────────── #

def get_chunker(source_type: SourceType, chunk_size: int, overlap: int) -> BaseChunker:
    """Factory: return the appropriate chunker for the source type."""
    if source_type == SourceType.CLINICAL_CASES:
        return SemanticChunker(chunk_size, overlap)
    elif source_type == SourceType.MEDICAL_THEORY:
        return HierarchicalChunker(chunk_size, overlap)
    elif source_type == SourceType.LATEST_PAPERS:
        return RecursiveChunker(chunk_size, overlap)
    raise ValueError(f"Unknown source type: {source_type}")


