from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5174")

WORDS_LLM_MODEL = os.getenv("WORDS_LLM_MODEL")
DIALOGUE_LLM_MODEL = os.getenv("DIALOGUE_LLM_MODEL")
FEEDBACK_LLM_MODEL = os.getenv("FEEDBACK_LLM_MODEL")

LOGFIRE_TOKEN = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")

# Firebase configuration
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

# Set Google Application Credentials for Google Cloud services
if FIREBASE_SERVICE_ACCOUNT_PATH:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FIREBASE_SERVICE_ACCOUNT_PATH

required_vars = [
    "SUPABASE_URL",
    "SUPABASE_API_KEY",
    "VAPI_API_KEY",
    "VAPI_ASSISTANT_ID",
    "OPENAI_API_KEY",
    "WORDS_LLM_MODEL",
    "DIALOGUE_LLM_MODEL",
    "FEEDBACK_LLM_MODEL",
    "LOGFIRE_TOKEN",
    "FIREBASE_PROJECT_ID",
]

# Optional vars (for development)
optional_vars = [
    "FIREBASE_SERVICE_ACCOUNT_PATH",
]

for var in required_vars:
    if not globals().get(var):
        raise RuntimeError(f"Missing required env var: {var}")

# Check optional vars
for var in optional_vars:
    if not globals().get(var):
        print(f"⚠️  Optional env var not set: {var}")
        print("   This may affect Firebase Admin SDK initialization")