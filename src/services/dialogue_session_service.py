from db.dialogue_session import save_dialogue_session_db, list_dialogue_sessions_db, get_dialogue_session_db
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

def list_dialogue_sessions_service(user_id: str):
    return list_dialogue_sessions_db(user_id)

def get_dialogue_session_service(session_id: str):
    session = get_dialogue_session_db(session_id)
    if not session:
        raise RuntimeError("Session not found")
    return session 