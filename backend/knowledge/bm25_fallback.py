"""BM25 full-text search fallback — used when vector store is unavailable.

Implements BM25Okapi from scratch (no external dependency needed).
Each knowledge source maintains its own BM25 index.
"""

import math
import logging
import re
from typing import Any

from knowledge.source import SourceType, RetrievedChunk, SOURCE_CONFIGS

logger = logging.getLogger(__name__)


class BM25Index:
    """BM25Okapi index for a single knowledge source.

    Thread-safe for read operations. Build once, query many times.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75,
                 min_score_ratio: float = 0.2):
        self.k1 = k1
        self.b = b
        # Results scoring less than this fraction of the best hit are dropped:
        # BM25 scores are unbounded, and Chinese bi-gram tokenisation makes
        # unrelated queries pick up low-value matches on common characters.
        self.min_score_ratio = min_score_ratio
        self.documents: list[str] = []
        self.doc_metadata: list[dict] = []
        self.avg_doc_len: float = 0.0
        self.N: int = 0
        self.df: dict[str, int] = {}     # document frequency per term
        self.idf: dict[str, float] = {}  # precomputed IDF
        self._built = False

    def build(self, documents: list[str], metadata_list: list[dict] | None = None):
        """Build the BM25 index from a list of documents."""
        self.documents = documents
        self.doc_metadata = metadata_list or [{} for _ in documents]
        self.N = len(documents)
        total_len = 0

        # Tokenize and compute stats
        term_doc_lists: dict[str, list[int]] = {}
        for i, doc in enumerate(documents):
            terms = self._tokenize(doc)
            total_len += len(terms)
            seen = set()
            for term in terms:
                if term not in term_doc_lists:
                    term_doc_lists[term] = []
                if term not in seen:
                    term_doc_lists[term].append(i)
                    seen.add(term)

        self.avg_doc_len = total_len / max(self.N, 1)
        self.df = {term: len(docs) for term, docs in term_doc_lists.items()}
        self.N = max(self.N, 1)

        # Precompute IDF
        for term, doc_count in self.df.items():
            self.idf[term] = math.log(1 + (self.N - doc_count + 0.5) / (doc_count + 0.5))

        self._built = True
        logger.info("BM25 index built: %d documents, %d terms", self.N, len(self.df))

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Search the index with BM25 scoring. Returns scored documents."""
        if not self._built or self.N == 0:
            return []

        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        # Score each document
        scores = []
        for i, doc in enumerate(self.documents):
            score = self._score_doc(query_terms, self._tokenize(doc), len(doc.split()))
            if score > 0:
                scores.append((i, score))

        # Drop weak matches relative to the best hit for this query
        best = max((s for _, s in scores), default=0.0)
        if best > 0:
            floor = best * self.min_score_ratio
            scores = [(i, s) for i, s in scores if s >= floor]

        # Sort and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        scores = scores[:top_k]

        results = []
        for idx, score in scores:
            results.append({
                "text": self.documents[idx],
                "score": score,
                "source": self.doc_metadata[idx].get("source", ""),
                "metadata": self.doc_metadata[idx],
            })
        return results

    def _score_doc(self, query_terms: list[str], doc_terms: list[str], doc_len: int) -> float:
        """Compute BM25Okapi score for a single document."""
        score = 0.0
        doc_term_counts: dict[str, int] = {}
        for t in doc_terms:
            doc_term_counts[t] = doc_term_counts.get(t, 0) + 1

        for term in set(query_terms):
            tf = doc_term_counts.get(term, 0)
            if tf == 0:
                continue
            idf = self.idf.get(term, 0)
            if idf <= 0:
                continue
            tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len))
            score += idf * tf_norm

        return score

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer: lowercase, split on non-alphanumeric."""
        text = text.lower()
        # Handle Chinese: extract individual characters and word-level tokens
        tokens = re.findall(r'[一-鿿]+|[a-z]+', text)
        result = []
        for token in tokens:
            if re.match(r'[一-鿿]+', token):
                # For Chinese, use bi-gram characters
                for i in range(len(token)):
                    result.append(token[i])
                if len(token) > 1:
                    for i in range(len(token) - 1):
                        result.append(token[i:i+2])
            else:
                result.append(token)
        return result


class BM25Fallback:
    """Manages BM25 indices for all knowledge sources.

    Drop-in replacement for VectorStore when Qdrant is unavailable.
    """

    def __init__(self):
        self.indices: dict[SourceType, BM25Index] = {}

    def ensure_index(self, source: SourceType) -> BM25Index:
        """Get or create BM25 index for a source."""
        if source not in self.indices:
            self.indices[source] = BM25Index()
        return self.indices[source]

    def index_documents(self, source: SourceType, documents: list[str],
                        metadata: list[dict] | None = None):
        """Build/replace BM25 index for a source."""
        idx = self.ensure_index(source)
        idx.build(documents, metadata)
        logger.info("Indexed %d documents for %s", len(documents), source.value)

    async def search(self, source: SourceType, query: str, top_k: int = 10) -> list[RetrievedChunk]:
        """Fallback search using BM25."""
        idx = self.indices.get(source)
        if not idx or not idx._built:
            logger.warning("BM25 index not built for %s", source.value)
            return []

        results = idx.search(query, top_k=top_k)
        return [
            RetrievedChunk(
                text=r["text"],
                source=source,
                score=r["score"],
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

    async def search_all(self, query: str, top_k_per_source: int = 10) -> dict[SourceType, list[RetrievedChunk]]:
        """Search all available BM25 indices."""
        results = {}
        for source, idx in self.indices.items():
            if idx._built:
                results[source] = await self.search(source, query, top_k_per_source)
            else:
                results[source] = []
        return results
