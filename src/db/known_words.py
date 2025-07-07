from supabase import Client
from typing import List, Optional
from models.words_model import WordResponse, WordCreate, WordUpdate
from db.supabase import supabase
import uuid
from datetime import datetime

def get_known_words(user_id: str) -> List[str]:
    """Get list of known words for backward compatibility"""
    response = supabase.table("known_words").select("word").eq("user_id", user_id).execute()
    return [row["word"] for row in response.data]

def get_user_words(user_id: str) -> List[WordResponse]:
    """Get all words for a user with full details"""
    response = supabase.table("known_words").select("*").eq("user_id", user_id).execute()
    
    words = []
    for row in response.data:
        words.append(WordResponse(
            id=row["id"],
            user_id=row["user_id"],
            word=row["word"],
            translation=row["translation"],
            example=row.get("example"),
            learned=row.get("learned", False),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        ))
    
    return words

def add_known_words(user_id: str, words: List[str]) -> int:
    """Add words for backward compatibility (creates with basic translation)"""
    count = 0
    for word in words:
        # Create basic translation (word itself as translation)
        word_data = {
            "user_id": user_id,
            "word": word,
            "translation": word,  # Basic fallback
            "learned": False
        }
        supabase.table("known_words").insert(word_data).execute()
        count += 1
    return count

def create_word(user_id: str, word_data: WordCreate) -> WordResponse:
    """Create a new word with full details"""
    db_data = {
        "user_id": user_id,
        "word": word_data.word,
        "translation": word_data.translation,
        "example": word_data.example,
        "learned": False
    }
    
    response = supabase.table("known_words").insert(db_data).execute()
    row = response.data[0]
    
    return WordResponse(
        id=row["id"],
        user_id=row["user_id"],
        word=row["word"],
        translation=row["translation"],
        example=row.get("example"),
        learned=row.get("learned", False),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    )

def update_word(word_id: str, updates: WordUpdate) -> Optional[WordResponse]:
    """Update a word"""
    update_data = {}
    if updates.word is not None:
        update_data["word"] = updates.word
    if updates.translation is not None:
        update_data["translation"] = updates.translation
    if updates.example is not None:
        update_data["example"] = updates.example
    
    if not update_data:
        return None
    
    response = supabase.table("known_words").update(update_data).eq("id", word_id).execute()
    
    if not response.data:
        return None
    
    row = response.data[0]
    return WordResponse(
        id=row["id"],
        user_id=row["user_id"],
        word=row["word"],
        translation=row["translation"],
        example=row.get("example"),
        learned=row.get("learned", False),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    )

def mark_word_learned(word_id: str) -> Optional[WordResponse]:
    """Mark a word as learned"""
    response = supabase.table("known_words").update({"learned": True}).eq("id", word_id).execute()
    
    if not response.data:
        return None
    
    row = response.data[0]
    return WordResponse(
        id=row["id"],
        user_id=row["user_id"],
        word=row["word"],
        translation=row["translation"],
        example=row.get("example"),
        learned=row.get("learned", False),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    )

def replace_known_words(user_id: str, words: List[str]) -> None:
    """Replace all known words for a user (backward compatibility)"""
    # Delete existing words
    supabase.table("known_words").delete().eq("user_id", user_id).execute()
    
    # Add new words
    for word in words:
        word_data = {
            "user_id": user_id,
            "word": word,
            "translation": word,  # Basic fallback
            "learned": False
        }
        supabase.table("known_words").insert(word_data).execute()

def delete_known_word(user_id: str, word: str) -> None:
    """Delete a word by word text (backward compatibility)"""
    supabase.table("known_words").delete().eq("user_id", user_id).eq("word", word).execute()

def delete_word(word_id: str) -> bool:
    """Delete a word by ID"""
    response = supabase.table("known_words").delete().eq("id", word_id).execute()
    return len(response.data) > 0