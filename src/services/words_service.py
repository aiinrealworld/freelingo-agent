# src/services/known_words_service.py

from db.known_words import get_known_words, add_known_words, replace_known_words, delete_known_word
from typing import List

from models.words_model import WordSuggestion
from services.llm_service import suggest_new_words
from services.user_session_service import update_known_words_in_session, update_new_words_in_session

def fetch_known_words(user_id: str) -> List[str]:
    known_words = get_known_words(user_id)
    update_known_words_in_session(user_id=user_id, words=known_words)
    return known_words

def update_known_words(user_id: str, words: List[str]) -> int:
    return replace_known_words(user_id, words)

def add_words_to_known(user_id: str, new_words: List[str]) -> int:
    return add_known_words(user_id, new_words)

def remove_known_word(user_id: str, word: str) -> None:
    return delete_known_word(user_id, word)

def suggest_new_words_for_user(user_id: str) -> WordSuggestion:
    known_words = fetch_known_words(user_id)
    new_words = suggest_new_words(known_words)
    update_new_words_in_session(user_id=user_id, words=new_words)
    return new_words