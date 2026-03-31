import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load env from ROOT .env
load_dotenv('C:/Code-journy/Quator-4/Hackahton-V/.env')

async def verify_agent_chat():
    url = "http://localhost:8000/agent/chat"
    payload = {
        "message": "Verify the fix: How do I reset my password?",
        "channel": "web_form",
        "customer_id": "test-user-123"
    }
    
    print(f"Testing {url}...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("--- AI Response ---")
                print(data.get("response"))
                print("--- Tools Used ---")
                print(data.get("tools"))
                print("--- Conversation ID ---")
                print(data.get("conversation_id"))
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    # Note: This requires the backend to be running.
    # To run backend: 
    #   cd backend
    #   python -m uvicorn api.main:app --reload
    asyncio.run(verify_agent_chat())
