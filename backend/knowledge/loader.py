"""Document loading and chunking pipeline."""


class DocumentLoader:
    async def load(self, path: str) -> list[str]:
        return []

    async def chunk(self, documents: list[str], chunk_size: int = 512) -> list[str]:
        result = []
        for doc in documents:
            result.extend([doc[i:i+chunk_size] for i in range(0, len(doc), chunk_size)])
        return result
