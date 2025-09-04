import pytest
from typing import List
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, SystemPromptPart, TextPart

from freelingo_agent.services.user_session_service import (
    get_session,
    get_dialogue_history_from_session,
)
from freelingo_agent.services.dialogue_service import run_dialogue_turn

@pytest.mark.integration
@pytest.mark.asyncio
async def test_run_dialogue_turn_fetches_known_words_and_returns_ai_response():

    TEST_USER_ID = "00000000-0000-0000-0000-000000000999"

    # Make sure session is clean
    session = get_session(TEST_USER_ID)
    session.known_words = []
    session.new_words = []
    session.dialogue_history = []

    # Act
    ai_response, full_response = await run_dialogue_turn(
        user_id=TEST_USER_ID, 
        student_response=""
    )

    print(f"Respone from dialogue_agent: {ai_response}")

    # Assert
    assert isinstance(ai_response, str)
    assert len(ai_response) > 0
    assert isinstance(full_response, dict)

    # Confirm conversation history updated
    history = get_dialogue_history_from_session(TEST_USER_ID)
    assert len(history) == 3  # System prompt + user input + AI response + tool return
    assert isinstance(history[0], ModelRequest)  # System/user prompt
    assert isinstance(history[1], ModelResponse)  # AI's generated message
    assert isinstance(history[2], ModelRequest)  # Tool return


from pydantic_ai.messages import ModelMessage
from freelingo_agent.services.user_session_service import (
    get_session,
    get_dialogue_history_from_session
)
from freelingo_agent.services.llm_service import get_dialogue_response

@pytest.mark.integration
@pytest.mark.asyncio
async def test_dialogue_turns_with_known_and_new_words_10_turns():
    
    TEST_USER_ID = "00000000-0000-0000-0000-000000000999"

    # Setup session
    session = get_session(TEST_USER_ID)
    session.new_words = ["manger", "jouer", "jardin"]
    session.dialogue_history = []

    # Simulated student responses using only allowed words
    student_responses = [
        "Je suis dans le jardin.",
        "Le chat veut jouer.",
        "Mon frère mange une orange.",
        "Elle est dans l'appartement.",
        "Tu veux un croissant ?"
    ]


    for student_response in student_responses:

        # Get AI message
        ai_message, new_history, full_response = await get_dialogue_response(
            user_id=TEST_USER_ID,
            known_words=session.known_words,
            student_response=student_response,
            dialogue_history=session.dialogue_history,
        )

        # Update history with AI response
        session.dialogue_history = new_history

    # Confirm conversation history updated
    history = get_dialogue_history_from_session(TEST_USER_ID)
    assert len(history) == 15  # 5 turns * 3 messages each (user input + AI response + tool return)

    assert isinstance(history[0], ModelRequest)  # System/user prompt
    assert isinstance(history[1], ModelResponse)  # AI's generated message

    print_message_contents(history)


def print_message_contents(history):
    for i, message in enumerate(history):
        print(f"\n[Turn {i}] Type: {type(message).__name__}")
        for part in message.parts:
            if isinstance(part, (UserPromptPart, SystemPromptPart, TextPart)):
                print("→", part.content)
