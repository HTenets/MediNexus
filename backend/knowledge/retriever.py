"""Multi-source retriever — RRF fusion, Z-score normalization, confidence weighting.

Implements the HF-RAG (CIKM 2025) hierarchical fusion approach:
  1. Intra-source: RRF fusion of multiple retrieval methods per source
  2. Inter-source: Z-score normalization to align score distributions
  3. Confidence weighting: Apply source-specific weights (0.8/0.6/0.3)
  4. Final ranking: Weighted combination → sorted by final_score

多源检索器 — RRF (Reciprocal Rank Fusion) 互惠排名融合，Z 分数归一化，置信度加权。

实现 HF-RAG（CIKM 2025）分层融合方法：
1. 源内：对每个源的多种检索方法进行 RRF 融合
2. 源间：使用 Z 分数归一化对分数分布进行对齐
3. 置信度加权：应用源特定权重（0.8/0.6/0.3）
4. 最终排序：加权组合 → 按 final_score 排序

"""

import logging
import math
from statistics import mean, stdev
from typing import Any

from knowledge.source import (
    SourceType,
    SourceConfig,
    RetrievedChunk,
    FusionResult,
    SOURCE_CONFIGS,
)

logger = logging.getLogger(__name__)


class MultiSourceRetriever:
    """Orchestrates multi-source retrieval with fusion."""

    def __init__(self, vector_store: Any, bm25_fallback: Any | None = None,
                 embedder: Any | None = None):
        self.vector_store = vector_store
        self.bm25_fallback = bm25_fallback
        self.embedder = embedder          # callable: text → list[float]
        self.rrf_k = 60                   # RRF constant

    # ── Main Entry Point ──────────────────────────────────────────────── #

    async def retrieve(self, query: str, top_k: int = 5,
                       use_fallback: bool = False) -> FusionResult:
        """Multi-source retrieval → fusion → ranked results.

        Args:
            query: User symptom/query text
            top_k: Final number of results to return
            use_fallback: Use BM25 instead of vector search (Qdrant unavailable)
        """
        if use_fallback:
            return await self._retrieve_bm25(query, top_k)
        else:
            return await self._retrieve_vector(query, top_k)

    # ── Vector Route ─────────────────────────────────────────────────── #

    async def _retrieve_vector(self, query: str, top_k: int) -> FusionResult:
        query_vector = await self._embed(query)
        if not query_vector:
            logger.warning("Embedding failed, falling back to BM25")
            return await self._retrieve_bm25(query, top_k)

        # Step 1: Search all source collections in parallel
        collections = [cfg.collection_name for cfg in SOURCE_CONFIGS.values()]
        raw_results = await self.vector_store.search_batch(
            collections, query_vector,
            limit_per_source=max(cfg.top_k_initial for cfg in SOURCE_CONFIGS.values()),
        )

        # Step 2: Convert to RetrievedChunk list per source
        source_chunks: dict[SourceType, list[RetrievedChunk]] = {}
        activated_sources = []
        for stype, cfg in SOURCE_CONFIGS.items():
            chunks = []
            for item in raw_results.get(cfg.collection_name, []):
                if item.get("score", 0) >= cfg.similarity_threshold:
                    chunks.append(RetrievedChunk(
                        text=item.get("text", ""),
                        source=stype,
                        score=item.get("score", 0),
                        metadata=item.get("metadata", {}),
                    ))
            if chunks:
                source_chunks[stype] = chunks
                activated_sources.append(stype)

        if not source_chunks:
            logger.info("No results from any source for query: %.50s", query)
            return FusionResult(chunks=[], source_counts={}, query=query, activated_sources=[])

        # Step 3: RRF intra-source fusion (for sources with multiple retrievers)
        # For now, each source uses a single retriever, so RRF is just ranking
        for stype in source_chunks:
            source_chunks[stype].sort(key=lambda c: c.score, reverse=True)

        # Step 4: Z-score inter-source normalization
        all_chunks = self._z_score_normalize(source_chunks)

        # Step 5: Confidence weighting
        for chunk in all_chunks:
            chunk.final_score = chunk.z_score * chunk.confidence_weight

        # Step 6: Sort and return top_k
        all_chunks.sort(key=lambda c: c.final_score, reverse=True)

        source_counts = {}
        for c in all_chunks:
            source_counts[c.source.value] = source_counts.get(c.source.value, 0) + 1

        return FusionResult(
            chunks=all_chunks[:top_k],
            source_counts=source_counts,
            query=query,
            activated_sources=activated_sources,
        )

    # ── BM25 Fallback Route ──────────────────────────────────────────── #

    async def _retrieve_bm25(self, query: str, top_k: int) -> FusionResult:
        if not self.bm25_fallback:
            logger.warning("BM25 fallback not configured")
            return FusionResult(chunks=[], source_counts={}, query=query, activated_sources=[])

        bm25_results = await self.bm25_fallback.search_all(query)

        # Convert and weight
        all_chunks = []
        for stype, chunks in bm25_results.items():
            if not chunks:
                continue
            for chunk in chunks:
                chunk.final_score = chunk.score * chunk.confidence_weight
                all_chunks.append(chunk)

        # For BM25, skip Z-score (scores are already BM25 scores, not comparable
        # to anything else anyway since BM25 is the only route)
        all_chunks.sort(key=lambda c: c.final_score, reverse=True)

        source_counts = {}
        for c in all_chunks:
            source_counts[c.source.value] = source_counts.get(c.source.value, 0) + 1

        return FusionResult(
            chunks=all_chunks[:top_k],
            source_counts=source_counts,
            query=query,
            activated_sources=list(set(c.source for c in all_chunks)),
        )

    # ── Normalization ────────────────────────────────────────────────── #

    def _z_score_normalize(self,
                           source_chunks: dict[SourceType, list[RetrievedChunk]]
                           ) -> list[RetrievedChunk]:
        """Z-score normalize scores within each source, then collect all."""
        all_chunks = []

        for stype, chunks in source_chunks.items():
            if len(chunks) < 2:
                # Single or no result — use raw score / max as pseudo Z
                max_score = max((c.score for c in chunks), default=1.0)
                for c in chunks:
                    c.z_score = c.score / max_score if max_score > 0 else 0
                all_chunks.extend(chunks)
                continue

            scores = [c.score for c in chunks]
            mu = mean(scores)
            sigma = stdev(scores)
            if sigma == 0:
                sigma = 1.0  # avoid division by zero

            for c in chunks:
                c.z_score = (c.score - mu) / sigma
            all_chunks.extend(chunks)

        return all_chunks

    # ── Embedding ─────────────────────────────────────────────────────── #

    async def _embed(self, text: str) -> list[float] | None:
        """Get embedding vector for text."""
        if self.embedder:
            if hasattr(self.embedder, "__call__"):
                return await self.embedder(text) if hasattr(self.embedder, "__call__") else None
            return self.embedder(text)
        return None
