"""Database initialization script — creates all tables directly (no alembic).

Prefer `alembic upgrade head` for environments with migration history;
this script remains for quick local bootstrap.
"""
import asyncio

from app.core.database import engine
from app.models import Base  # imports register all tables


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized.")


if __name__ == "__main__":
    asyncio.run(init())
