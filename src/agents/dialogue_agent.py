import logfire
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Dict, Any, List, Literal

from config import DIALOGUE_LLM_MODEL
from agents.agents_config import DIALOGUE_AGENT_PROMPT

# Configure logging
logfire.configure(send_to_logfire="if-token-present")

class VocabularyChallenge(BaseModel):
    description: str
    tags: List[Literal["low_overlap", "no_verbs", "no_question_words", "topic_mismatch", "short_vocab", "repetition_risk"]]

class RuleChecks(BaseModel):
    used_only_allowed_vocabulary: bool
    one_sentence: bool
    max_eight_words: bool
    no_corrections_or_translations: bool

class Rationale(BaseModel):
    reasoning_summary: str
    vocabulary_challenge: VocabularyChallenge
    rule_checks: RuleChecks

class AiReply(BaseModel):
    text: str
    word_count: int

class DialogueResponse(BaseModel):
    rationale: Rationale
    ai_reply: AiReply

def create_dialogue_agent(system_prompt: str) -> Agent:
    return Agent(
        model=DIALOGUE_LLM_MODEL,
        system_prompt=system_prompt,
        temperature=0.3,
        output_type=DialogueResponse,
        instrument=True,
    )