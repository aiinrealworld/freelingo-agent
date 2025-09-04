from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from .dialogue_model import DialogueResponse
from .feedback_model import FeedbackAgentOutput
from .planner_model import PlannerAgentOutput
from .words_model import WordSuggestion
from .referee_model import RefereeAgentOutput
from .user_session import UserSession
from .dialogue_session import DialogueSessionRequest


class GraphState(BaseModel):
    """State for the LangGraph workflow - integrates with existing UserSession"""
    # User and session info (using existing models)
    user_id: str
    user_session: UserSession  # Your existing UserSession
    dialogue_session: Optional[DialogueSessionRequest] = None
    
    # Current workflow state
    current_agent: Literal["DIALOGUE", "FEEDBACK", "PLANNER", "NEW_WORDS", "REFEREE"] = "DIALOGUE"
    
    # Agent outputs
    last_dialogue_response: Optional[DialogueResponse] = None
    last_feedback: Optional[FeedbackAgentOutput] = None
    last_plan: Optional[PlannerAgentOutput] = None
    last_words: Optional[WordSuggestion] = None
    last_referee_decision: Optional[RefereeAgentOutput] = None
    
    # Workflow control
    should_continue: bool = True
    next_agent: Optional[Literal["PLANNER", "NEW_WORDS", "FEEDBACK", "END"]] = None
    
    # Context for agents (derived from existing session data)
    conversation_context: str = ""
    learning_focus: List[str] = Field(default_factory=list)
    session_goals: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class AgentTransition(BaseModel):
    """Defines how agents transition between each other"""
    from_agent: str
    to_agent: str
    condition: str
    description: str

