#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import only the models and transcript construction logic
from models.transcript_model import Transcript, TranscriptTurn, AiTurn, UserTurn
from models.dialogue_model import Rationale, VocabularyChallenge, RuleChecks, AiReply
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

def test_transcript_construction_logic():
    """Test the transcript construction logic directly"""
    print("=== Testing Transcript Construction Logic ===")
    
    # Create sample dialogue history
    user_message = ModelRequest(
        parts=[UserPromptPart(content="bonjour")]
    )
    
    ai_message = ModelResponse(
        parts=[TextPart(content="bonjour")]
    )
    
    dialogue_history = [user_message, ai_message]
    
    # Create sample agent response
    last_agent_response = {
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
    
    print(f"Dialogue history length: {len(dialogue_history)}")
    print(f"Agent response: {last_agent_response}")
    
    # Manually construct transcript using the same logic
    transcript_turns = []
    user_messages = []
    ai_messages = []
    
    # First pass: collect all user and AI messages in order
    for msg in dialogue_history:
        if isinstance(msg, ModelRequest):
            # User message
            for part in msg.parts:
                if isinstance(part, UserPromptPart):
                    user_messages.append(part.content)
        elif isinstance(msg, ModelResponse):
            # AI message
            for part in msg.parts:
                if isinstance(part, TextPart):
                    ai_messages.append(part.content)
    
    print(f"Found {len(user_messages)} user messages: {user_messages}")
    print(f"Found {len(ai_messages)} AI messages: {ai_messages}")
    
    # Second pass: pair user and AI messages to create transcript turns
    min_length = min(len(user_messages), len(ai_messages))
    
    for i in range(min_length):
        user_text = user_messages[i]
        ai_text = ai_messages[i]
        
        print(f"Creating transcript turn {i+1}: user='{user_text}', ai='{ai_text}'")
        
        # Create UserTurn
        user_turn = UserTurn(text=user_text)
        
        # Create AiTurn with the agent response
        if last_agent_response and 'rationale' in last_agent_response and 'ai_reply' in last_agent_response:
            ai_turn = AiTurn(
                rationale=last_agent_response['rationale'],
                ai_reply=last_agent_response['ai_reply']
            )
        else:
            # Fallback
            ai_turn = AiTurn(
                rationale=Rationale(
                    reasoning_summary="No rationale available",
                    vocabulary_challenge=VocabularyChallenge(
                        description="No challenge description",
                        tags=[]
                    ),
                    rule_checks=RuleChecks(
                        used_only_allowed_vocabulary=False,
                        one_sentence=False,
                        max_eight_words=False,
                        no_corrections_or_translations=False
                    )
                ),
                ai_reply=AiReply(
                    text=ai_text,
                    word_count=len(ai_text.split())
                )
            )
        
        # Create TranscriptTurn
        transcript_turns.append(TranscriptTurn(
            ai_turn=ai_turn,
            user_turn=user_turn
        ))
    
    # Create final transcript
    transcript = Transcript(transcript=transcript_turns)
    
    print(f"\n=== Results ===")
    print(f"Created {len(transcript_turns)} transcript turns")
    print(f"Transcript: {transcript}")
    print(f"Transcript dict: {transcript.dict()}")
    
    # Check if transcript has content
    if transcript.transcript:
        print(f"✓ Transcript has {len(transcript.transcript)} turns")
        for i, turn in enumerate(transcript.transcript):
            print(f"  Turn {i+1}:")
            print(f"    User: {turn.user_turn.text}")
            print(f"    AI: {turn.ai_turn.ai_reply.text}")
            print(f"    Rationale: {turn.ai_turn.rationale.reasoning_summary}")
    else:
        print("✗ Transcript is empty")

if __name__ == "__main__":
    test_transcript_construction_logic()
