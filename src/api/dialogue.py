from fastapi import APIRouter, Request, Depends, HTTPException, Query
from pydantic import BaseModel
from services.dialogue_service import run_dialogue_turn
from services.dialogue_session_service import save_dialogue_session_service, list_dialogue_sessions_service, get_dialogue_session_service
from models.dialogue_session import DialogueSessionRequest, DialogueSessionResponse
from models.user import User
from utils.firebase_auth import get_current_user_firebase
from typing import Any

router = APIRouter()

class DialogueRequest(BaseModel):
    message: str
    user_id: str

class DialogueResponse(BaseModel):
    response: str

@router.post("/dialogue", response_model=DialogueResponse)
async def dialogue_endpoint(payload: DialogueRequest):
    print(f"Received from user {payload.user_id}: {payload.message}")
    ai_response, full_response = await run_dialogue_turn(user_id=payload.user_id, student_response=payload.message)
    # UI only gets the clean text, full_response is available for storage if needed
    return DialogueResponse(response=ai_response)

@router.post("/dialogue-session", response_model=DialogueSessionResponse, status_code=201)
async def save_dialogue_session(
    session: DialogueSessionRequest,
    current_user: User = Depends(get_current_user_firebase)
):
    # Auth check
    if current_user.user_id != session.user_id:
        raise HTTPException(status_code=403, detail="Can only save sessions for yourself")
    try:
        session_id = save_dialogue_session_service(
            user_id=session.user_id,
            messages=[m.dict() for m in session.messages],
            started_at=session.started_at,
            ended_at=session.ended_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return DialogueSessionResponse(session_id=session_id, status="saved")

@router.get("/dialogue-sessions/{user_id}")
async def list_dialogue_sessions(user_id: str, current_user: User = Depends(get_current_user_firebase)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only list your own sessions")
    try:
        sessions = list_dialogue_sessions_service(user_id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialogue-session/{session_id}")
async def get_dialogue_session(session_id: str) -> Any:
    try:
        session = get_dialogue_session_service(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 