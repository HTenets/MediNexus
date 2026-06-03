"""GraphRAGQuery — knowledge graph enhanced RAG.

Same API as rag.py for seamless switching (as designed in ADR-007).
Delegates to RAGQuery internally, adds knowledge graph enhancement.
"""

import logging
from typing import Any

from knowledge.rag import RAGQuery
from knowledge.source import FusionResult

logger = logging.getLogger(__name__)


class GraphRAGQuery:
    """Knowledge graph enhanced RAG. Identical API to RAGQuery.

    In v0.1.0, this wraps RAGQuery + adds KG enhancement.
    In future (v0.3.0+), this could use GraphRAG techniques
    (graph traversal + vector retrieval hybrid).
    """

    def __init__(self, rag_query: RAGQuery):
        self.rag_query = rag_query

    async def query(self, text: str, top_k: int = 5) -> FusionResult:
        return await self.rag_query.query(text, top_k=top_k, include_graph=True)

    async def query_formatted(self, text: str, top_k: int = 5,
                              format: str = "llm_context") -> str:
        return await self.rag_query.query_formatted(text, top_k=top_k, format=format)

    async def health_check(self) -> dict[str, Any]:
        return await self.rag_query.health_check()
