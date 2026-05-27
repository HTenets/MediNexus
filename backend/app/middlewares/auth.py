from fastapi import Request, HTTPException
from app.core.auth import get_current_user


async def auth_middleware(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)
    try:
        await get_current_user(request)
    except HTTPException:
        pass  # Proper auth middleware TBD
    return await call_next(request)
