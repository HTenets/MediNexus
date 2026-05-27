"""Qdrant vector store operations."""


class VectorStore:
    async def search(self, collection: str, vector: list[float], limit: int = 10) -> list[dict]:
        return []
