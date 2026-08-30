"""RAG factory — wires the retrieval stack together at startup.

Until now ``RAGQuery`` existed but was never instantiated, so ReviewAgent and
DoctorAgent silently fell back to a keyword lookup over seed snippets. This
module builds a real retrieval stack:

  - **BM25 route (always available)** — indices built from the bundled seed
    clinical cases / theory / papers. This is genuine multi-source retrieval
    with RRF + Z-score fusion, not a stub; it just doesn't need Qdrant.
  - **Vector route (optional)** — when ``MEDINEXUS_QDRANT_URL`` *and* an
    embedding provider are configured, Qdrant-backed semantic search is used
    and BM25 stays as the automatic fallback.
  - **Knowledge graph** — the seeded symptom→disease graph enhances recall.

Deliberately *not* implemented: a fake/local hash-based "embedding". BM25 is an
honest retrieval path; a hashing embedder would produce meaningless vectors and
make the demo look more capable than it is.
"""

import logging
from typing import Any
from urllib.parse import urlparse

from app.config import settings
from knowledge.bm25_fallback import BM25Fallback
from knowledge.graph import KnowledgeGraph
from knowledge.loader import (
    SEED_CLINICAL_CASES,
    SEED_MEDICAL_THEORY,
    SEED_PAPER_ABSTRACTS,
)
from knowledge.rag import RAGQuery
from knowledge.retriever import MultiSourceRetriever
from knowledge.source import SourceType

logger = logging.getLogger(__name__)

_SEED_BY_SOURCE = {
    SourceType.CLINICAL_CASES: SEED_CLINICAL_CASES,
    SourceType.MEDICAL_THEORY: SEED_MEDICAL_THEORY,
    SourceType.LATEST_PAPERS: SEED_PAPER_ABSTRACTS,
}


def build_bm25() -> BM25Fallback:
    """Index the bundled seed knowledge into per-source BM25 indices."""
    bm25 = BM25Fallback()
    for source_type, docs in _SEED_BY_SOURCE.items():
        texts = [d["text"] for d in docs if d.get("text")]
        metadata = [d.get("metadata", {}) for d in docs if d.get("text")]
        if texts:
            bm25.index_documents(source_type, texts, metadata)
    logger.info("BM25 knowledge base ready: %d sources indexed", len(_SEED_BY_SOURCE))
    return bm25


def build_knowledge_graph() -> KnowledgeGraph:
    """Load the seeded symptom→disease graph."""
    from knowledge.graph.symptom_graph import SEED_DISEASE_INFO, SEED_SYMPTOM_MAP

    graph = KnowledgeGraph()
    graph.load_from_dict(SEED_SYMPTOM_MAP)
    graph.set_disease_info(SEED_DISEASE_INFO)
    return graph


# ── Embeddings ────────────────────────────────────────────────────────── #

async def _ollama_embed(model: str, base_url: str, text: str) -> list[float]:
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/api/embeddings",
            json={"model": model, "prompt": text},
        )
        resp.raise_for_status()
        return resp.json().get("embedding") or []


async def _openai_embed(model: str, base_url: str, api_key: str, text: str) -> list[float]:
    import httpx

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "input": text},
        )
        resp.raise_for_status()
        data = resp.json().get("data") or []
        return data[0].get("embedding") if data else []


def build_embedder() -> tuple[Any | None, int]:
    """Build an embedding callable plus its vector dimension.

    Returns ``(None, 0)`` when no embedding provider is configured — callers
    then use the BM25 route.
    """
    provider = (settings.embedding_provider or "").lower()
    model = settings.embedding_model
    base_url = settings.embedding_base_url
    api_key = settings.embedding_api_key

    # Ollama ships embeddings on the same host as generation, so it is the
    # natural default for a self-hosted deployment.
    if provider in ("", "ollama", "auto"):
        if provider == "ollama" or (provider == "auto" and settings.llm_provider == "ollama"):
            model = model or settings.ollama_model
            base_url = base_url or settings.ollama_base_url
            if model and base_url:
                async def _embed(text: str, _m=model, _u=base_url) -> list[float]:
                    return await _ollama_embed(_m, _u, text)
                return _embed, settings.embedding_dim or 768

    if provider in ("openai", "deepseek", "moonshot") and api_key:
        model = model or "text-embedding-3-small"
        base_url = base_url or "https://api.openai.com/v1"

        async def _embed(text: str, _m=model, _u=base_url, _k=api_key) -> list[float]:
            return await _openai_embed(_m, _u, _k, text)
        return _embed, settings.embedding_dim or 1536

    if provider and provider not in ("auto", "none"):
        logger.warning("Embedding provider '%s' not usable (missing key or base URL)", provider)
    return None, 0


# ── Vector store ──────────────────────────────────────────────────────── #

def _parse_qdrant(url: str) -> tuple[str, int]:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    return parsed.hostname or "localhost", parsed.port or 6333


def build_vector_store(vector_size: int):
    """Construct the Qdrant-backed store, or None if unusable."""
    try:
        from knowledge.vector_store import VectorStore
    except ImportError:
        logger.info("qdrant-client not installed — using BM25 retrieval route")
        return None

    host, port = _parse_qdrant(settings.qdrant_url)
    try:
        return VectorStore(host=host, port=port, vector_size=vector_size)
    except Exception as e:  # noqa: BLE001
        logger.warning("Qdrant store unavailable at %s:%s (%s) — using BM25", host, port, e)
        return None


# ── Public entry point ────────────────────────────────────────────────── #

def create_rag_query() -> RAGQuery:
    """Build the shared RAGQuery instance used by the agents.

    Never raises: the worst case is a BM25-only RAGQuery, which is a fully
    functional retrieval stack.
    """
    bm25 = build_bm25()
    graph = build_knowledge_graph()

    vector_store = None
    embedder = None

    if settings.qdrant_url:
        embedder, dim = build_embedder()
        if embedder:
            vector_store = build_vector_store(dim)
        else:
            logger.info("No embedding provider configured — using BM25 retrieval route")
    else:
        logger.info("No QDRANT_URL configured — using BM25 retrieval route")

    retriever = MultiSourceRetriever(
        vector_store=vector_store,
        bm25_fallback=bm25,
        embedder=embedder,
    )

    rag = RAGQuery(retriever=retriever, knowledge_graph=graph, force_fallback=vector_store is None)
    logger.info(
        "RAG ready (route=%s, knowledge_graph=on)",
        "bm25" if vector_store is None else "qdrant+bm25-fallback",
    )
    return rag
