#!/usr/bin/env python
"""Test script for WhatsApp (Twilio) integration."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

from src.channels.whatsapp_handler import WhatsAppHandler
from src.channels.base import Channel, ChannelMessage


def test_handler_initialization():
    """Test WhatsApp handler initialization."""
    print("=" * 60)
    print("TEST 1: WhatsApp Handler Initialization")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    if handler.client:
        print("✓ Twilio client initialized successfully")
        print(f"  Account SID: {handler.account_sid[:10]}...")
        print(f"  From Number: {handler.from_number}")
        return True
    else:
        print("⚠️ Twilio client not initialized (running in mock mode)")
        print(f"  Account SID present: {bool(os.getenv('TWILIO_ACCOUNT_SID'))}")
        print(f"  Auth Token present: {bool(os.getenv('TWILIO_AUTH_TOKEN'))}")
        print(f"  WhatsApp Number: {handler.from_number}")
        return True  # Mock mode is OK for testing


def test_parse_webhook():
    """Test parsing Twilio webhook data."""
    print("\n" + "=" * 60)
    print("TEST 2: Parse WhatsApp Webhook")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Simulate Twilio webhook data
    test_webhook = {
        "Body": "Hello, I need help with my account",
        "From": "whatsapp:+923001234567",
        "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "ProfileName": "Test User",
        "WaId": "923001234567",
        "SmsMessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    }
    
    print(f"Input webhook data:")
    for key, value in test_webhook.items():
        print(f"  {key}: {value}")
    
    # Parse webhook
    message = handler.parse_webhook(test_webhook)
    
    print(f"\n✓ Parsed ChannelMessage:")
    print(f"  Channel: {message.channel}")
    print(f"  Content: {message.content}")
    print(f"  Customer Phone: {message.customer_phone}")
    print(f"  Customer Name: {message.customer_name}")
    print(f"  Message ID: {message.channel_message_id}")
    print(f"  Metadata: {message.metadata}")
    
    # Validate
    assert message.channel == Channel.WHATSAPP, "Channel should be WHATSAPP"
    assert message.content == "Hello, I need help with my account", "Content should match"
    assert message.customer_phone == "+923001234567", "Phone should be extracted"
    
    print("\n✓ Webhook parsing test passed!")
    return True


async def test_send_response():
    """Test sending WhatsApp response."""
    print("\n" + "=" * 60)
    print("TEST 3: Send WhatsApp Response")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Test phone number (use your test number)
    test_phone = os.getenv("TEST_WHATSAPP_PHONE", "+923001234567")
    
    print(f"Sending test WhatsApp message to: {test_phone}")
    
    success = await handler.send_response(
        customer_phone=test_phone,
        body="🤖 This is a test message from Customer Success FTE!\n\nIf you receive this, the WhatsApp integration is working correctly.\n\nBest regards,\nAI Customer Success Team"
    )
    
    if success:
        print("✓ WhatsApp message sent successfully!")
    else:
        print("❌ Failed to send WhatsApp message. Check logs for details.")
    
    return success


async def test_send_formatted_response():
    """Test sending formatted WhatsApp response."""
    print("\n" + "=" * 60)
    print("TEST 4: Send Formatted Response")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    test_phone = os.getenv("TEST_WHATSAPP_PHONE", "+923001234567")
    
    # Simulate a customer support response
    response_body = """Hi there! 👋

Thank you for contacting support.

Based on your inquiry, here's what I found:

✅ Your account is active
✅ All services are running normally
✅ No issues detected

If you need further assistance, please don't hesitate to ask!

Best regards,
Customer Success FTE"""

    print(f"Sending formatted response to: {test_phone}")
    
    success = await handler.send_response(
        customer_phone=test_phone,
        body=response_body
    )
    
    if success:
        print("✓ Formatted response sent!")
    else:
        print("❌ Failed to send formatted response")
    
    return success


async def test_webhook_to_response():
    """Test full flow: webhook parsing -> response."""
    print("\n" + "=" * 60)
    print("TEST 5: Full Flow - Webhook to Response")
    print("=" * 60)
    
    handler = WhatsAppHandler()
    
    # Simulate incoming webhook
    webhook_data = {
        "Body": "What are your business hours?",
        "From": "whatsapp:+923001234567",
        "MessageSid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "ProfileName": "John Doe"
    }
    
    print("Step 1: Parse incoming webhook...")
    message = handler.parse_webhook(webhook_data)
    print(f"  ✓ Parsed message from {message.customer_name}")
    
    print("\nStep 2: Generate and send response...")
    response = f"Hi {message.customer_name}! Our business hours are Monday-Friday, 9 AM - 6 PM PKT. How can I help you today?"
    
    success = await handler.send_response(
        customer_phone=message.customer_phone,
        body=response
    )
    
    if success:
        print("  ✓ Response sent successfully!")
    else:
        print("  ❌ Failed to send response")
    
    return success


async def main():
    """Run all WhatsApp tests."""
    print("\n🧪 WHATSAPP (TWILIO) INTEGRATION TEST SUITE\n")
    
    results = []
    
    # Test 1: Initialization
    results.append(("Handler Initialization", test_handler_initialization()))
    
    # Test 2: Webhook parsing
    results.append(("Webhook Parsing", test_parse_webhook()))
    
    # Test 3: Send response
    results.append(("Send Response", await test_send_response()))
    
    # Test 4: Formatted response
    results.append(("Formatted Response", await test_send_formatted_response()))
    
    # Test 5: Full flow
    results.append(("Full Flow", await test_webhook_to_response()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All WhatsApp integration tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
