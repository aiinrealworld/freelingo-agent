from db.supabase import supabase
from typing import List

KNOWN_WORDS_TABLE = "known_words_test"

def get_known_words(user_id: str) -> List[str]:
    res = supabase.from_(KNOWN_WORDS_TABLE).select("word").eq("user_id", user_id).execute()
    return [item["word"] for item in res.data or []]

def add_known_words(user_id: str, words: List[str]) -> int:
    rows = [{"user_id": user_id, "word": word} for word in words]
    supabase.from_(KNOWN_WORDS_TABLE).insert(rows).execute()
    return len(rows)

def replace_known_words(user_id: str, words: List[str]) -> None:
    supabase.from_(KNOWN_WORDS_TABLE).delete().eq("user_id", user_id).execute()
    add_known_words(user_id, words)

def delete_known_word(user_id: str, word: str) -> None:
    supabase.from_(KNOWN_WORDS_TABLE).delete().eq("user_id", user_id).eq("word", word).execute()