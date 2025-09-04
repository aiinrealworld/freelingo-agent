from typing import List
from pydantic import BaseModel, Field


class RuleChecks(BaseModel):
    used_only_allowed_vocabulary: bool
    one_sentence: bool
    max_eight_words: bool
    no_corrections_or_translations: bool


class Rationale(BaseModel):
    reasoning_summary: str
    rule_checks: RuleChecks


class RefereeAgentOutput(BaseModel):
    is_valid: bool
    violations: List[str]
    rationale: Rationale
