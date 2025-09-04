from freelingo_agent.db.supabase import supabase
from typing import List, Optional, Dict, Any

def save_dialogue_session_db(session_id: str, user_id: str, messages: List[Dict[str, Any]], started_at: Optional[str] = None, ended_at: Optional[str] = None, created_at: Optional[str] = None) -> bool:
    data = {
        "id": session_id,
        "user_id": user_id,
        "messages": messages,
        "started_at": started_at,
        "ended_at": ended_at,
        "created_at": created_at,
    }
    response = supabase.table("dialogue_sessions").insert(data).execute()
    if not response.data:
        raise RuntimeError("Failed to save session")
    return True

def list_dialogue_sessions_db(user_id: str) -> List[Dict[str, Any]]:
    response = supabase.table("dialogue_sessions").select("id, started_at, ended_at, messages").eq("user_id", user_id).order("started_at", desc=True).execute()
    sessions = []
    for row in response.data:
        sessions.append({
            "session_id": row["id"],
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
            "message_count": len(row.get("messages", [])),
        })
    return sessions

def get_dialogue_session_db(session_id: str) -> Optional[Dict[str, Any]]:
    response = supabase.table("dialogue_sessions").select("*").eq("id", session_id).single().execute()
    if not response.data:
        return None
    row = response.data
    return {
        "session_id": row["id"],
        "user_id": row["user_id"],
        "messages": row["messages"],
        "started_at": row.get("started_at"),
        "ended_at": row.get("ended_at"),
    } 