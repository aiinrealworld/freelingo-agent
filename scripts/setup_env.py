#!/usr/bin/env python3
"""
Setup environment variables for FreeLingo
"""

import os
import sys

def create_env_file():
    """Create .env file with template"""
    
    env_content = """# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_API_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# VAPI Configuration (for voice features)
VAPI_API_KEY=your_vapi_api_key_here
VAPI_ASSISTANT_ID=your_vapi_assistant_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Frontend URL
FRONTEND_BASE_URL=http://localhost:5174

# LLM Models
WORDS_LLM_MODEL=gpt-4o-mini
DIALOGUE_LLM_MODEL=gpt-4o-mini
FEEDBACK_LLM_MODEL=gpt-4o-mini

# Logging
LOGFIRE_TOKEN=your_logfire_token_here

# Google Services
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json

# Firebase Configuration
FIREBASE_PROJECT_ID=your_firebase_project_id_here
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/your/firebase-service-account.json
"""
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("\n📋 Next steps:")
    print("   1. Edit .env file with your actual values")
    print("   2. Get Supabase keys from: Supabase Dashboard > Settings > API")
    print("   3. Get Firebase config from: Firebase Console > Project Settings")
    print("   4. Run: python scripts/populate_custom_words.py --user-id YOUR_USER_ID")

if __name__ == "__main__":
    print("🚀 FreeLingo Environment Setup")
    print("=" * 40)
    
    create_env_file() 