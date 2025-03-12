#!/usr/bin/env python3
"""
Script to verify OpenAI API setup and environment configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from app.utils.openai_manager import OpenAIManager

def verify_env_file():
    """Verify .env file exists and contains required variables"""
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv(env_path)
    
    required_vars = ['OPENAI_API_KEY', 'OPENAI_MAX_TOKENS', 'OPENAI_DEFAULT_MODEL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment file check passed")
    return True

def verify_openai_key():
    """Verify OpenAI API key is valid"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        # Try a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        print("✅ OpenAI API key verification passed")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key verification failed: {str(e)}")
        return False

def verify_openai_manager():
    """Verify OpenAIManager initialization and functionality"""
    try:
        manager = OpenAIManager()
        # Try a simple API call
        response = manager.call_openai_with_retry(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            max_tokens=10
        )
        print("✅ OpenAIManager verification passed")
        return True
    except Exception as e:
        print(f"❌ OpenAIManager verification failed: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("\n🔍 Starting OpenAI setup verification...\n")
    
    success = all([
        verify_env_file(),
        verify_openai_key(),
        verify_openai_manager()
    ])
    
    print("\n" + "="*50)
    if success:
        print("✅ All verifications passed! OpenAI setup is correct.")
        sys.exit(0)
    else:
        print("❌ Some verifications failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main() 