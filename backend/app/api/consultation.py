from fastapi import APIRouter, Depends
from app.core.dependencies import get_session_id

router = APIRouter()


@router.post("")
async def start_consultation(session_id: str = Depends(get_session_id)):
    return {"session_id": session_id, "status": "started"}


@router.get("/{consult_id}")
async def get_consultation(consult_id: str):
    return {"consult_id": consult_id, "status": "pending"}
