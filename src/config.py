from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

required_vars = [
    "SUPABASE_URL",
    "SUPABASE_API_KEY",
    "VAPI_API_KEY",
    "VAPI_ASSISTANT_ID",
    "OPENAI_API_KEY",
]

for var in required_vars:
    if not globals().get(var):
        raise RuntimeError(f"Missing required env var: {var}")