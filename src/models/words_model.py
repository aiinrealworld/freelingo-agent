from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class UsageExample(BaseModel):
    translation: str  # English translation of the word
    fr: str  # French sentence
    en: str  # English translation of the sentence

class WordSuggestion(BaseModel):
    new_words: List[str]
    usages: Dict[str, UsageExample]  # word -> usage object

# New models for React UI compatibility
class WordCreate(BaseModel):
    word: str
    translation: str
    example: Optional[str] = None
    user_id: str

class WordResponse(WordCreate):
    id: str
    user_id: str
    created_at: datetime

class WordUpdate(BaseModel):
    word: Optional[str] = None
    translation: Optional[str] = None
    example: Optional[str] = None

class DialogueMessage(BaseModel):
    message: str
    user_id: str

class DialogueResponse(BaseModel):
    response: str
    suggested_words: List[str] = []

class UserProgress(BaseModel):
    total_words: int
    learned_words: int
    dialogue_sessions: int
    streak_days: int
