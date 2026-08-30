"""Knowledge search API — exposes the retrieval stack to the UI.

The "多维知识源分析" page used to fetch ``/api/mock/knowledge-*`` endpoints that
do not exist, so it could only ever render an empty shell. This wires it to the
real multi-source retriever, including the per-source confidence weighting and
knowledge-graph enhancement that the agents use internally.
"""

import logging

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.core.rag import get_rag_query

__all__ = ["router"]

logger = logging.getLogger(__name__)

router = APIRouter()

_SOURCE_LABELS = {
    "clinical_cases": "临床病例",
    "medical_theory": "医学理论",
    "latest_papers": "前沿论文",
}


def _title_for(chunk) -> str:
    meta = chunk.metadata or {}
    return (
        meta.get("disease")
        or meta.get("topic")
        or meta.get("title")
        or _SOURCE_LABELS.get(chunk.source.value, chunk.source.value)
    )


def _summary_for(chunk) -> str:
    text = " ".join((chunk.text or "").split())
    return text[:400]


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=500, description="检索关键词/症状描述"),
    top_k: int = Query(5, ge=1, le=20, description="每个来源返回的最大条数"),
    user_id: str = Depends(get_current_user),
):
    """Search the knowledge base across all three sources.

    Returns the same three-bucket shape the analysis page renders:
    ``cases`` / ``theory`` / ``papers``.
    """
    rag = get_rag_query()
    result = await rag.query(q, top_k=top_k * 3)

    buckets: dict[str, list[dict]] = {"cases": [], "theory": [], "papers": []}
    key_by_source = {
        "clinical_cases": "cases",
        "medical_theory": "theory",
        "latest_papers": "papers",
    }

    for chunk in result.chunks:
        key = key_by_source.get(chunk.source.value)
        if not key or len(buckets[key]) >= top_k:
            continue
        meta = chunk.metadata or {}
        buckets[key].append({
            "title": _title_for(chunk),
            "source": _SOURCE_LABELS.get(chunk.source.value, chunk.source.value),
            "journal": meta.get("journal"),
            "content": _summary_for(chunk),
            "score": round(chunk.final_score, 4),
            "confidence": chunk.confidence_weight,
        })

    return {
        "query": q,
        "route": "bm25" if rag.force_fallback else "vector",
        "activated_sources": [s.value for s in result.activated_sources],
        "total": sum(len(v) for v in buckets.values()),
        **buckets,
    }


@router.get("/health")
async def knowledge_health():
    """Report which retrieval components are actually available.

    Public: it exposes only component availability, no patient data.
    """
    rag = get_rag_query()
    return await rag.health_check()
