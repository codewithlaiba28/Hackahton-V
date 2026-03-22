import asyncio
import os
import sys
from dotenv import load_dotenv

# Run this script FROM the backend directory!
# cd backend && python debug_gmail.py

load_dotenv('.env')

from src.channels.gmail_handler import GmailHandler

async def main():
    try:
        handler = GmailHandler(
            credentials_path="credentials.json", 
            token_path="token.json"
        )
        print("Fetching last 10 messages from ALL (including READ)...")
        # Querying for all messages matching query ''
        messages = await handler.fetch_messages(query="")
        print(f"Total messages found: {len(messages)}")
        for msg in messages[:10]:
            print(f"- From: {msg.customer_email} | Subject: {msg.metadata.get('subject', 'No Subject')}")
    except Exception as e:
        print(f"Debugger error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
