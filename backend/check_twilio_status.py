"""
Check Twilio Account Status and WhatsApp Limits
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

print("=" * 70)
print("📱 TWILIO ACCOUNT STATUS")
print("=" * 70)
print()

try:
    client = Client(account_sid, auth_token)
    
    # Get account info
    account = client.api.accounts(account_sid).fetch()
    print(f"✅ Account: {account.friendly_name}")
    print(f"   SID: {account.sid}")
    print(f"   Status: {account.status}")
    print(f"   Type: {account.type}")
    print()
    
    # Get WhatsApp number info
    print(f"📞 WhatsApp Number: {whatsapp_number}")
    
    # Check if it's sandbox
    if '14155238886' in whatsapp_number:
        print(f"   ⚠️  This is the TWILIO SANDBOX number")
        print(f"   ⚠️  Limit: 5 messages per day")
        print()
        print("   To remove limits:")
        print("   1. Upgrade account: https://console.twilio.com")
        print("   2. Get dedicated WhatsApp number")
        print("   3. Update TWILIO_WHATSAPP_NUMBER in .env")
    else:
        print(f"   ✅ This is your dedicated number")
    
    print()
    
    # Check messaging service
    try:
        messaging_services = client.messaging.services.list(limit=5)
        if messaging_services:
            print(f"📨 Messaging Services: {len(messaging_services)}")
            for ms in messaging_services:
                print(f"   - {ms.friendly_name} ({ms.sid})")
    except Exception as e:
        print(f"⚠️  Could not fetch messaging services: {e}")
    
    print()
    
    # Check recent messages
    print("📊 Recent Messages (last 10):")
    messages = client.messages.list(limit=10)
    
    if messages:
        for msg in messages[:10]:
            date = msg.date_created.strftime('%Y-%m-%d %H:%M') if msg.date_created else 'Unknown'
            print(f"   {date} | {msg.to} | {msg.status} | {msg.direction}")
    else:
        print("   No messages found")
    
    print()
    print("=" * 70)
    print("ℹ️  SANDBOX LIMIT INFO:")
    print("=" * 70)
    print()
    print("The Twilio Sandbox allows:")
    print("  • 5 messages per day (resets every 24 hours)")
    print("  • Only to numbers that joined the sandbox")
    print("  • 24-hour session window")
    print()
    print("To send unlimited messages:")
    print("  1. Upgrade to paid Twilio account")
    print("  2. Get WhatsApp Business API approval")
    print("  3. Cost: ~$0.005 per message")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Check your TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
