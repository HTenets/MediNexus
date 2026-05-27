"""RAG query interface (abstract)."""


class RAGQuery:
    async def query(self, text: str, top_k: int = 5) -> list[str]:
        return []
