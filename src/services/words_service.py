# src/services/words_service.py

from db.words import get_known_words, get_user_words
from typing import List

from models.words_model import WordSuggestion
from services.llm_service import suggest_new_words
from services.user_session_service import update_known_words_in_session, update_new_words_in_session

def fetch_known_words(user_id: str) -> List[str]:
    known_words = get_known_words(user_id)
    update_known_words_in_session(user_id=user_id, words=known_words)
    return known_words





async def suggest_new_words_for_user(user_id: str) -> WordSuggestion:
    known_words = fetch_known_words(user_id)
    new_words = await suggest_new_words(known_words)
    update_new_words_in_session(user_id=user_id, words=new_words.new_words)
    return new_words