from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any
from .feedback_model import FeedbackAgentOutput
from .words_model import WordSuggestion


class SessionSummary(BaseModel):
    total_exchanges: int
    vocabulary_used: int
    session_duration: Optional[str] = None

class EndSessionResponse(BaseModel):
    session_id: str
    status: str
    feedback: Optional[FeedbackAgentOutput] = None
    new_words: Optional[WordSuggestion] = None
    session_summary: Optional[SessionSummary] = None 