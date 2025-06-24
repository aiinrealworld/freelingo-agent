from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from models.user import User
from config import SUPABASE_URL
import httpx

bearer_scheme = HTTPBearer()
_JWKS_CACHE = None

async def get_current_user(authorization=Depends(bearer_scheme)) -> User:
    token = authorization.credentials
    try:
        payload = await verify_jwt(token)
        return User(user_id=payload["sub"], email=payload["email"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def verify_jwt(token: str) -> dict:
    global _JWKS_CACHE
    if not _JWKS_CACHE:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{SUPABASE_URL}/auth/v1/keys")
            res.raise_for_status()
            _JWKS_CACHE = res.json()
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = next((k for k in _JWKS_CACHE["keys"] if k["kid"] == unverified_header["kid"]), None)
        if not key:
            raise Exception("Unable to find matching JWK")
        return jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"JWT error: {e}")