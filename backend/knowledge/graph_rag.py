"""GraphRAG interface — same API as rag.py for seamless switching."""


class GraphRAGQuery:
    async def query(self, text: str, top_k: int = 5) -> list[str]:
        return []
