from db.dialogue_session import save_dialogue_session_db, list_dialogue_sessions_db, get_dialogue_session_db
from services.user_session_service import get_dialogue_history_from_session, get_agent_response_from_session
from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Dict, Any

def save_dialogue_session_service(user_id: str, messages: List[dict], started_at: Optional[str] = None, ended_at: Optional[str] = None) -> str:
    from datetime import datetime
    from uuid import uuid4
    session_id = str(uuid4())
    now = datetime.utcnow().isoformat() + 'Z'
    save_dialogue_session_db(
        session_id=session_id,
        user_id=user_id,
        messages=messages,
        started_at=started_at,
        ended_at=ended_at,
        created_at=now
    )
    return session_id

def get_conversation_with_agent_responses(user_id: str) -> List[Dict[str, Any]]:
    """Get conversation history with full agent responses for database storage"""
    from pydantic_ai.messages import UserPromptPart, TextPart, ModelResponse
    from datetime import datetime
    
    dialogue_history = get_dialogue_history_from_session(user_id)
    last_agent_response = get_agent_response_from_session(user_id)
    
    conversation = []
    message_id = 1
    
    for msg in dialogue_history:
        if hasattr(msg, 'parts'):
            if isinstance(msg, ModelResponse):
                # AI message
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        conversation.append({
                            "id": str(message_id),
                            "text": part.content,
                            "sender": "ai",
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "agent_response": last_agent_response if message_id == len(dialogue_history) else None
                        })
                        message_id += 1
            else:
                # User message
                for part in msg.parts:
                    if isinstance(part, UserPromptPart):
                        conversation.append({
                            "id": str(message_id),
                            "text": part.content,
                            "sender": "user",
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "agent_response": None
                        })
                        message_id += 1
    
    return conversation

def list_dialogue_sessions_service(user_id: str):
    return list_dialogue_sessions_db(user_id)

def get_dialogue_session_service(session_id: str):
    session = get_dialogue_session_db(session_id)
    if not session:
        raise RuntimeError("Session not found")
    return session 