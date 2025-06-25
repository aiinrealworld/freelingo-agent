from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from models.user_session import UserSession
from pydantic_ai.messages import ModelMessage

# In-memory store (replace with Redis or Supabase later)
SESSION_STORE: Dict[str, "UserSession"] = {}


def get_session(user_id: str) -> UserSession:
    session = SESSION_STORE.get(user_id)
    if not session:
        session = UserSession(user_id=user_id)
        SESSION_STORE[user_id] = session
    return session


def update_known_words_in_session(user_id: str, words: List[str]) -> None:
    session = get_session(user_id)
    session.known_words = words
    session.updated_at = datetime.now(timezone.utc)


def update_new_words_in_session(user_id: str, words: List[str]) -> None:
    session = get_session(user_id)
    session.new_words = words
    session.updated_at = datetime.now(timezone.utc)


def update_dialogue_turn_in_session(user_id: str, dialogue_history: List[ModelMessage]) -> None:
    session = get_session(user_id)
    session.dialogue_history = dialogue_history
    session.updated_at = datetime.now(timezone.utc)


def get_dialogue_history_from_session(user_id: str) -> List[ModelMessage]:
    return get_session(user_id).dialogue_history


def clear_dialogue_in_session(user_id: str) -> None:
    session = get_session(user_id)
    session.dialogue_history = []
    session.updated_at = datetime.now(timezone.utc)
