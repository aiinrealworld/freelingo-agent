from freelingo_agent.services.user_session_service import (
    get_session, update_dialogue_turn_in_session, 
    store_agent_response_in_session, get_dialogue_history_from_session
)
from freelingo_agent.services.words_service import fetch_known_words
from freelingo_agent.services.llm_service import get_dialogue_response
from freelingo_agent.models.dialogue_model import DialogueResponse
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from typing import List, Dict, Any, Tuple

async def run_dialogue_turn(user_id: str, student_response: str) -> Tuple[str, Dict[str, Any]]:
    """
    Handles a single dialogue turn for the user.
    Fetches known words and dialogue history from session,
    calls LLM for the next AI message, and updates session.

    Returns:
        str: The AI's next French message (clean text for UI).
        Dict: Full agent response (for storage and feedback agent).
    """

    session = get_session(user_id)

    # Ensure known_words are in session
    if not session.known_words:
        session.known_words = fetch_known_words(user_id)

    known_words = session.known_words

    # Fetch history
    dialogue_history = get_dialogue_history_from_session(user_id)

    # Get next AI message
    ai_message, new_dialogue_history, full_response = await get_dialogue_response(
        user_id=user_id,
        known_words=known_words,
        student_response=student_response,
        dialogue_history=dialogue_history,
    )

    # Store the full agent response in session
    store_agent_response_in_session(user_id, full_response)

    # Append message to history
    update_dialogue_turn_in_session(user_id, new_dialogue_history)

    return ai_message, full_response

def extract_full_agent_response(result_output) -> Dict[str, Any]:
    """Extract the full agent response including rationale, rule_checks, etc."""
    if hasattr(result_output, '__dict__'):
        return result_output.__dict__
    elif hasattr(result_output, 'model_dump'):
        return result_output.model_dump()
    elif hasattr(result_output, 'dict'):
        return result_output.dict()
    else:
        return {"raw_response": str(result_output)}
