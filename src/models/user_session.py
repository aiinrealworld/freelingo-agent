from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pydantic_ai.messages import ModelMessage
from pydantic_ai import Agent

@dataclass
class UserSession:
    user_id: str
    known_words: List[str] = field(default_factory=list)
    dialogue_agent: Optional[Agent] = None
    dialogue_history: List[ModelMessage] = field(default_factory=list)
    last_agent_response: Optional[Dict[str, Any]] = None  # Store full agent response
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))