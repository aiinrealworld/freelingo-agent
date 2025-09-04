from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from models.user import User
from utils.firebase_admin import verify_firebase_token
from typing import Optional

bearer_scheme = HTTPBearer()

async def get_current_user_firebase(authorization=Depends(bearer_scheme)) -> User:
    """Get current user from Firebase JWT token using Admin SDK"""
    token = authorization.credentials
    try:
        # Use Firebase Admin SDK to verify token
        user_info = verify_firebase_token(token)
        
        return User(
            user_id=user_info["uid"],  # Firebase UID
            email=user_info.get("email", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from Firebase token without verification (for testing)"""
    try:
        # Use Firebase Admin SDK for verification
        user_info = verify_firebase_token(token)
        return user_info["uid"]
    except Exception:
        return None

# For backward compatibility, you can use either auth system
get_current_user = get_current_user_firebase 