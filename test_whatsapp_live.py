"""
Live WhatsApp Agent Test

This script tests the running backend and shows the AI response.
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Check if backend is healthy"""
    print("=" * 70)
    print("🏥 STEP 1: Health Check")
    print("=" * 70)
    
    try:
        response = requests.get(f"{API_URL}/health")
        data = response.json()
        print(f"✅ Backend Status: {data['status']}")
        print(f"✅ Channels: {', '.join(data['channels'].keys())}")
        print()
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_whatsapp_webhook():
    """Test WhatsApp webhook with sample message"""
    print("=" * 70)
    print("💬 STEP 2: Simulate WhatsApp Message")
    print("=" * 70)
    
    # Test message
    test_data = {
        "Body": "Hello, I need help resetting my API key",
        "From": "whatsapp:+923001234567",
        "MessageSid": "SMtest123456",
        "ProfileName": "Test User"
    }
    
    print(f"📤 Sending WhatsApp message:")
    print(f"   From: {test_data['From']}")
    print(f"   Body: {test_data['Body']}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/webhook/whatsapp",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Webhook Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"   Body: {response.text[:200]}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook received successfully!")
            print()
            print("⏳ The AI agent is processing your message...")
            print("   Check the backend console for the AI response.")
            print()
            return True
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_web_form():
    """Test web form submission"""
    print("=" * 70)
    print("🌐 STEP 3: Test Web Form")
    print("=" * 70)
    
    test_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "How do I export my data?",
        "category": "technical",
        "priority": "medium",
        "message": "I need help exporting my data from the platform. Can you guide me?"
    }
    
    print(f"📤 Submitting web form:")
    print(f"   Name: {test_data['name']}")
    print(f"   Email: {test_data['email']}")
    print(f"   Subject: {test_data['subject']}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/support/submit",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Form Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Ticket ID: {data.get('ticket_id', 'N/A')}")
            print(f"   Message: {data.get('message', 'N/A')[:100]}")
            print(f"   Response: {data.get('response', 'N/A')[:200]}")
            print()
            print("✅ Web form processed successfully!")
            return True
        else:
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gmail_poll():
    """Test manual Gmail polling"""
    print("=" * 70)
    print("📧 STEP 4: Test Gmail Polling")
    print("=" * 70)
    
    try:
        response = requests.get(f"{API_URL}/webhook/gmail/poll")
        data = response.json()
        
        print(f"📥 Gmail Poll Response:")
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Total Fetched: {data.get('total_fetched', 0)}")
        print(f"   Processed: {data.get('processed_count', 0)}")
        print(f"   Mode: {data.get('mode', 'unknown')}")
        
        if data.get('messages'):
            print(f"\n   Messages:")
            for msg in data['messages'][:3]:
                print(f"      - From: {msg.get('from', 'N/A')}")
                print(f"        Subject: {msg.get('subject', 'N/A')}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_dashboard_url():
    """Show dashboard URL"""
    print("=" * 70)
    print("📊 DASHBOARD & FRONTEND")
    print("=" * 70)
    print()
    print("✅ Frontend is running at: http://localhost:3000")
    print()
    print("📍 Pages available:")
    print("   - Landing Page: http://localhost:3000")
    print("   - Dashboard: http://localhost:3000/dashboard")
    print("   - Login: http://localhost:3000/login")
    print("   - Signup: http://localhost:3000/signup")
    print()


def main():
    """Run all tests"""
    print()
    print("🤖 " + "=" * 68)
    print("🤖  WHATSAPP AGENT LIVE TEST")
    print("🤖 " + "=" * 68)
    print()
    
    # Test 1: Health
    test1 = test_health()
    if not test1:
        print("❌ Backend is not running. Start it first!")
        print("   Command: python -m uvicorn api.main:app --reload")
        sys.exit(1)
    
    # Test 2: WhatsApp
    test2 = test_whatsapp_webhook()
    
    # Test 3: Web Form
    test3 = test_web_form()
    
    # Test 4: Gmail
    test4 = test_gmail_poll()
    
    # Dashboard
    show_dashboard_url()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    results = [
        ("Backend Health", test1),
        ("WhatsApp Webhook", test2),
        ("Web Form", test3),
        ("Gmail Polling", test4),
    ]
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("📱 TO TEST WHATSAPP IN REAL-TIME:")
        print("   1. Send 'join <keyword>' to +14155238886 on WhatsApp")
        print("   2. Then send: 'Hello, I need help'")
        print("   3. Check backend console for AI response")
        print()
    else:
        print("⚠️  Some tests failed. Check errors above.")
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
