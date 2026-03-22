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
        print("Gmail service initialized.")
        profile = handler.service.users().getProfile(userId='me').execute()
        print(f"Authenticated as: {profile.get('emailAddress')}")
        print(f"Total messages in mailbox: {profile.get('messagesTotal')}")
        
        print("\nListing last 5 messages with labels:")
        results = handler.service.users().messages().list(userId='me', maxResults=5).execute()
        msgs = results.get('messages', [])
        for m in msgs:
            details = handler.service.users().messages().get(userId='me', id=m['id'], format='minimal').execute()
            labels = details.get('labelIds', [])
            subject = "Unknown"
            # Get subject from headers
            full = handler.service.users().messages().get(userId='me', id=m['id'], format='full').execute()
            headers = full.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            print(f"- ID: {m['id']} | Subject: {subject} | Labels: {labels}")
    except Exception as e:
        print(f"Auth verification error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
