"""Memory manager — hierarchical retrieval."""


class MemoryManager:
    async def retrieve(self, patient_id: str, context: str) -> str:
        return ""

    async def store(self, patient_id: str, memory_type: str, data: dict):
        pass
