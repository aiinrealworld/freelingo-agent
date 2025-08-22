#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.dialogue_session_service import construct_transcript_from_dialogue_history
from services.user_session_service import get_session, clear_dialogue_in_session, update_dialogue_turn_in_session, store_agent_response_in_session
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

def test_transcript_construction():
    """Test transcript construction with manually populated dialogue history"""
    user_id = "test_user_123"
    
    # Clear any existing session
    clear_dialogue_in_session(user_id)
    
    # Get the session
    session = get_session(user_id)
    print(f"Initial session for user {user_id}: {session}")
    
    # Manually create dialogue history
    print("\n=== Creating dialogue history ===")
    
    # Create a user message
    user_message = ModelRequest(
        parts=[UserPromptPart(content="bonjour")]
    )
    
    # Create an AI message
    ai_message = ModelResponse(
        parts=[TextPart(content="bonjour")]
    )
    
    # Create dialogue history
    dialogue_history = [user_message, ai_message]
    
    # Update the session with dialogue history
    update_dialogue_turn_in_session(user_id, dialogue_history)
    
    # Create a mock agent response
    mock_agent_response = {
        "rationale": {
            "reasoning_summary": "Student greeted; respond with greeting.",
            "vocabulary_challenge": {
                "description": "No challenge; straightforward greeting.",
                "tags": []
            },
            "rule_checks": {
                "used_only_allowed_vocabulary": True,
                "one_sentence": True,
                "max_eight_words": True,
                "no_corrections_or_translations": True
            }
        },
        "ai_reply": {
            "text": "bonjour",
            "word_count": 1
        }
    }
    
    # Store the agent response
    store_agent_response_in_session(user_id, mock_agent_response)
    
    # Check the session after populating
    session = get_session(user_id)
    print(f"\nSession after populating:")
    print(f"  Dialogue history length: {len(session.dialogue_history)}")
    print(f"  Last agent response: {session.last_agent_response}")
    
    # Try to construct transcript
    print("\n=== Constructing transcript ===")
    try:
        transcript = construct_transcript_from_dialogue_history(user_id)
        print(f"Transcript: {transcript}")
        print(f"Transcript dict: {transcript.dict()}")
        
        # Check if transcript has content
        if transcript.transcript:
            print(f"✓ Transcript has {len(transcript.transcript)} turns")
            for i, turn in enumerate(transcript.transcript):
                print(f"  Turn {i+1}:")
                print(f"    User: {turn.user_turn.text}")
                print(f"    AI: {turn.ai_turn.ai_reply.text}")
        else:
            print("✗ Transcript is empty")
            
    except Exception as e:
        print(f"Error constructing transcript: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript_construction()
