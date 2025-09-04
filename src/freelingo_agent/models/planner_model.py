from typing import List
from pydantic import BaseModel, Field


class PlannerAgentOutput(BaseModel):
    session_objectives: List[str]
    suggested_new_words: List[str]
    practice_strategies: List[str]
    conversation_prompts: List[str]
