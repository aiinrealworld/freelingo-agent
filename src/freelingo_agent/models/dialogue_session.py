from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any

class DialogueSessionMessage(BaseModel):
    id: str
    text: str  # Clean text for UI display
    sender: Literal['ai', 'user']
    timestamp: str  # ISO8601
    # Full agent response for AI messages (for feedback agent later)
    agent_response: Optional[Dict[str, Any]] = None  # Full response with rationale, rule_checks, etc.

class DialogueSessionRequest(BaseModel):
    user_id: str
    messages: List[DialogueSessionMessage]
    started_at: Optional[str] = None
    ended_at: Optional[str] = None

class DialogueSessionResponse(BaseModel):
    session_id: str
    status: str 