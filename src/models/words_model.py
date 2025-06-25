from pydantic import BaseModel
from typing import List, Dict

class UsageExample(BaseModel):
    fr: str  # French sentence
    en: str  # English translation

class WordSuggestion(BaseModel):
    new_words: List[str]
    usages: Dict[str, UsageExample]  # word -> usage object
