from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from freelingo_agent.services.dialogue_service import run_dialogue_turn
from freelingo_agent.services.dialogue_session_service import save_dialogue_session_service, list_dialogue_sessions_service, get_dialogue_session_service, get_conversation_with_agent_responses
from freelingo_agent.services.graph_workflow_service import GraphWorkflowService
from freelingo_agent.models.dialogue_session import DialogueSessionRequest, DialogueSessionResponse
from freelingo_agent.models.user import User
from freelingo_agent.services.auth_service import get_current_user
from freelingo_agent.services.user_session_service import get_dialogue_history_from_session
from typing import Any
from datetime import datetime

router = APIRouter()
workflow_service = GraphWorkflowService()

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
    current_user: User = Depends(get_current_user)
):
    # Auth check
    if current_user.user_id != session.user_id:
        raise HTTPException(status_code=403, detail="Can only save sessions for yourself")
    try:
        session_id = save_dialogue_session_service(
            user_id=session.user_id,
            started_at=session.started_at,
            ended_at=session.ended_at
        )
        # Trigger workflow after successful save
        from freelingo_agent.models.graph_state import GraphState
        from freelingo_agent.models.user_session import UserSession
        from freelingo_agent.services.user_session_service import get_session
        from freelingo_agent.services.words_service import fetch_known_words
        from freelingo_agent.services.dialogue_session_service import construct_transcript_from_dialogue_history
        
        # Get current user session with dialogue history and known words
        current_session = get_session(session.user_id)
        known_words = fetch_known_words(session.user_id)
        
        # Create enriched UserSession for workflow
        enriched_session = UserSession(
            user_id=session.user_id,
            known_words=known_words,
            dialogue_history=current_session.dialogue_history,
            last_agent_response=current_session.last_agent_response,
            created_at=current_session.created_at,
            updated_at=current_session.updated_at
        )
        
        # Construct transcript once for the workflow
        transcript = construct_transcript_from_dialogue_history(session.user_id)
        
        state = GraphState(
            user_id=session.user_id,
            user_session=enriched_session,
            transcript=transcript
        )
        await workflow_service.trigger_feedback_loop(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return DialogueSessionResponse(session_id=session_id, status="saved")

@router.post("/dialogue-session/current/{user_id}", response_model=DialogueSessionResponse, status_code=201)
async def save_current_dialogue_session(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Save the current dialogue session with structured transcript"""
    # Auth check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only save sessions for yourself")
    
    try:
        # Check if there's dialogue history to save
        dialogue_history = get_dialogue_history_from_session(user_id)
        
        if not dialogue_history:
            raise HTTPException(status_code=400, detail="No conversation to save")
        
        session_id = save_dialogue_session_service(
            user_id=user_id,
            started_at=None,  # Could be enhanced to track session start time
            ended_at=datetime.utcnow().isoformat() + 'Z'
        )
        # Trigger workflow after saving current session
        from freelingo_agent.models.graph_state import GraphState
        from freelingo_agent.models.user_session import UserSession
        from freelingo_agent.services.user_session_service import get_session
        from freelingo_agent.services.words_service import fetch_known_words
        from freelingo_agent.services.dialogue_session_service import construct_transcript_from_dialogue_history
        
        # Get current user session with dialogue history and known words
        current_session = get_session(user_id)
        known_words = fetch_known_words(user_id)
        
        # Create enriched UserSession for workflow
        enriched_session = UserSession(
            user_id=user_id,
            known_words=known_words,
            dialogue_history=current_session.dialogue_history,
            last_agent_response=current_session.last_agent_response,
            created_at=current_session.created_at,
            updated_at=current_session.updated_at
        )
        
        # Construct transcript once for the workflow
        transcript = construct_transcript_from_dialogue_history(user_id)
        
        state = GraphState(
            user_id=user_id,
            user_session=enriched_session,
            transcript=transcript
        )
        await workflow_service.trigger_feedback_loop(state)
        
        return DialogueSessionResponse(session_id=session_id, status="saved")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialogue-sessions/{user_id}")
async def list_dialogue_sessions(user_id: str, current_user: User = Depends(get_current_user)):
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