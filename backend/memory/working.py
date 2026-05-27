"""Working memory via Redis."""


class WorkingMemory:
    async def get(self, key: str) -> str | None:
        return None

    async def set(self, key: str, value: str, ttl: int = 3600):
        pass
