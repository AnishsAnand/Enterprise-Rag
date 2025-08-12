import os
import requests
import openai
from dotenv import load_dotenv
load_dotenv()

# Load from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # DeepSeek on OpenRouter

def test_openai():
    if not OPENAI_API_KEY:
        print("⚠️ No OpenAI API key set")
        return
    try:
        openai.api_key = OPENAI_API_KEY
        resp = openai.models.list()
        print(f"✅ OpenAI key valid. Found {len(resp.data)} models.")
    except Exception as e:
        print(f"❌ OpenAI API key failed: {e}")

def test_openrouter_deepseek():
    if not OPENROUTER_API_KEY:
        print("⚠️ No OpenRouter API key set")
        return
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if resp.status_code == 200:
            print("✅ DeepSeek key valid (via OpenRouter).")
        else:
            print(f"❌ DeepSeek API key failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ DeepSeek API request error: {e}")

if __name__ == "__main__":
    print("🔍 Testing OpenAI...")
    test_openai()
    print("\n🔍 Testing DeepSeek (OpenRouter)...")
    test_openrouter_deepseek()
