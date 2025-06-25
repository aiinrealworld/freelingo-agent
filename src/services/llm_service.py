from typing import List, Tuple
import json
from agents.words_agent import words_agent
from agents.dialogue_agent import dialogue_agent
from models.words_model import WordSuggestion
from pydantic_ai.messages import ModelMessage

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

        return WordSuggestion(**parsed_output)
    
    except Exception as e:
        raise RuntimeError(f"words_agent failed: {e}")


async def get_dialogue_response(
    known_words: List[str],
    new_words: List[str],
    student_response: str,
    dialogue_history: List[ModelMessage],
) -> Tuple[str, List[ModelMessage]]:
    
    """
    Calls the dialogue_agent to generate the next AI message in French.

    Args:
        known_words (List[str]): Words the user already knows.
        new_words (List[str]): 3 new words for this dialogue.
        conversation_history (List[dict]): List of previous turns. Each dict has 'speaker' and 'message'.

    Returns:
        str: The next AI message in French.
    """

    try:
        user_prompt = {
            "known_words": known_words,
            "new_words": new_words,
            "student_response": student_response
        }

        

        result = await dialogue_agent.run(
            user_prompt=user_prompt,
            message_history=dialogue_history
        )
        
        return result.output, result.all_messages()

    except Exception as e:
        raise RuntimeError(f"dialogue_agent failed: {e}")
