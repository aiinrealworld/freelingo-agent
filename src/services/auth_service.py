import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from models.user import User

bearer_scheme = HTTPBearer()

# Initialize Firebase only once
if not firebase_admin._apps:
    creds_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if not creds_path:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_PATH environment variable is not set.")
    cred = credentials.Certificate(creds_path)
    firebase_admin.initialize_app(cred)


def verify_token(token: str) -> dict:
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")


def get_current_user(authorization=Depends(bearer_scheme)) -> User:
    token = authorization.credentials
    payload = verify_token(token)
    return User(user_id=payload["uid"], email=payload.get("email", ""))
