import requests
import json

def test_chat():
    url = "http://localhost:8000/agent/chat"
    payload = {
        "message": "Verify the fix: How do I reset my password?",
        "channel": "web_form",
        "customer_id": "test-user-sync"
    }
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("--- AI Response ---")
            print(data.get("response"))
            print("--- Tools Used ---")
            print(data.get("tools"))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_chat()
