from typing import List
from pydantic import BaseModel, Field


class PlannerAgentOutput(BaseModel):
    session_objectives: List[str]
    practice_strategies: List[str]
