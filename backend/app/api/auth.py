"""Authentication endpoints — login and session management."""

import logging

from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.auth import create_access_token, create_refresh_token
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class LoginRequest(BaseModel):
    email: str = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")
    role: str = Field(..., pattern="^(patient|doctor)$", description="角色")


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


def _build_demo_user(email: str, role: str) -> dict:
    """Build a demo user profile (demo mode only)."""
    avatar = email[0].upper() if email else "U"
    role_key = role if role in ("patient", "doctor") else "patient"
    names = {"patient": "张三", "doctor": "李医生"}
    ids = {"patient": "patient_demo_001", "doctor": "doctor_demo_001"}
    return {
        "id": ids[role_key],
        "name": names[role_key],
        "email": email,
        "role": role_key,
        "avatar": avatar,
    }


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint.

    Demo mode: accepts any email/password and returns mock user data.
    Production mode: requires real credential validation — refuses login
    instead of silently accepting arbitrary credentials.
    """
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱和密码不能为空",
        )

    if settings.demo_mode or not settings.database_url:
        user = _build_demo_user(request.email, request.role)
    else:
        # Production mode: database-backed auth must be implemented.
        # Do NOT fall back to accepting arbitrary credentials.
        logger.error(
            "Production login attempted but database auth is not implemented. "
            "Set MEDINEXUS_DEMO_MODE=true until DB auth is ready."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="认证服务暂未配置，请联系管理员",
        )

    access_token = create_access_token(subject=user["id"])
    refresh_token = create_refresh_token(subject=user["id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresh access token using a valid refresh token.

    The refresh token is decoded and its subject is used to mint a new
    access token. Invalid or expired refresh tokens are rejected.
    """
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误，需要refresh token",
        )

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌缺少用户信息",
        )

    return {
        "access_token": create_access_token(subject=subject),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout():
    """Logout endpoint — client should clear token."""
    return {"message": "登出成功"}
