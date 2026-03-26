"""
Test WhatsApp with direct processing - shows AI response
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_whatsapp_direct():
    """Test WhatsApp processing directly (without webhook)"""
    print("=" * 70)
    print("🧪 DIRECT WHATSAPP PROCESSING TEST")
    print("=" * 70)
    print()
    
    from api.main import process_direct_message
    
    # Test message
    test_content = "Hello, I need help resetting my API key"
    test_phone = "+923001234567"
    
    print(f"📥 Incoming WhatsApp message:")
    print(f"   From: {test_phone}")
    print(f"   Content: {test_content}")
    print()
    print("🔄 Processing...")
    print()
    
    try:
        ticket_id, outbound = await process_direct_message(
            channel="whatsapp",
            content=test_content,
            customer_phone=test_phone,
            customer_name="Test User",
            channel_message_id="SMtest123"
        )
        
        print()
        print("=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        print(f"✅ Ticket ID: {ticket_id}")
        print(f"✅ AI Response: {outbound}")
        print()
        
        # Check if response was sent
        if outbound and len(outbound) > 0:
            print("✅ Response generated successfully!")
            print()
            print("📱 WHATSAPP RESPONSE SHOULD BE SENT TO:", test_phone)
        else:
            print("❌ No response generated")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_whatsapp_direct())
