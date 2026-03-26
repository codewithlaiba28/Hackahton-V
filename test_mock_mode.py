"""
Test Twilio Message Sending with Mock Mode
This bypasses the Twilio API limit check
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("MOCK MODE TEST - Bypass Twilio API")
print("=" * 70)
print()

# Save original credentials
original_sid = os.getenv('TWILIO_ACCOUNT_SID')
original_token = os.getenv('TWILIO_AUTH_TOKEN')

print("Original Credentials:")
print(f"  Account SID: {original_sid[:10]}...")
print(f"  Auth Token: {original_token[:5]}...")
print()

# Set mock mode
os.environ['TWILIO_ACCOUNT_SID'] = 'mock'
os.environ['TWILIO_AUTH_TOKEN'] = 'mock'

print("Mock Mode Enabled:")
print(f"  Account SID: mock")
print(f"  Auth Token: mock")
print()

import asyncio
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.api.main import process_direct_message

async def test_mock_mode():
    """Test with mock mode - no Twilio API calls"""
    print("Testing with MOCK mode...")
    print()
    
    try:
        ticket_id, outbound = await process_direct_message(
            channel='whatsapp',
            content='Hello, I need help',
            customer_phone='+923001111222',
            customer_name='Mock Test User',
            channel_message_id='SMmock123'
        )
        
        print()
        print("=" * 70)
        print("MOCK MODE RESULTS")
        print("=" * 70)
        print(f"✓ Ticket ID: {ticket_id}")
        print(f"✓ Response Generated: {outbound[:100] if outbound else 'None'}...")
        print()
        print("✓ Mock mode working - no Twilio API calls made!")
        print()
        print("To send real messages, you need to:")
        print("  1. Wait for Twilio limit to reset (24 hours)")
        print("  2. OR upgrade to paid Twilio account")
        print("  3. OR use your own Twilio credentials")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)

asyncio.run(test_mock_mode())
