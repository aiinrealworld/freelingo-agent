from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

WORDS_LLM_MODEL = os.getenv("WORDS_LLM_MODEL")
DIALOGUE_LLM_MODEL = os.getenv("DIALOGUE_LLM_MODEL")
FEEDBACK_LLM_MODEL = os.getenv("FEEDBACK_LLM_MODEL")

LOGFIRE_TOKEN = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


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
    "GOOGLE_CREDS_PATH",
]

for var in required_vars:
    if not globals().get(var):
        raise RuntimeError(f"Missing required env var: {var}")