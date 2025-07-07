from supabase import Client
from typing import Optional
from models.words_model import UserProgress
from db.supabase import supabase
from datetime import datetime

def get_user_progress(user_id: str) -> UserProgress:
    """Get user learning progress"""
    # Get words count
    words_response = supabase.table("known_words").select("*").eq("user_id", user_id).execute()
    total_words = len(words_response.data)
    learned_words = len([w for w in words_response.data if w.get("learned", False)])
    
    # Get progress data
    progress_response = supabase.table("user_progress").select("*").eq("user_id", user_id).execute()
    
    if progress_response.data:
        progress_data = progress_response.data[0]
        dialogue_sessions = progress_data.get("dialogue_sessions", 0)
        streak_days = progress_data.get("streak_days", 0)
    else:
        # Create initial progress record
        progress_data = {
            "user_id": user_id,
            "dialogue_sessions": 0,
            "streak_days": 0
        }
        supabase.table("user_progress").insert(progress_data).execute()
        dialogue_sessions = 0
        streak_days = 0
    
    return UserProgress(
        total_words=total_words,
        learned_words=learned_words,
        dialogue_sessions=dialogue_sessions,
        streak_days=streak_days
    )

def increment_dialogue_sessions(user_id: str) -> None:
    """Increment dialogue sessions count"""
    # Try to update existing record
    response = supabase.table("user_progress").update({
        "dialogue_sessions": supabase.table("user_progress").select("dialogue_sessions").eq("user_id", user_id).execute().data[0]["dialogue_sessions"] + 1,
        "last_activity": datetime.now().isoformat()
    }).eq("user_id", user_id).execute()
    
    # If no record exists, create one
    if not response.data:
        progress_data = {
            "user_id": user_id,
            "dialogue_sessions": 1,
            "streak_days": 0,
            "last_activity": datetime.now().isoformat()
        }
        supabase.table("user_progress").insert(progress_data).execute()

def update_streak_days(user_id: str, streak_days: int) -> None:
    """Update user's streak days"""
    response = supabase.table("user_progress").update({
        "streak_days": streak_days,
        "last_activity": datetime.now().isoformat()
    }).eq("user_id", user_id).execute()
    
    # If no record exists, create one
    if not response.data:
        progress_data = {
            "user_id": user_id,
            "dialogue_sessions": 0,
            "streak_days": streak_days,
            "last_activity": datetime.now().isoformat()
        }
        supabase.table("user_progress").insert(progress_data).execute() 