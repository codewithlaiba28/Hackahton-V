"""
Test WhatsApp Reply Functionality

This script tests if the WhatsApp handler correctly:
1. Parses incoming webhook messages
2. Sends reply messages via Twilio
3. Handles errors properly

Usage:
    python test_whatsapp_reply.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.channels.whatsapp_handler import WhatsAppHandler


def test_handler_initialization():
    """Test 1: Handler initialization"""
    print("=" * 60)
    print("TEST 1: WhatsApp Handler Initialization")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    if handler.from_number:
        print(f"✅ WhatsApp Number Configured: {handler.from_number}")
    else:
        print("❌ WhatsApp Number NOT configured")
        return False
    
    if handler.client:
        print("✅ Twilio Client Initialized")
    else:
        print("⚠️  Twilio Client in MOCK mode (credentials invalid/missing)")
    
    print()
    return True


def test_webhook_parsing():
    """Test 2: Webhook parsing"""
    print("=" * 60)
    print("TEST 2: WhatsApp Webhook Parsing")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Simulate Twilio webhook payload
    test_webhook = {
        "Body": "Hello, I need help with my API key",
        "From": "whatsapp:+923001234567",
        "MessageSid": "SMtest123456789",
        "ProfileName": "Test User"
    }
    
    try:
        msg = handler.parse_webhook(test_webhook)
        print(f"✅ Webhook Parsed Successfully")
        print(f"   - Customer Phone: {msg.customer_phone}")
        print(f"   - Customer Name: {msg.customer_name}")
        print(f"   - Content: {msg.content[:50]}...")
        print(f"   - Channel Message ID: {msg.channel_message_id}")
        print()
        return True
    except Exception as e:
        print(f"❌ Webhook Parsing Failed: {e}")
        print()
        return False


def test_invalid_webhook():
    """Test 3: Invalid webhook (SMS attempt)"""
    print("=" * 60)
    print("TEST 3: SMS Rejection (WhatsApp Only)")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Simulate SMS webhook (should be rejected)
    sms_webhook = {
        "Body": "Test SMS",
        "From": "+923001234567",  # No whatsapp: prefix
        "MessageSid": "SMtest123"
    }
    
    try:
        msg = handler.parse_webhook(sms_webhook)
        print(f"❌ SMS was NOT rejected (should have been)")
        print()
        return False
    except ValueError as e:
        print(f"✅ SMS Correctly Rejected: {e}")
        print()
        return True
    except Exception as e:
        print(f"⚠️  Unexpected Error: {e}")
        print()
        return False


async def test_send_message():
    """Test 4: Send message"""
    print("=" * 60)
    print("TEST 4: Send WhatsApp Message")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    test_phone = "+923001234567"
    test_body = "This is a test message from Customer Success FTE. How can I help you today?"
    
    try:
        result = await handler.send_message(test_phone, test_body)
        
        if result:
            print(f"✅ Message Send: SUCCESS")
            print(f"   - To: {test_phone}")
            print(f"   - Body: {test_body[:50]}...")
        else:
            print(f"❌ Message Send: FAILED")
        
        print()
        return result
    except Exception as e:
        print(f"❌ Message Send Error: {e}")
        print()
        return False


async def test_full_pipeline():
    """Test 5: Full pipeline simulation"""
    print("=" * 60)
    print("TEST 5: Full Pipeline (Webhook → Parse → Reply)")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Step 1: Simulate incoming webhook
    webhook = {
        "Body": "Hi, I'm having trouble logging in",
        "From": "whatsapp:+923001234567",
        "MessageSid": "SMtest999",
        "ProfileName": "John Doe"
    }
    
    print("Step 1: Parse incoming webhook...")
    msg = handler.parse_webhook(webhook)
    print(f"   ✅ Parsed: {msg.customer_name} sent '{msg.content}'")
    
    # Step 2: Simulate AI response
    ai_response = "Hello! I'd be happy to help you with your login issue. Can you tell me what error message you're seeing?"
    print(f"\nStep 2: AI Response Generated ({len(ai_response)} chars)")
    
    # Step 3: Send reply
    print("\nStep 3: Sending reply via WhatsApp...")
    result = await handler.send_message(msg.customer_phone, ai_response)
    
    if result:
        print(f"   ✅ Reply sent successfully")
    else:
        print(f"   ❌ Reply failed")
    
    print()
    return result


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 WHATSAPP REPLY FUNCTIONALITY TEST SUITE")
    print("=" * 60 + "\n")
    
    # Test 1: Initialization
    test1 = test_handler_initialization()
    
    # Test 2: Webhook parsing
    test2 = test_webhook_parsing()
    
    # Test 3: SMS rejection
    test3 = test_invalid_webhook()
    
    # Test 4: Send message
    test4 = await test_send_message()
    
    # Test 5: Full pipeline
    test5 = await test_full_pipeline()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    results = [
        ("Handler Initialization", test1),
        ("Webhook Parsing", test2),
        ("SMS Rejection", test3),
        ("Send Message", test4),
        ("Full Pipeline", test5),
    ]
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WhatsApp integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
