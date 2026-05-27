"""Database initialization script."""
import asyncio
from app.core.database import engine
from app.models.patient import Base


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")


if __name__ == "__main__":
    asyncio.run(init())
