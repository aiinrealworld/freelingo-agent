from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pydantic_ai.messages import ModelMessage
from pydantic_ai import Agent

@dataclass
class UserSession:
    user_id: str
    known_words: List[str] = field(default_factory=list)
    new_words: List[str] = field(default_factory=list)
    dialogue_agent: Optional[Agent] = None
    dialogue_history: List[ModelMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))