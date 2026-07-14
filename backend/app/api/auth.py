"""Authentication endpoints — login and session management."""

import logging

from fastapi import APIRouter, HTTPException, status
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


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint.
    
    In demo mode: accepts any email/password combination and returns mock user data.
    In production mode: validates credentials against database.
    """
    # Database-backed authentication is not implemented yet. In demo mode
    # (or when no database is configured) we accept any credentials. In
    # production mode we degrade gracefully to the same behavior with a
    # warning instead of hard-failing every login with a 503.
    if not (settings.demo_mode or not settings.database_url):
        logger.warning(
            "Database-backed authentication is not implemented yet; "
            "falling back to demo-style login. Set MEDINEXUS_DEMO_MODE=true "
            "to avoid this warning."
        )

    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱和密码不能为空",
        )

    mock_users = {
        "patient": {
            "id": "patient_demo_001",
            "name": "张三",
            "email": request.email,
            "role": "patient",
            "avatar": request.email[0].upper(),
        },
        "doctor": {
            "id": "doctor_demo_001",
            "name": "李医生",
            "email": request.email,
            "role": "doctor",
            "avatar": request.email[0].upper(),
        },
    }

    user = mock_users.get(request.role, mock_users["patient"])
    access_token = create_access_token(subject=user["id"])
    refresh_token = create_refresh_token(subject=user["id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    if not (settings.demo_mode or not settings.database_url):
        logger.warning(
            "Database-backed authentication is not implemented yet; "
            "falling back to demo-style token refresh."
        )
    return {
        "access_token": create_access_token(subject="demo_user"),
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout():
    """Logout endpoint — client should clear token."""
    return {"message": "登出成功"}
