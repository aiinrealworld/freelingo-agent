from pydantic import BaseModel
from typing import List, Literal

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
