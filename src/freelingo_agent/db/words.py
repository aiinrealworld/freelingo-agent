from supabase import Client
from typing import List, Optional
from freelingo_agent.models.words_model import WordResponse, WordCreate, WordUpdate
from freelingo_agent.db.supabase import supabase
import uuid
from datetime import datetime

def get_known_words(user_id: str) -> List[str]:
    """Get list of known words for backward compatibility"""
    response = supabase.table("words").select("word").eq("user_id", user_id).order("created_at", desc=True).execute()
    return [row["word"] for row in response.data]

def get_user_words(user_id: str) -> List[WordResponse]:
    """Get all words for a user with full details"""
    response = supabase.table("words").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    
    words = []
    for row in response.data:
        words.append(WordResponse(
            id=row["id"],
            user_id=row["user_id"],
            word=row["word"],
            translation=row["translation"],
            example=row.get("example"),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
        ))
    
    return words



def create_word(user_id: str, word_data: WordCreate) -> WordResponse:
    """Create a new word with full details"""
    db_data = {
        "user_id": user_id,
        "word": word_data.word,
        "translation": word_data.translation,
        "example": word_data.example
    }
    
    response = supabase.table("words").insert(db_data).execute()
    row = response.data[0]
    
    return WordResponse(
        id=row["id"],
        user_id=row["user_id"],
        word=row["word"],
        translation=row["translation"],
        example=row.get("example"),
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
    
    response = supabase.table("words").update(update_data).eq("id", word_id).execute()
    
    if not response.data:
        return None
    
    row = response.data[0]
    return WordResponse(
        id=row["id"],
        user_id=row["user_id"],
        word=row["word"],
        translation=row["translation"],
        example=row.get("example"),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    )







def delete_word(word_id: str) -> bool:
    """Delete a word by ID"""
    response = supabase.table("words").delete().eq("id", word_id).execute()
    return len(response.data) > 0