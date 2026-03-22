import asyncio
from dotenv import load_dotenv
import os
import sys

# Add backend to path so we can import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from src.channels.gmail_handler import GmailHandler
from src.channels.whatsapp_handler import WhatsAppHandler
import logging

logging.basicConfig(level=logging.INFO)

async def check_integrations():
    print("--- Checking Gmail ---")
    g_handler = GmailHandler()
    if not g_handler.service:
        print("GMAIL ERROR: Service not initialized. Are credentials.json and token.json valid? Are google libs installed?")
    else:
        print("GMAIL: Service initialized!")
        msgs = await g_handler.fetch_messages("is:unread")
        print(f"GMAIL results: {len(msgs)} messages found.")

    print("\n--- Checking WhatsApp ---")
    w_handler = WhatsAppHandler()
    if not w_handler.client:
        print("WHATSAPP ERROR: Twilio client not initialized. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
    else:
        print("WHATSAPP: Client initialized!")

if __name__ == "__main__":
    asyncio.run(check_integrations())
