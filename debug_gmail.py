import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from backend.src.channels.gmail_handler import GmailHandler

async def main():
    handler = GmailHandler(
        credentials_path="backend/credentials.json", 
        token_path="backend/token.json"
    )
    print("Fetching last 10 messages...")
    messages = await handler.fetch_messages(query="") # No query = all messages
    print(f"Found {len(messages)} messages.")
    for msg in messages[:10]:
        print(f"- From: {msg.customer_email} | Subject: {msg.metadata.get('subject')}")

if __name__ == "__main__":
    asyncio.run(main())
