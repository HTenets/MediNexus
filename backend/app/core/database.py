"""Database engine — gracefully handles demo mode (no DB)."""

import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

# Demo mode: database engine is None
_engine = None
AsyncSession = None

if settings.database_url:
    _engine = create_async_engine(settings.database_url, echo=False)
    AsyncSession = async_sessionmaker(_engine, expire_on_commit=False)
    logger.info("Database engine initialized: %s", settings.database_url[:30] + "...")
else:
    logger.info("No DATABASE_URL configured — running in demo mode without database.")

engine = _engine


async def get_session():
    """FastAPI dependency: yields an async DB session.

    In demo mode, raises RuntimeError (caller should handle gracefully).
    """
    if AsyncSession is None:
        raise RuntimeError("Database not configured — running in demo mode")
    async with AsyncSession() as session:
        yield session
