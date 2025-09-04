#!/usr/bin/env python3

import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from freelingo_agent.services.dialogue_service import run_dialogue_turn
from freelingo_agent.services.dialogue_session_service import save_dialogue_session_service, construct_transcript_from_dialogue_history
from freelingo_agent.services.user_session_service import get_session, clear_dialogue_in_session

async def test_transcript_with_conversation():
    """Test transcript construction with an actual conversation"""
    user_id = "test_user_123"
    
    # Clear any existing session
    clear_dialogue_in_session(user_id)
    
    # Get the session
    session = get_session(user_id)
    print(f"Initial session for user {user_id}: {session}")
    
    # Simulate a dialogue turn to populate the history
    print("\n=== Simulating dialogue turn ===")
    try:
        ai_response, full_response = await run_dialogue_turn(
            user_id=user_id, 
            student_response="bonjour"
        )
        print(f"AI Response: {ai_response}")
        print(f"Full Response: {full_response}")
    except Exception as e:
        print(f"Error in dialogue turn: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Check the session after dialogue turn
    session = get_session(user_id)
    print(f"\nSession after dialogue turn:")
    print(f"  Dialogue history length: {len(session.dialogue_history)}")
    print(f"  Last agent response: {session.last_agent_response}")
    
    # Try to construct transcript
    print("\n=== Constructing transcript ===")
    try:
        transcript = construct_transcript_from_dialogue_history(user_id)
        print(f"Transcript: {transcript}")
        print(f"Transcript dict: {transcript.dict()}")
    except Exception as e:
        print(f"Error constructing transcript: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save the session
    print("\n=== Saving session ===")
    try:
        session_id = save_dialogue_session_service(
            user_id=user_id,
            started_at=None,
            ended_at="2024-01-01T00:00:00Z"
        )
        print(f"Session saved with ID: {session_id}")
    except Exception as e:
        print(f"Error saving session: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_transcript_with_conversation())
