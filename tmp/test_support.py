import requests

def test_support():
    url = "http://localhost:8000/support/submit"
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Issue",
        "message": "This is a test issue for verification."
    }
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("--- Success Response ---")
            print(response.json())
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_support()
