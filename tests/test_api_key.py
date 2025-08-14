"""Test API key setup and basic LangChain functionality."""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=== API KEY TEST ===")
print(f"Current working directory: {os.getcwd()}")

# Check environment
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
else:
    print("❌ No API key found in environment")
    print("Environment variables:")
    for key, value in os.environ.items():
        if 'OPENAI' in key or 'API' in key:
            print(f"  {key}: {value[:10]}..." if value else f"  {key}: (empty)")

# Test basic LangChain import
try:
    from langchain_openai import ChatOpenAI
    print("✅ LangChain import successful")

    # Test LLM initialization
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    print("✅ LLM initialization successful")

    # Test simple API call
    print("\n🤖 Testing simple API call...")
    response = llm.invoke("Say 'Hello, API test successful!' and nothing else.")
    print(f"✅ API Response: {response.content}")

except ImportError as e:
    print(f"❌ LangChain import failed: {e}")
except Exception as e:
    print(f"❌ API test failed: {e}")
    import traceback
    traceback.print_exc()
