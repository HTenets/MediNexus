"""Application-wide handle on the retrieval stack.

The RAG instance is built once at startup (see ``app.main``) because indexing
the knowledge base is not free. Modules that need retrieval — agents via the
supervisor, and the knowledge API — pull it from here instead of each building
their own copy.
"""

from typing import Any

_rag_query: Any = None


def set_rag_query(rag_query) -> None:
    """Install the process-wide RAGQuery instance."""
    global _rag_query
    _rag_query = rag_query


def get_rag_query():
    """Return the shared RAGQuery, building it lazily on first use.

    Lazy construction keeps callers (and tests) working even when they import
    the module without going through the app lifespan.
    """
    global _rag_query
    if _rag_query is None:
        from knowledge.factory import create_rag_query

        _rag_query = create_rag_query()
    return _rag_query
