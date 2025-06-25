from services.user_session_service import (
    get_session,
    get_dialogue_history_from_session,
    update_dialogue_turn_in_session,
)
from services.words_service import fetch_known_words
from services.llm_service import get_dialogue_response


async def run_dialogue_turn(user_id: str, student_response: str) -> str:
    """
    Handles a single dialogue turn for the user.
    Fetches known/new words and dialogue history from session,
    calls LLM for the next AI message, and updates session.

    Returns:
        str: The AI's next French message.
    """

    session = get_session(user_id)

    # Ensure known_words are in session
    if not session.known_words:
        session.known_words = fetch_known_words(user_id)

    # Use empty new_words if not present
    known_words = session.known_words
    new_words = session.new_words or []

    # Fetch history
    dialogue_history = get_dialogue_history_from_session(user_id)

    # Stop if dialogue is already complete
    # if len(conversation_history) >= 10:
    #    raise ValueError("Dialogue already complete (10 turns).")

    # Get next AI message
    ai_message, new_dialogue_history = await get_dialogue_response(
        user_id=user_id,
        known_words=known_words,
        new_words=new_words,
        student_response=student_response,
        dialogue_history=dialogue_history,
    )

    # Append message to history
    update_dialogue_turn_in_session(user_id, new_dialogue_history)

    return ai_message
