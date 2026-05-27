from pydantic import BaseModel
from typing import Any


class MemoryEntry(BaseModel):
    session_id: str
    patient_id: str
    content: dict[str, Any]
    memory_type: str = "episodic"  # episodic | semantic
