import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print("\n--- API Key Check ---")

# 1. Check OpenAI
if not OPENAI_API_KEY:
    print("⚠️ No OpenAI API key set")
else:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.models.list()
        print(f"✅ OpenAI API key works. Found {len(response.data)} models.")
    except Exception as e:
        print(f"❌ OpenAI API key failed: {e}")

# 2. Check DeepSeek via OpenRouter
if not DEEPSEEK_API_KEY:
    print("⚠️ No DeepSeek API key set")
else:
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hello from API key test!"}],
            "max_tokens": 10
        }
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        if r.status_code == 200:
            print("✅ DeepSeek API key works.")
        else:
            print(f"❌ DeepSeek API key failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ DeepSeek API key error: {e}")
