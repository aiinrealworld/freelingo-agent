from typing import List
import json
from agents.words_agent import words_agent
from models.words_model import WordSuggestion

from services.known_words_service import fetch_known_words
from models.words_model import WordSuggestion

def suggest_new_words_for_user(user_id: str) -> WordSuggestion:
    known_words = fetch_known_words(user_id)
    return suggest_new_words(known_words)


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
        print(f"response {result.output}")
        parsed_output = json.loads(result.output)

        return WordSuggestion(**parsed_output)
    
    except Exception as e:
        raise RuntimeError(f"words_agent failed: {e}")
