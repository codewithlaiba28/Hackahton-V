"""Production Gmail handler for Customer Success FTE."""

import os
import base64
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.channels.base import Channel, ChannelMessage

# Google API client library imports (would be installed in production)
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger(__name__)

class GmailHandler:
    """Production handler for Gmail integration."""
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google API using local token/credentials."""
        if not GOOGLE_API_AVAILABLE:
            logger.warning("Google API libraries not installed. GmailHandler running in mock mode.")
            return

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # Note: In production, would handle full OAuth flow if no token exists
            
        if creds:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service initialized")

    async def fetch_messages(self, query: str = "is:unread") -> List[ChannelMessage]:
        """Fetch unread messages from Gmail inbox."""
        if not self.service:
            logger.error("Gmail service not initialized. Cannot fetch messages.")
            return []

        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            channel_messages = []
            for msg in messages:
                txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                
                # Parse components
                payload = txt.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
                
                # Extract snippet as content
                content = txt.get('snippet', '')
                
                channel_messages.append(ChannelMessage(
                    channel=Channel.EMAIL,
                    content=content,
                    customer_email=sender,
                    subject=subject,
                    channel_message_id=msg['id'],
                    metadata={'thread_id': txt.get('threadId')}
                ))
                
                # Mark as read (remove UNREAD label)
                self.service.users().messages().modify(
                    userId='me', 
                    id=msg['id'], 
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

            return channel_messages

        except Exception as e:
            logger.error(f"Error fetching Gmail messages: {e}")
            return []

    async def send_response(self, customer_email: str, subject: str, body: str, thread_id: Optional[str] = None) -> bool:
        """Send an email response to a customer."""
        if not self.service:
            logger.info(f"[MOCK EMAIL] To: {customer_email}, Subject: {subject}, Body: {body}")
            return True

        from email.message import EmailMessage
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = customer_email
        message['Subject'] = f"Re: {subject}" if not subject.startswith("Re: ") else subject
        
        # If part of a thread, we should set In-Reply-To and References headers
        # but for simplicity we'll just send a new message in the same thread
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {
            'raw': encoded_message
        }
        
        if thread_id:
            create_message['threadId'] = thread_id

        try:
            self.service.users().messages().send(userId="me", body=create_message).execute()
            return True
        except Exception as e:
            logger.error(f"Error sending Gmail message: {e}")
            return False
