"""User persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: str) -> User | None:
    return await session.get(User, user_id)


async def create_user(
    session: AsyncSession,
    *,
    user_id: str,
    email: str,
    password_hash: str,
    name: str,
    role: str,
) -> User:
    user = User(
        id=user_id,
        email=email.lower(),
        password_hash=password_hash,
        name=name,
        role=role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
