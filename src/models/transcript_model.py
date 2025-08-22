from pydantic import BaseModel
from typing import List, Literal
from models.dialogue_model import Rationale, AiReply

class UserTurn(BaseModel):
    text: str  # user's response (any language)

class AiTurn(BaseModel):
    rationale: Rationale
    ai_reply: AiReply

class TranscriptTurn(BaseModel):
    ai_turn: AiTurn
    user_turn: UserTurn

class Transcript(BaseModel):
    transcript: List[TranscriptTurn]
