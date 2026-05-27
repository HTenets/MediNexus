from fastapi import Request, Depends
from app.core.auth import get_current_user


async def get_session_id(request: Request, user: str = Depends(get_current_user)):
    return request.headers.get("X-Session-Id", "default")
