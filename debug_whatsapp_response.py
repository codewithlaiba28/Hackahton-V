"""
Debug WhatsApp Response - Check what's actually being sent to Twilio
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Disable tracing
os.environ['OPENAI_AGENTS_DISABLE_TRACING'] = '1'
os.environ['OTEL_TRACES_EXPORTER'] = 'none'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.api.main import process_direct_message

async def test_whatsapp_response():
    """Test what response is actually generated"""
    print("=" * 70)
    print("DEBUG: WhatsApp Response Test")
    print("=" * 70)
    print()
    
    # Use a NEW phone number to avoid any caching
    test_phone = "+923009999888"
    test_content = "Hi"
    
    print(f"Input:")
    print(f"  Phone: {test_phone}")
    print(f"  Message: {test_content}")
    print()
    print("Processing...")
    print()
    
    try:
        ticket_id, outbound = await process_direct_message(
            channel='whatsapp',
            content=test_content,
            customer_phone=test_phone,
            customer_name='Debug Test User',
            channel_message_id='SMdebug123'
        )
        
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Ticket ID: {ticket_id}")
        print()
        print(f"Output Type: {type(outbound)}")
        print(f"Output Length: {len(outbound) if outbound else 0}")
        print()
        print(f"Raw Output:")
        print(f"  {outbound}")
        print()
        
        # Check if output is a proper string or tool call
        if 'function' in outbound or 'name' in outbound:
            print("⚠️  WARNING: Output looks like a tool call, not a message!")
            print("   This might cause Twilio to reject the message.")
        else:
            print("✓ Output looks like a proper message")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_whatsapp_response())
