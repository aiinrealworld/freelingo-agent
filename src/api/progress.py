from fastapi import APIRouter, HTTPException, Depends
from models.words_model import UserProgress
from db.progress import get_user_progress
from utils.firebase_auth import get_current_user_firebase
from models.user import User

router = APIRouter(tags=["progress"])

@router.get("/user/{user_id}/progress", response_model=UserProgress)
async def get_user_progress_endpoint(user_id: str, current_user: User = Depends(get_current_user_firebase)):
    """Get user learning progress"""
    # Verify the user is requesting their own progress
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only access your own progress")
    
    try:
        progress = get_user_progress(user_id)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}") 