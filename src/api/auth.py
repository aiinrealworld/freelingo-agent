from fastapi import APIRouter, Depends
from models.user import User
from utils.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=User)
def get_me(user: User = Depends(get_current_user)):
    return user