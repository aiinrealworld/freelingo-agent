import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException
from typing import Optional

# Initialize Firebase Admin SDK
def initialize_firebase_admin():
    """Initialize Firebase Admin SDK with service account"""
    try:
        # Check if already initialized
        if not firebase_admin._apps:
            # Get service account path from environment
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            
            if service_account_path and os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for development)
                firebase_admin.initialize_app()
                
        print("✅ Firebase Admin SDK initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
        raise

def verify_firebase_token(token: str) -> dict:
    """Verify Firebase ID token and return user info"""
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        
        # Extract user information
        user_info = {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email", ""),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name", ""),
            "picture": decoded_token.get("picture", "")
        }
        
        return user_info
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

def get_user_by_uid(uid: str) -> Optional[dict]:
    """Get user information by Firebase UID"""
    try:
        user_record = auth.get_user(uid)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "email_verified": user_record.email_verified,
            "display_name": user_record.display_name,
            "photo_url": user_record.photo_url,
            "disabled": user_record.disabled
        }
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting user by UID: {e}")
        return None

def create_user_if_not_exists(uid: str, email: str = None) -> bool:
    """Create user record in Supabase if it doesn't exist"""
    try:
        # Check if user exists in Firebase
        user_record = auth.get_user(uid)
        
        # If user exists in Firebase, ensure they exist in Supabase
        # This is handled by the database operations
        return True
        
    except auth.UserNotFoundError:
        # User doesn't exist in Firebase
        return False
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False

# Initialize on module import
try:
    initialize_firebase_admin()
except Exception as e:
    print(f"Warning: Firebase Admin SDK initialization failed: {e}")
    print("You may need to set FIREBASE_SERVICE_ACCOUNT_PATH environment variable") 