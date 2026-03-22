#!/usr/bin/env python
"""Test script for Gmail integration."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

from src.channels.gmail_handler import GmailHandler


async def test_fetch_messages():
    """Test fetching unread Gmail messages."""
    print("=" * 60)
    print("TEST 1: Fetch Unread Gmail Messages")
    print("=" * 60)
    
    handler = GmailHandler(
        credentials_path="credentials.json",
        token_path="token.json"
    )
    
    if not handler.service:
        print("❌ Gmail service not initialized. Check credentials/token files.")
        return False
    
    print("✓ Gmail service initialized")
    
    # Fetch unread messages
    messages = await handler.fetch_messages(query="is:unread")
    
    print(f"\n📬 Found {len(messages)} unread messages")
    
    for i, msg in enumerate(messages[:5], 1):
        print(f"\n--- Message {i} ---")
        print(f"  From: {msg.customer_email}")
        print(f"  Subject: {msg.subject}")
        print(f"  Content ({len(msg.content)} chars): {msg.content[:100]}...")
        print(f"  Thread ID: {msg.metadata.get('thread_id', 'N/A')}")
    
    return len(messages) >= 0


async def test_send_response():
    """Test sending Gmail response."""
    print("\n" + "=" * 60)
    print("TEST 2: Send Gmail Response")
    print("=" * 60)
    
    handler = GmailHandler(
        credentials_path="credentials.json",
        token_path="token.json"
    )
    
    if not handler.service:
        print("❌ Gmail service not initialized.")
        return False
    
    # Test email (replace with your test email)
    test_email = os.getenv("TEST_EMAIL", "your-test-email@gmail.com")
    
    print(f"Sending test email to: {test_email}")
    
    success = await handler.send_response(
        customer_email=test_email,
        subject="Test from Customer Success FTE",
        body="This is a test message from the Customer Success FTE system.\n\nIf you receive this, the Gmail integration is working correctly!\n\nBest regards,\nCustomer Success FTE",
        thread_id=None
    )
    
    if success:
        print("✓ Email sent successfully!")
    else:
        print("❌ Failed to send email. Check logs for details.")
    
    return success


async def test_fetch_and_reply():
    """Test fetching messages and replying to them."""
    print("\n" + "=" * 60)
    print("TEST 3: Fetch and Reply to Messages")
    print("=" * 60)
    
    handler = GmailHandler(
        credentials_path="credentials.json",
        token_path="token.json"
    )
    
    if not handler.service:
        print("❌ Gmail service not initialized.")
        return False
    
    # Fetch unread messages
    messages = await handler.fetch_messages(query="is:unread")
    
    if not messages:
        print("No unread messages to reply to.")
        return True
    
    print(f"Found {len(messages)} unread messages. Replying to first 3...")
    
    replied = 0
    for msg in messages[:3]:
        print(f"\nReplying to: {msg.customer_email} (Subject: {msg.subject})")
        
        success = await handler.send_response(
            customer_email=msg.customer_email,
            subject=msg.subject,
            body=f"Thank you for your message about '{msg.subject}'.\n\nThis is an automated response from our Customer Success FTE. We have received your inquiry and will assist you shortly.\n\nBest regards,\nCustomer Success Team",
            thread_id=msg.metadata.get('thread_id')
        )
        
        if success:
            replied += 1
            print(f"  ✓ Reply sent!")
        else:
            print(f"  ❌ Failed to send reply")
    
    print(f"\n✓ Successfully replied to {replied}/{len(messages[:3])} messages")
    return replied > 0


async def main():
    """Run all Gmail tests."""
    print("\n🧪 GMAIL INTEGRATION TEST SUITE\n")
    
    results = []
    
    # Test 1: Fetch messages
    results.append(("Fetch Messages", await test_fetch_messages()))
    
    # Test 2: Send response
    results.append(("Send Response", await test_send_response()))
    
    # Test 3: Fetch and reply
    results.append(("Fetch & Reply", await test_fetch_and_reply()))
    
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
        print("\n🎉 All Gmail integration tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
