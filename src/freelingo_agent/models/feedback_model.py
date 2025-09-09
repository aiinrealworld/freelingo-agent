from typing import Dict, List
from pydantic import BaseModel, Field


class VocabExample(BaseModel):
    fr: str = Field(description="One level-appropriate example sentence in French.")
    en: str = Field(description="English translation of the French example.")


class FeedbackIssue(BaseModel):
    kind: str  # "grammar" | "word_choice" | "word_order"
    evidence: str
    fix_hint_fr: str
    fix_hint_en: str
    priority: int


class FeedbackAgentOutput(BaseModel):
    strengths: List[str]
    issues: List[FeedbackIssue]
    next_focus_areas: List[str]
    vocab_usage: Dict[str, VocabExample] = Field(default_factory=dict)


