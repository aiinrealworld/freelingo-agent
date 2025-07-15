from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.dialogue_service import run_dialogue_turn

router = APIRouter()

class DialogueRequest(BaseModel):
    message: str
    user_id: str

class DialogueResponse(BaseModel):
    response: str

@router.post("/dialogue", response_model=DialogueResponse)
async def dialogue_endpoint(payload: DialogueRequest):
    print(f"Received from user {payload.user_id}: {payload.message}")
    ai_response = await run_dialogue_turn(user_id=payload.user_id, student_response=payload.message)
    return DialogueResponse(response=ai_response) 