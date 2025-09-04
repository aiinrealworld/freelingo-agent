from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import logfire

from freelingo_agent.services.graph_workflow_service import GraphWorkflowService
from freelingo_agent.models.graph_state import GraphState
from freelingo_agent.models.user_session import UserSession

# Configure logging
logfire.configure(send_to_logfire="if-token-present")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["workflow"])
workflow_service = GraphWorkflowService()


@router.post("/start-session")
async def start_session(user_id: str, session_goals: List[str] = None) -> Dict[str, Any]:
    """Start a new learning session"""
    try:
        logger.info(f"Starting new session for user {user_id}")
        
        initial_state = await workflow_service.start_session(user_id, session_goals)
        
        return {
            "success": True,
            "user_id": initial_state.user_id,
            "current_agent": initial_state.current_agent,

            "session_goals": initial_state.session_goals,
            "dialogue_history_length": len(initial_state.user_session.dialogue_history) if initial_state.user_session else 0
        }
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/process-dialogue")
async def process_dialogue(user_id: str, message: str, session_id: str = None) -> Dict[str, Any]:
    """Process a user message in dialogue mode"""
    try:
        logger.info(f"Processing dialogue for user {user_id}")
        
        # Create a simple state for dialogue processing
        # In a real implementation, you'd retrieve the state from storage
        user_session = UserSession(user_id=user_id)
        state = GraphState(
            user_id=user_id,
            user_session=user_session,
            session_goals=["Practice conversation", "Learn new vocabulary"]
        )
        
        response = await workflow_service.process_dialogue(state, message)
        
        return {
            "success": True,
            "response": response,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error processing dialogue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process dialogue: {str(e)}")


@router.post("/end-session")
async def end_session(user_id: str, session_id: str) -> Dict[str, Any]:
    """End the current dialogue session and start the feedback flow"""
    try:
        logger.info(f"Ending session {session_id} for user {user_id}")
        
        # Create a state with the session to end
        user_session = UserSession(user_id=user_id)
        state = GraphState(
            user_id=user_id,
            user_session=user_session,
            session_goals=["Practice conversation", "Learn new vocabulary"]
        )
        
        # Run the end session workflow
        final_state = await workflow_service.end_session(state)
        
        return {
            "success": True,
            "session_ended": True,
            "final_agent": final_state.current_agent,
            "feedback": final_state.last_feedback.model_dump() if final_state.last_feedback else None,
            "plan": final_state.last_plan.model_dump() if final_state.last_plan else None,
            "new_words": final_state.last_words.model_dump() if final_state.last_words else None,
            "referee_decision": final_state.last_referee_decision.model_dump() if final_state.last_referee_decision else None
        }
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


@router.get("/workflow-status/{user_id}")
async def get_workflow_status(user_id: str) -> Dict[str, Any]:
    """Get the current workflow status for a user"""
    try:
        logger.info(f"Getting workflow status for user {user_id}")
        
        # In a real implementation, you'd retrieve the state from storage
        # For now, return a placeholder status
        return {
            "success": True,
            "user_id": user_id,
            "current_agent": "DIALOGUE",

            "session_active": True
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


@router.post("/test-workflow")
async def test_workflow(user_id: str = "test_user") -> Dict[str, Any]:
    """Test the complete workflow from start to finish"""
    try:
        logger.info(f"Testing complete workflow for user {user_id}")
        
        # Start session
        initial_state = await workflow_service.start_session(user_id, ["Test learning goals"])
        
        # End session to trigger the workflow
        final_state = await workflow_service.end_session(initial_state)
        
        return {
            "success": True,
            "test_completed": True,
            "initial_state": {
                "current_agent": initial_state.current_agent,
                "dialogue_history_length": len(initial_state.user_session.dialogue_history) if initial_state.user_session else 0
            },
            "final_state": {
                "current_agent": final_state.current_agent,
                "feedback_generated": final_state.last_feedback is not None,
                "plan_generated": final_state.last_plan is not None,
                "words_generated": final_state.last_words is not None,
                "referee_decision": final_state.last_referee_decision is not None
            }
        }
    except Exception as e:
        logger.error(f"Error testing workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test workflow: {str(e)}")

