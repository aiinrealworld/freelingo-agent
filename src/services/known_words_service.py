# src/services/known_words_service.py

from db.known_words import get_known_words, add_known_words, replace_known_words, delete_known_word
from typing import List

def fetch_known_words(user_id: str) -> List[str]:
    return get_known_words(user_id)

def update_known_words(user_id: str, words: List[str]) -> int:
    return replace_known_words(user_id, words)

def add_words_to_known(user_id: str, new_words: List[str]) -> int:
    return add_known_words(user_id, new_words)

def remove_known_word(user_id: str, word: str) -> None:
    return delete_known_word(user_id, word)