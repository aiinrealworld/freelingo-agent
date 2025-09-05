from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class UsageExample(BaseModel):
    fr: str  # French sentence
    en: str  # English translation of the sentence

class WordSuggestion(BaseModel):
    new_words: List[str]
    usages: Dict[str, UsageExample]  # word -> usage object

# Single Word model for all operations
class Word(BaseModel):
    id: Optional[str] = None
    user_id: str
    word: str
    translation: str
    example: Optional[str] = None
    created_at: Optional[datetime] = None

class DialogueMessage(BaseModel):
    message: str
    user_id: str

class DialogueResponse(BaseModel):
    response: str
    suggested_words: List[str] = []
