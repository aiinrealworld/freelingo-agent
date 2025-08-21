from typing import List, Tuple, Dict, Any
import json
from agents.words_agent import words_agent
from agents.agents_config import DIALOGUE_AGENT_PROMPT
from agents.dialogue_agent import create_dialogue_agent
from models.words_model import WordSuggestion
from pydantic_ai.messages import ModelMessage, UserPromptPart, ModelResponse, TextPart
from services.user_session_service import get_session

async def suggest_new_words(known_words: List[str]) -> WordSuggestion:
    """
    Calls the words_agent to suggest 3 new words that pair well with known words.

    Args:
        known_words (List[str]): The user's known French words.

    Returns:
        WordSuggestion: new words + example sentences
    """

    try:
        result = await words_agent.run(
            user_prompt = f"List of known words: {known_words}"
        )
        parsed_output = json.loads(result.output)
        print(parsed_output)
        
        return WordSuggestion(**parsed_output)
    
    except Exception as e:
        raise RuntimeError(f"words_agent failed: {e}")


async def get_dialogue_response(
    user_id: str,
    known_words: List[str],
    student_response: str,
    dialogue_history: List[ModelMessage],
) -> Tuple[str, List[ModelMessage], Dict[str, Any]]:
    """
    Calls the dialogue_agent to generate the next AI message in French.

    Args:
        known_words (List[str]): Words the user already knows.
        dialogue_history (List[ModelMessage]): List of previous ModelMessage objects.

    Returns:
        str: The next AI message in French (clean text for UI).
        List[ModelMessage]: Updated dialogue history with new turn.
        Dict: Full agent response (for storage and feedback agent).
    """

    try:
        session = get_session(user_id=user_id)
        dialogue_agent = session.dialogue_agent

        if dialogue_agent is None:
            updated_dialogue_agent_prompt = DIALOGUE_AGENT_PROMPT.format(
                known_words=json.dumps(known_words, ensure_ascii=False)
            )
            print("[DEBUG] Dialogue Agent System Prompt:")
            print(updated_dialogue_agent_prompt)
            dialogue_agent = create_dialogue_agent(updated_dialogue_agent_prompt)
            session.dialogue_agent = dialogue_agent
        else:
            print("[DEBUG] Dialogue Agent System Prompt (existing agent):")
            print(dialogue_agent.system_prompt)
        
        print("[DEBUG] Message History:")
        for i, msg in enumerate(dialogue_history):
            print(f"  [{i}] {msg}")
      
        result = await dialogue_agent.run(
            user_prompt=student_response,
            message_history=dialogue_history
        )
        print("[DEBUG] Dialogue Agent Response:")
        print(result.output)
        
        # Extract the actual reply text from the structured response
        if hasattr(result.output, 'ai_reply') and hasattr(result.output.ai_reply, 'text'):
            ai_message = result.output.ai_reply.text
        else:
            # Fallback: try to use the output directly if it's a string
            ai_message = str(result.output)
        
        # Extract full response for storage
        full_response = extract_full_agent_response(result.output)
        
        return ai_message, result.all_messages(), full_response

    except Exception as e:
        raise RuntimeError(f"dialogue_agent failed: {e}")

def extract_full_agent_response(result_output) -> Dict[str, Any]:
    """Extract the full agent response including rationale, rule_checks, etc."""
    if hasattr(result_output, '__dict__'):
        return result_output.__dict__
    elif hasattr(result_output, 'dict'):
        return result_output.dict()
    else:
        return {"raw_response": str(result_output)}
