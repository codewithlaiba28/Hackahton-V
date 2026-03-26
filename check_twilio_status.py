"""
Check Twilio Account Status and Limits
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
import os
import json

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

print("=" * 70)
print("TWILIO ACCOUNT STATUS CHECK")
print("=" * 70)
print()

print(f"Account SID: {account_sid}")
print(f"Auth Token: {auth_token[:5]}...{auth_token[-5:] if auth_token else 'None'}")
print(f"WhatsApp Number: {whatsapp_number}")
print()

try:
    client = Client(account_sid, auth_token)
    
    # Fetch account info
    print("Fetching account information...")
    account = client.api.accounts(account_sid).fetch()
    print(f"✓ Account Name: {account.friendly_name}")
    print(f"✓ Account SID: {account.sid}")
    print(f"✓ Account Status: {account.status}")
    print()
    
    # Try to send a test message (without actually sending)
    print("Checking messaging capability...")
    try:
        # This will fail if there's a limit, but we can see the error
        message = client.messages.create(
            body="Test",
            from_=whatsapp_number,
            to="whatsapp:+923001234567"  # Fake number for testing
        )
        print(f"✓ Message created: {message.sid}")
    except TwilioRestException as e:
        print(f"✗ Message creation failed:")
        print(f"   Error Code: {e.code}")
        print(f"   Error Message: {e.msg}")
        print(f"   Status: {e.status}")
        print()
        
        if e.code == 63038:
            print("⚠️  ERROR 63038: Daily message limit exceeded!")
            print()
            print("POSSIBLE CAUSES:")
            print("  1. Twilio Free Trial account - 5 messages/day limit")
            print("  2. Sandbox account - restricted messaging")
            print("  3. Account not upgraded to paid plan")
            print()
            print("SOLUTIONS:")
            print("  1. Wait 24 hours for limit reset")
            print("  2. Upgrade to paid Twilio account")
            print("  3. Use mock mode for testing (set TWILIO_ACCOUNT_SID=mock)")
        elif e.code == 21211:
            print("⚠️  ERROR 21211: Invalid phone number format")
        elif e.code == 21670:
            print("⚠️  ERROR 21670: Not a valid WhatsApp user")
        elif e.code == 21675:
            print("⚠️  ERROR 21675: Not opted-in for WhatsApp")
        else:
            print(f"⚠️  Unknown error: {e.code}")
    
    print()
    print("=" * 70)
    
except Exception as e:
    print(f"✗ Failed to connect to Twilio:")
    print(f"   Error: {e}")
    print()
    print("POSSIBLE CAUSES:")
    print("  1. Invalid Account SID or Auth Token")
    print("  2. Account suspended or closed")
    print("  3. Network connectivity issue")
    print()
    print("SOLUTION:")
    print("  - Check your Twilio credentials in .env file")
    print("  - Verify account is active at https://console.twilio.com")

print()
print("=" * 70)
