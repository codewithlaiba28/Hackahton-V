import asyncio
import os
import sys
from dotenv import load_dotenv

# Run from backend
load_dotenv('.env')

from src.channels.gmail_handler import GmailHandler

async def main():
    try:
        handler = GmailHandler(
            credentials_path="credentials.json", 
            token_path="token.json"
        )
        msg_id = "19d148ee59d94fef" # The NEW one the user sent
        print(f"Marking message {msg_id} as UNREAD...")
        handler.service.users().messages().modify(
            userId='me', 
            id=msg_id, 
            body={'addLabelIds': ['UNREAD']}
        ).execute()
        print("Success! Now wait for the background poll or trigger /webhook/gmail/poll.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
