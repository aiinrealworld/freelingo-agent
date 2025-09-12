from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from freelingo_agent.services.dialogue_service import run_dialogue_turn
from freelingo_agent.services.dialogue_session_service import save_dialogue_session_service, list_dialogue_sessions_service, get_dialogue_session_service, get_conversation_with_agent_responses
from freelingo_agent.services.graph_workflow_service import GraphWorkflowService
from freelingo_agent.models.dialogue_session import EndSessionResponse, SessionSummary
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
    ai_response, full_response = await run_dialogue_turn(user_id=payload.user_id, student_response=payload.message)
    # UI only gets the clean text, full_response is available for storage if needed
    return DialogueResponse(response=ai_response)


@router.post("/dialogue-session/end/{user_id}", response_model=EndSessionResponse, status_code=201)
async def save_end_dialogue_session(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """End the dialogue session and return feedback with new words"""
    # Auth check
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only save sessions for yourself")
    
    try:
        # Check if there's dialogue history to save
        dialogue_history = get_dialogue_history_from_session(user_id)
        
        if not dialogue_history:
            raise HTTPException(status_code=400, detail="No conversation to save")
        
        # Get session data BEFORE saving (since save clears the session)
        from freelingo_agent.models.graph_state import GraphState
        from freelingo_agent.models.user_session import UserSession
        from freelingo_agent.services.user_session_service import get_session
        from freelingo_agent.services.words_service import fetch_known_words
        from freelingo_agent.services.dialogue_session_service import construct_transcript_from_dialogue_history
        
        # Get current user session with dialogue history and known words BEFORE saving
        current_session = get_session(user_id)
        known_words = fetch_known_words(user_id)
        
        # Construct transcript BEFORE saving (since save clears the session)
        transcript = construct_transcript_from_dialogue_history(user_id)
        
        # Create enriched UserSession for workflow
        enriched_session = UserSession(
            user_id=user_id,
            known_words=known_words,
            dialogue_history=current_session.dialogue_history,
            last_agent_response=current_session.last_agent_response,
            created_at=current_session.created_at,
            updated_at=current_session.updated_at
        )
        
        # Save the session (this constructs transcript from session and saves it)
        now = datetime.utcnow().isoformat()
        session_start_time = current_session.created_at.isoformat() if current_session.created_at else now
        session_id = save_dialogue_session_service(
            user_id=user_id,
            started_at=session_start_time,  # Use actual session creation time
            ended_at=now
        )
        
        # Log session completion with transcript summary
        print(f"\n🎯 DIALOGUE SESSION ENDED")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        print(f"   Duration: {session_start_time} → {now}")
        print(f"   Transcript Summary:")
        if transcript and transcript.transcript:
            print(f"   - Total turns: {len(transcript.transcript)}")
            for i, turn in enumerate(transcript.transcript, 1):
                user_text = turn.user_turn.text[:50] + "..." if len(turn.user_turn.text) > 50 else turn.user_turn.text
                ai_text = turn.ai_turn.ai_reply.text[:50] + "..." if len(turn.ai_turn.ai_reply.text) > 50 else turn.ai_turn.ai_reply.text
                print(f"     Turn {i}: User: \"{user_text}\" | AI: \"{ai_text}\"")
        else:
            print(f"   - No transcript available")
        print(f"   Vocabulary used: {len(known_words)} words")
        print(f"   Status: Session saved successfully\n")
        
        # Trigger workflow with the transcript we constructed BEFORE saving
        state = GraphState(
            user_id=user_id,
            user_session=enriched_session,
            transcript=transcript
        )
        
        # Run workflow and capture results
        feedback = None
        new_words = None
        
        try:
            final_state = await workflow_service.trigger_feedback_loop(state)
            feedback = final_state.last_feedback
            new_words = final_state.last_words
        except Exception as workflow_error:
            # Log the workflow error but don't fail the entire request
            print(f"Workflow execution failed: {workflow_error}")
            # Continue with session saved but no feedback
            pass
        
        # Create session summary
        session_summary = SessionSummary(
            total_exchanges=len(dialogue_history),
            vocabulary_used=len(known_words) if known_words else 0,
            session_duration=None  # Could be enhanced to calculate actual duration
        )
        
        # Return enriched response with workflow results (or None if workflow failed)
        return EndSessionResponse(
            session_id=session_id,
            status="saved",
            feedback=feedback,
            new_words=new_words,
            session_summary=session_summary
        )
        
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