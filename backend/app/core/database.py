from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.database_url)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSession() as session:
        yield session
