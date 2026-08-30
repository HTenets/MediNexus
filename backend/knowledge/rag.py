"""RAGQuery — multi-source retrieval-augmented generation.

Integrates:
  - 3 knowledge sources (cases/theory/papers) with confidence weighting
  - RRF + Z-score fusion (HF-RAG style)
  - BM25 fallback when vector store is down
  - Optional knowledge graph enhancement
"""

import logging
from typing import Any

from knowledge.source import FusionResult, SourceType
from knowledge.retriever import MultiSourceRetriever
from knowledge.graph import KnowledgeGraph

logger = logging.getLogger(__name__)


class RAGQuery:
    """Main entry point for knowledge retrieval. Used by Doctor and Review agents."""

    def __init__(self, retriever: MultiSourceRetriever | None = None,
                 knowledge_graph: KnowledgeGraph | None = None,
                 force_fallback: bool = False):
        self.retriever = retriever
        self.knowledge_graph = knowledge_graph
        # ``force_fallback`` is set when no vector store is configured at all:
        # BM25 is then not a degraded mode but the intended retrieval path.
        self.force_fallback = force_fallback
        self._vector_store_healthy = not force_fallback

    async def query(self, text: str, top_k: int = 5,
                    use_fallback: bool | None = None,
                    include_graph: bool = True) -> FusionResult:
        """Execute multi-source retrieval with optional KG enhancement.

        Args:
            text: Query text (symptoms, diagnosis, etc.)
            top_k: Number of final results
            use_fallback: Force BM25 fallback (None = auto-detect)
            include_graph: Whether to enhance with knowledge graph
        """
        # Auto-detect fallback
        if use_fallback is None:
            use_fallback = self.force_fallback or not self._vector_store_healthy

        # Retrieve from multi-source
        result = await self.retriever.retrieve(text, top_k=top_k, use_fallback=use_fallback)

        # Enhance with knowledge graph if available
        if include_graph and self.knowledge_graph and result.chunks:
            result = await self._enhance_with_graph(result)

        return result

    async def query_formatted(self, text: str, top_k: int = 5,
                              format: str = "llm_context") -> str:
        """Query and return formatted string ready for LLM context injection.

        Args:
            format: "llm_context" (default) | "review" | "simple"
        """
        result = await self.query(text, top_k=top_k)

        if format == "simple":
            return "\n\n".join(c.text for c in result.chunks)

        return self._format_for_llm(result)

    def _format_for_llm(self, result: FusionResult) -> str:
        """Format fusion result as LLM context block."""
        if not result.chunks:
            return ""

        lines = ["## 知识库检索结果", ""]

        # Source summary
        lines.append(f"### 检索来源: {', '.join(s.value for s in result.activated_sources)}")
        lines.append("")

        for i, chunk in enumerate(result.chunks, 1):
            source_label = {
                SourceType.CLINICAL_CASES: "📋 临床病例",
                SourceType.MEDICAL_THEORY: "📚 医学理论",
                SourceType.LATEST_PAPERS: "📄 最新论文",
            }.get(chunk.source, str(chunk.source))

            lines.append(f"**[{i}] {source_label}** (可信度: {chunk.confidence_weight:.1f})")
            lines.append(chunk.text)
            lines.append("")

        # Evidence level note
        lines.append("---")
        lines.append("*以上内容由知识库检索生成，仅供参考。置信度: 病例=0.8(高), 理论=0.6(中), 论文=0.3(低)*")

        return "\n".join(lines)

    # ── Health Check ──────────────────────────────────────────────────── #

    async def health_check(self) -> dict[str, Any]:
        """Check all components health."""
        status = {"vector_store": False, "bm25": False, "graph": False}

        if self.retriever and self.retriever.vector_store:
            try:
                healthy = await self.retriever.vector_store.health_check()
                status["vector_store"] = healthy
                self._vector_store_healthy = healthy
            except Exception:
                self._vector_store_healthy = False

        status["bm25"] = self.retriever and self.retriever.bm25_fallback is not None
        status["graph"] = self.knowledge_graph is not None

        return status

    # ── KG Enhancement ────────────────────────────────────────────────── #

    async def _enhance_with_graph(self, result: FusionResult) -> FusionResult:
        """Enhance retrieval results with knowledge graph relations."""
        if not self.knowledge_graph:
            return result

        graph_info = await self.knowledge_graph.query(result.query)
        if not graph_info:
            return result

        # Add graph results as additional context chunks
        from knowledge.source import RetrievedChunk
        graph_chunk = RetrievedChunk(
            text=graph_info,
            source=SourceType.CLINICAL_CASES,  # Use clinical weight for KG results
            score=0.7,
            metadata={"source_type": "knowledge_graph"},
        )
        # Recalculate scores
        graph_chunk.z_score = 1.0
        graph_chunk.final_score = 0.7 * graph_chunk.confidence_weight

        # Insert at position 1 (after top result)
        result.chunks.insert(0, graph_chunk)

        return result
