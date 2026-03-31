import requests
import os
import json

def final_audit():
    base_url = "http://localhost:8005"
    print(f"--- STARTING FINAL AUDIT ON {base_url} ---")
    
    # 1. Health Check
    try:
        health = requests.get(f"{base_url}/health").json()
        print(f"✅ Health: {health}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return

    # 2. Tickets Check (Real Data)
    try:
        tickets = requests.get(f"{base_url}/tickets?limit=5").json()
        count = len(tickets.get("tickets", []))
        print(f"✅ Real Tickets Count: {count}")
        if count > 0:
            print(f"   Example Ticket: {tickets['tickets'][0]}")
    except Exception as e:
        print(f"❌ Tickets Fetch Failed: {e}")

    # 3. Form Submission (Exercise 1.3)
    try:
        form_payload = {
            "name": "Audit User",
            "email": "audit@example.com",
            "subject": "Final Audit Verification",
            "message": "This is a test from the final audit script."
        }
        res = requests.post(f"{base_url}/support/submit", json=form_payload)
        print(f"✅ Support Form: {res.status_code} - {res.json().get('ticket_id')}")
    except Exception as e:
        print(f"❌ Form Submission Failed: {e}")

    # 4. Agent Chat (Exercise 1.5)
    try:
        chat_payload = {
            "message": "How do I reset my password?",
            "channel": "web_form",
            "email": "audit@example.com"
        }
        res = requests.post(f"{base_url}/agent/chat", json=chat_payload)
        print(f"✅ Agent Chat: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"   AI Response: {data.get('response')[:50]}...")
            print(f"   Tools Used: {data.get('tools')}")
    except Exception as e:
        print(f"❌ Agent Chat Failed: {e}")

    # 5. Dashboard Metrics (Real Data)
    try:
        metrics = requests.get(f"{base_url}/metrics/channels").json()
        print(f"✅ Channel Metrics: {metrics}")
    except Exception as e:
        print(f"❌ Metrics Fetch Failed: {e}")

    print("--- FINAL AUDIT COMPLETE ---")

if __name__ == "__main__":
    final_audit()
