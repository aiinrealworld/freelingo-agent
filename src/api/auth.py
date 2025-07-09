from fastapi import APIRouter, Depends
from services.auth_service import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=User)
def get_me(user: User = Depends(get_current_user)):
    return user