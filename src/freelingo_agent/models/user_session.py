from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from pydantic_ai.messages import ModelMessage
from freelingo_agent.models.words_model import Word

class UserSession(BaseModel):
    user_id: str
    known_words: List[Word] = Field(default_factory=list)
    new_words: List[str] = Field(default_factory=list)  # Add new_words field
    dialogue_agent: Optional[Any] = None  # Using Any to avoid type annotation issues
    dialogue_history: List[ModelMessage] = Field(default_factory=list)
    last_agent_response: Optional[Dict[str, Any]] = None  # Store full agent response
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        arbitrary_types_allowed = True