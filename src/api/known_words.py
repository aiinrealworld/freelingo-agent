from fastapi import APIRouter, Depends
from models.known_words import KnownWordsList
from utils.auth import get_current_user
from models.user import User
from db.known_words import get_known_words, add_known_words, replace_known_words, delete_known_word

router = APIRouter(prefix="/known-words", tags=["known_words"])

@router.get("/", response_model=KnownWordsList)
def list_known_words(user: User = Depends(get_current_user)):
    words = get_known_words(user.user_id)
    return KnownWordsList(words=words)

@router.post("/")
def add_words(payload: KnownWordsList, user: User = Depends(get_current_user)):
    count = add_known_words(user.user_id, payload.words)
    return {"success": True, "added": count}

@router.put("/")
def replace_words(payload: KnownWordsList, user: User = Depends(get_current_user)):
    replace_known_words(user.user_id, payload.words)
    return {"success": True, "updated_count": len(payload.words)}

@router.delete("/")
def delete_word(word: str, user: User = Depends(get_current_user)):
    delete_known_word(user.user_id, word)
    return {"success": True}