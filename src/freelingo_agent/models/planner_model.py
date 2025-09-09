from typing import List
from pydantic import BaseModel, Field


class PlannerAgentOutput(BaseModel):
    session_objectives: List[str] = Field(description="High-level goals for the next session, phrased as short action-oriented statements", max_length=3)
    vocab_gaps: List[str] = Field(description="Specific vocabulary areas that need building to help conversation flow", max_length=3)
