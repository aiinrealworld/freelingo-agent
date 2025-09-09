from typing import List
from pydantic import BaseModel, Field


class ChainChecks(BaseModel):
    feedback_transcript_alignment: bool
    planner_feedback_incorporation: bool
    new_words_plan_alignment: bool
    overall_chain_coherence: bool


class Rationale(BaseModel):
    reasoning_summary: str
    chain_checks: ChainChecks


class RefereeAgentOutput(BaseModel):
    is_valid: bool
    violations: List[str]
    rationale: Rationale
