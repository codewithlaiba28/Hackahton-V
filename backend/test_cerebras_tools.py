import os
import httpx
from dotenv import load_dotenv

load_dotenv()

key = "csk-2jw8xvmwmv32tfyvyectnmwpxdvp4ckfr66tdwp83r336324"
url = "https://api.cerebras.ai/v1/chat/completions"

def test_cerebras_with_tools():
    print(f"Testing Cerebras with key: {key[:10]}...")
    payload = {
        "model": "llama3.1-8b",
        "messages": [{"role": "user", "content": "What is the weather?"}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"]
                    }
                }
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cerebras_with_tools()
