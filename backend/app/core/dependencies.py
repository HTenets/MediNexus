"""FastAPI dependency injection — reusable dependencies."""

from fastapi import Request, Depends
from app.core.auth import get_optional_user


async def get_session_id(request: Request) -> str:
    """Extract session ID from request header or cookie."""
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        session_id = request.cookies.get("session_id", "default")
    return session_id


async def get_current_patient_id(
    request: Request,
    user: str | None = Depends(get_optional_user),
) -> str:
    """Extract patient ID from path, query, or auth."""
    patient_id = request.path_params.get("patient_id")
    if not patient_id:
        patient_id = request.query_params.get("patient_id")
    if not patient_id and user:
        patient_id = user
    return patient_id or "anonymous"


async def pagination_params(page: int = 1, page_size: int = 20) -> dict:
    """Standard pagination parameters."""
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    return {"page": page, "page_size": page_size}
