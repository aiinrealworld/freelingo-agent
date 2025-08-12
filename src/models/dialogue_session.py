from pydantic import BaseModel
from typing import List, Literal, Optional

class DialogueSessionMessage(BaseModel):
    id: str
    text: str
    sender: Literal['ai', 'user']
    timestamp: str  # ISO8601

class DialogueSessionRequest(BaseModel):
    user_id: str
    messages: List[DialogueSessionMessage]
    started_at: Optional[str] = None
    ended_at: Optional[str] = None

class DialogueSessionResponse(BaseModel):
    session_id: str
    status: str 