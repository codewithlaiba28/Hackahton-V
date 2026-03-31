import requests
import json

def verify_channels():
    base_url = "http://localhost:8005"
    print(f"--- VERIFYING CHANNEL RESPONSES ON {base_url} ---")
    
    # 1. WhatsApp Handler Verification
    print("\n[STEP 1: Testing WhatsApp Webhook]")
    whatsapp_payload = {
        "Body": "Hello from WhatsApp Audit!",
        "From": "whatsapp:+1234567890",
        "MessageSid": "SM_AUDIT_123",
        "ProfileName": "Audit User"
    }
    try:
        # Twilio sends form data, but our endpoint handles JSON if headers are set
        res = requests.post(f"{base_url}/webhook/whatsapp", json=whatsapp_payload)
        print(f"✅ WhatsApp Webhook Status: {res.status_code}")
        # Check backend logs for processing
    except Exception as e:
        print(f"❌ WhatsApp Webhook Failed: {e}")

    # 2. Gmail Handler Verification (Manual Trigger)
    print("\n[STEP 2: Testing Gmail Manual Poll]")
    try:
        # This will trigger a fetch and processing
        res = requests.get(f"{base_url}/webhook/gmail/poll?q=label:inbox")
        print(f"✅ Gmail Poll Status: {res.status_code}")
        data = res.json()
        print(f"   Messages Fetched: {data.get('total_fetched', 0)}")
        print(f"   Processed: {data.get('processed_count', 0)}")
    except Exception as e:
        print(f"❌ Gmail Poll Failed: {e}")

    # 3. CRM Integration Check
    print("\n[STEP 3: Checking Ticket Generation]")
    try:
        tickets = requests.get(f"{base_url}/tickets?limit=10").json()
        print(f"✅ Recent CRM Tickets: {[t['id'][:8] for t in tickets.get('tickets', [])]}")
    except Exception as e:
        print(f"❌ Ticket Audit Failed: {e}")

    print("\n--- CHANNEL VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_channels()
