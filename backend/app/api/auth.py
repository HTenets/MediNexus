"""Authentication endpoints — register, login, and session management.

When a database is configured, credentials are validated against the users
table (bcrypt hashes). Without a database (pure demo deployment), registered
users live in memory and unknown credentials fall back to demo accounts,
preserving the zero-setup demo experience.
"""

import logging
import uuid

from fastapi import APIRouter, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.config import settings
from app.core.auth import create_access_token, create_refresh_token
from app.core.database import AsyncSession, db_enabled
from app.core.password import MAX_PASSWORD_LENGTH, hash_password, verify_password
from app.repositories import user_repo

logger = logging.getLogger(__name__)

router = APIRouter()

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# In-memory user store for pure-demo deployments without a database
_memory_users: dict[str, dict] = {}


class RegisterRequest(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN, max_length=254, description="用户邮箱")
    password: str = Field(..., min_length=8, max_length=MAX_PASSWORD_LENGTH, description="密码（8-72位）")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    role: str = Field("patient", pattern="^(patient|doctor)$", description="角色")


class LoginRequest(BaseModel):
    email: str = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")
    role: str = Field("patient", pattern="^(patient|doctor)$", description="角色")


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


def _user_payload(user_id: str, name: str, email: str, role: str) -> dict:
    return {
        "id": user_id,
        "name": name,
        "email": email,
        "role": role,
        "avatar": (name or email or "U")[:1].upper(),
    }


def _issue_tokens(user_id: str) -> dict:
    return {
        "access_token": create_access_token(subject=user_id),
        "refresh_token": create_refresh_token(subject=user_id),
        "token_type": "bearer",
    }


def _build_demo_user(email: str, role: str) -> dict:
    """Fallback demo user for no-database deployments."""
    role_key = role if role in ("patient", "doctor") else "patient"
    names = {"patient": "张三", "doctor": "李医生"}
    ids = {"patient": "patient_demo_001", "doctor": "doctor_demo_001"}
    return _user_payload(ids[role_key], names[role_key], email, role_key)


@router.post("/register", response_model=LoginResponse, status_code=201)
async def register(request: RegisterRequest):
    """Register a new account and return auth tokens."""
    email = request.email.lower()

    if db_enabled():
        async with AsyncSession() as session:
            existing = await user_repo.get_by_email(session, email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="该邮箱已被注册"
                )
            user = await user_repo.create_user(
                session,
                user_id=f"user_{uuid.uuid4().hex[:12]}",
                email=email,
                password_hash=hash_password(request.password),
                name=request.name,
                role=request.role,
            )
        payload = _user_payload(user.id, user.name, user.email, user.role)
    else:
        if email in _memory_users:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="该邮箱已被注册"
            )
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        _memory_users[email] = {
            "id": user_id,
            "name": request.name,
            "role": request.role,
            "password_hash": hash_password(request.password),
        }
        logger.warning("Demo mode (no database): registered user held in memory only")
        payload = _user_payload(user_id, request.name, email, request.role)

    logger.info("Registered user: %s (%s)", payload["id"], email)
    return {**_issue_tokens(payload["id"]), "user": payload}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint.

    With a database: validates credentials against the users table.
    Without one: checks in-memory registered users, then falls back to demo
    accounts (documented pure-demo behavior).
    """
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱和密码不能为空"
        )
    email = request.email.lower()

    if db_enabled():
        async with AsyncSession() as session:
            user = await user_repo.get_by_email(session, email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
            )
        payload = _user_payload(user.id, user.name, user.email, user.role)
        return {**_issue_tokens(user.id), "user": payload}

    memory_user = _memory_users.get(email)
    if memory_user:
        if not verify_password(request.password, memory_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误"
            )
        payload = _user_payload(
            memory_user["id"], memory_user["name"], email, memory_user["role"]
        )
        return {**_issue_tokens(memory_user["id"]), "user": payload}

    logger.warning(
        "Demo login accepted without database for %s — data will not persist", email
    )
    user = _build_demo_user(email, request.role)
    return {**_issue_tokens(user["id"]), "user": user}


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresh access token using a valid refresh token."""
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
