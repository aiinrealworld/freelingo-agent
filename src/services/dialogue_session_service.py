from db.dialogue_session import save_dialogue_session_db, list_dialogue_sessions_db, get_dialogue_session_db
from services.user_session_service import get_dialogue_history_from_session, get_agent_response_from_session
from models.transcript_model import Transcript, TranscriptTurn, AiTurn, UserTurn
from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Dict, Any

def save_dialogue_session_service(user_id: str, messages: List[dict] = None, started_at: Optional[str] = None, ended_at: Optional[str] = None) -> str:
    from datetime import datetime
    from uuid import uuid4
    from services.user_session_service import clear_dialogue_in_session
    
    # Construct the transcript from dialogue history
    transcript = construct_transcript_from_dialogue_history(user_id)
    
    # Convert transcript to dict for database storage
    transcript_dict = transcript.dict()
    
    session_id = str(uuid4())
    now = datetime.utcnow().isoformat() + 'Z'
    save_dialogue_session_db(
        session_id=session_id,
        user_id=user_id,
        messages=transcript_dict,  # Store the structured transcript
        started_at=started_at,
        ended_at=ended_at,
        created_at=now
    )
    
    # Clear the dialogue history after saving the session
    # This ensures that the next dialogue session starts fresh
    clear_dialogue_in_session(user_id)
    
    return session_id

def construct_transcript_from_dialogue_history(user_id: str) -> Transcript:
    """Construct a Transcript model from the dialogue history and agent responses"""
    from pydantic_ai.messages import UserPromptPart, TextPart, ModelResponse, ModelRequest, ToolCallPart, ToolReturnPart
    import json
    
    dialogue_history = get_dialogue_history_from_session(user_id)
    last_agent_response = get_agent_response_from_session(user_id)
    
    # If no dialogue history, return empty transcript
    if not dialogue_history:
        return Transcript(transcript=[])
    
    transcript_turns = []
    user_messages = []
    ai_messages = []
    agent_responses = []
    
    # First pass: collect all user and AI messages in order, along with their agent responses
    for i, msg in enumerate(dialogue_history):
        if isinstance(msg, ModelRequest):
            # User message
            for j, part in enumerate(msg.parts):
                if isinstance(part, UserPromptPart):
                    # Skip the first empty user message (UI trigger to start conversation)
                    if len(user_messages) == 0 and (not part.content or not part.content.strip()):
                        continue
                    else:
                        user_messages.append(part.content)
        elif isinstance(msg, ModelResponse):
            # AI message - check for TextPart, ToolCallPart, or ToolReturnPart
            for j, part in enumerate(msg.parts):
                if isinstance(part, TextPart):
                    ai_messages.append(part.content)
                    # For TextPart, we don't have structured agent response, so use fallback
                    agent_responses.append(None)
                elif isinstance(part, ToolCallPart):
                    # Extract AI text from the tool call if available
                    ai_text = None
                    agent_response = None
                    
                    if hasattr(part, 'content') and part.content:
                        ai_text = part.content
                    elif hasattr(part, 'tool_name') and part.tool_name:
                        # Use tool name as fallback
                        ai_text = f"[Tool: {part.tool_name}]"
                    
                    # Try to extract agent response from the tool call args
                    if hasattr(part, 'args') and part.args:
                        try:
                            args_data = json.loads(part.args)
                            if 'rationale' in args_data and 'ai_reply' in args_data:
                                agent_response = args_data
                        except (json.JSONDecodeError, KeyError):
                            pass
                    
                    ai_messages.append(ai_text)
                    agent_responses.append(agent_response)
                    
                elif isinstance(part, ToolReturnPart):
                    # Extract AI text from the tool return if available
                    if hasattr(part, 'content') and part.content:
                        ai_messages.append(part.content)
                        agent_responses.append(None)
    
    # If we have user messages but no AI messages from dialogue history, 
    # try to extract AI text from the last agent response
    if user_messages and not ai_messages and last_agent_response:
        if 'ai_reply' in last_agent_response and hasattr(last_agent_response['ai_reply'], 'text'):
            ai_text = last_agent_response['ai_reply'].text
            ai_messages.append(ai_text)
            agent_responses.append(last_agent_response)
    
    # Second pass: pair user and AI messages to create transcript turns
    # We need to handle the case where there might be an initial AI message without a user message
    min_length = min(len(user_messages), len(ai_messages))
    
    for i in range(min_length):
        user_text = user_messages[i]
        ai_text = ai_messages[i]
        agent_response = agent_responses[i] if i < len(agent_responses) else None
        
        # Create UserTurn
        user_turn = UserTurn(text=user_text)
        
        # Create AiTurn with the appropriate agent response
        if agent_response and 'rationale' in agent_response and 'ai_reply' in agent_response:
            ai_turn = AiTurn(
                rationale=agent_response['rationale'],
                ai_reply=agent_response['ai_reply']
            )
        elif last_agent_response and 'rationale' in last_agent_response and 'ai_reply' in last_agent_response:
            ai_turn = AiTurn(
                rationale=last_agent_response['rationale'],
                ai_reply=last_agent_response['ai_reply']
            )
        else:
            # Fallback if agent response is not properly structured
            from models.dialogue_model import Rationale, VocabularyChallenge, RuleChecks, AiReply
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
    
    return Transcript(transcript=transcript_turns)

def get_conversation_with_agent_responses(user_id: str) -> List[Dict[str, Any]]:
    """Get conversation history with full agent responses for database storage"""
    from pydantic_ai.messages import UserPromptPart, TextPart, ModelResponse
    from datetime import datetime
    
    dialogue_history = get_dialogue_history_from_session(user_id)
    last_agent_response = get_agent_response_from_session(user_id)
    
    conversation = []
    message_id = 1
    
    for msg in dialogue_history:
        if hasattr(msg, 'parts'):
            if isinstance(msg, ModelResponse):
                # AI message
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        conversation.append({
                            "id": str(message_id),
                            "text": part.content,
                            "sender": "ai",
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "agent_response": last_agent_response if message_id == len(dialogue_history) else None
                        })
                        message_id += 1
            else:
                # User message
                for part in msg.parts:
                    if isinstance(part, UserPromptPart):
                        conversation.append({
                            "id": str(message_id),
                            "text": part.content,
                            "sender": "user",
                            "timestamp": datetime.utcnow().isoformat() + 'Z',
                            "agent_response": None
                        })
                        message_id += 1
    
    return conversation

def list_dialogue_sessions_service(user_id: str):
    return list_dialogue_sessions_db(user_id)

def get_dialogue_session_service(session_id: str):
    session = get_dialogue_session_db(session_id)
    if not session:
        raise RuntimeError("Session not found")
    return session 