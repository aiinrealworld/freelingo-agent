from typing import List, Tuple
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
) -> Tuple[str, List[ModelMessage]]:
    
    """
    Calls the dialogue_agent to generate the next AI message in French.

    Args:
        known_words (List[str]): Words the user already knows.
        conversation_history (List[dict]): List of previous turns. Each dict has 'speaker' and 'message'.

    Returns:
        str: The next AI message in French.
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
            # If agent already exists, print its system prompt
            print("[DEBUG] Dialogue Agent System Prompt (existing agent):")
            print(dialogue_agent.system_prompt)
        print("[DEBUG] Message History:")
        for i, msg in enumerate(dialogue_history):
            if hasattr(msg, 'parts'):
                if isinstance(msg, ModelResponse):
                    for part in msg.parts:
                        if isinstance(part, TextPart):
                            print(f"  [AI] {part.content}")
                else:
                    for part in msg.parts:
                        if isinstance(part, UserPromptPart):
                            print(f"  [User] {part.content}")
      
        result = await dialogue_agent.run(
            user_prompt=student_response,
            message_history=dialogue_history
        )
        print("[DEBUG] Dialogue Agent Response:")
        print(result.output)
        
        return result.output, result.all_messages()

    except Exception as e:
        raise RuntimeError(f"dialogue_agent failed: {e}")
