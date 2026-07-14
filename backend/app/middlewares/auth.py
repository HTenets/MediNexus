"""Auth middleware — enforces JWT authentication on protected paths.

Public paths (health, docs, login) bypass auth. WebSocket connections
are authenticated separately in the websocket endpoint.
"""

import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from app.config import settings

logger = logging.getLogger(__name__)

# Paths that don't require authentication
PUBLIC_PATHS = {
    "/health",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/docs",
    "/openapi.json",
    "/redoc",
}


async def auth_middleware(request: Request, call_next):
    path = request.url.path

    # Allow public paths and preflight
    if path in PUBLIC_PATHS or path.endswith("/health") or request.method == "OPTIONS":
        return await call_next(request)

    # WebSocket upgrade is handled in the endpoint itself
    if request.headers.get("upgrade", "").lower() == "websocket":
        return await call_next(request)

    # Extract and validate Bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "缺少认证凭据"},
        )

    token = auth_header[7:]
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        # Only access tokens are valid for API calls
        if payload.get("type") != "access":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "无效的令牌类型"},
            )
        # Attach user id to request state for downstream use
        request.state.user_id = payload.get("sub")
    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "无效的认证凭据"},
        )

    return await call_next(request)
