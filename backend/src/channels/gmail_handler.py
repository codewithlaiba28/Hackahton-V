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

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract the plain text body from a Gmail message payload."""
        # Recursive function to find text parts
        def find_parts(part_node):
            text_parts = []
            if 'parts' in part_node:
                for subpart in part_node['parts']:
                    text_parts.extend(find_parts(subpart))
            
            mime_type = part_node.get('mimeType', '')
            if mime_type == 'text/plain' and 'body' in part_node and 'data' in part_node['body']:
                try:
                    text_parts.append(base64.urlsafe_b64decode(part_node['body']['data']).decode('utf-8'))
                except Exception:
                    pass
            elif mime_type == 'text/html' and 'body' in part_node and 'data' in part_node['body']:
                try:
                    # Basic HTML to text if plain was not found
                    import re
                    html = base64.urlsafe_b64decode(part_node['body']['data']).decode('utf-8')
                    text_parts.append(re.sub(r'<[^>]+>', '', html))
                except Exception:
                    pass
            return text_parts

        all_text = find_parts(payload)
        # Prioritize plain text if available
        return "\n".join(all_text) if all_text else ""

    async def fetch_messages(self, query: str = "is:unread", mark_as_read: bool = True) -> List[ChannelMessage]:
        """
        Fetch unread messages from Gmail inbox.
        
        Args:
            query: Gmail search query (default: "is:unread" for unread messages only)
        
        Returns:
            List of ChannelMessage objects with full content extracted
        """
        if not self.service:
            logger.error("Gmail service not initialized. Cannot fetch messages.")
            return []

        try:
            logger.info(f"Fetching Gmail messages with query: '{query}'")
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found matching query")
                return []

            logger.info(f"Found {len(messages)} messages")
            channel_messages = []
            
            for msg in messages:
                try:
                    # Fetch full message with format=full to get payload
                    txt = self.service.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='full'
                    ).execute()

                    # Parse components
                    payload = txt.get('payload', {})
                    headers = payload.get('headers', [])

                    # Extract headers
                    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
                    
                    # Extract recipient (for verification)
                    recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), "")
                    cc = next((h['value'] for h in headers if h['name'].lower() == 'cc'), "")

                    # Extract full body content
                    content = self._extract_body(payload)
                    
                    # Fallback to snippet if body extraction failed
                    if not content:
                        content = txt.get('snippet', '')
                        logger.warning(f"Using snippet for message {msg['id']} - body extraction failed")

                    # Skip empty messages
                    if not content or not content.strip():
                        logger.warning(f"Skipping empty message {msg['id']}")
                        continue

                    logger.info(f"Extracted message from {sender} with subject '{subject}' ({len(content)} chars)")

                    channel_messages.append(ChannelMessage(
                        channel=Channel.EMAIL,
                        content=content.strip(),
                        customer_email=sender,
                        subject=subject,
                        channel_message_id=msg['id'],
                        metadata={
                            'thread_id': txt.get('threadId'),
                            'recipient': recipient,
                            'cc': cc,
                            'labels': txt.get('labelIds', []),
                            'internal_date': txt.get('internalDate')
                        }
                    ))

                    if mark_as_read:
                        try:
                            self.service.users().messages().modify(
                                userId='me',
                                id=msg['id'],
                                body={'removeLabelIds': ['UNREAD']}
                            ).execute()
                            logger.info(f"Marked message {msg['id']} as read")
                        except Exception as mark_error:
                            logger.warning(f"Failed to mark message as read: {mark_error}")

                except Exception as msg_error:
                    logger.error(f"Error processing message {msg['id']}: {msg_error}")
                    continue

            logger.info(f"Successfully fetched {len(channel_messages)} messages from Gmail")
            return channel_messages

        except Exception as e:
            logger.error(f"Error fetching Gmail messages: {e}", exc_info=True)
            return []

    async def send_reply(self, customer_email: str, subject: str, body: str, thread_id: Optional[str] = None, in_reply_to: Optional[str] = None, cc: Optional[str] = None) -> bool:
        """
        Send an email response to a customer via Gmail API.
        
        Args:
            customer_email: Recipient email address
            subject: Email subject line
            body: Email body content
            thread_id: Optional thread ID to reply in
            in_reply_to: Optional Message-ID to reply to
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.service:
            logger.info(f"[MOCK EMAIL] To: {customer_email}, Subject: {subject}, Body: {body[:100]}...")
            return True

        from email.message import EmailMessage
        import email.utils

        message = EmailMessage()
        message.set_content(body)
        message['To'] = customer_email
        message['From'] = 'me'  # Gmail will fill this in
        if cc:
            message['Cc'] = cc
        message['Subject'] = f"Re: {subject}" if not subject.startswith("Re: ") else subject
        
        # Add In-Reply-To and References headers for threading
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        create_message = {
            'raw': encoded_message
        }

        if thread_id:
            create_message['threadId'] = thread_id

        try:
            logger.info(f"Sending Gmail message to {customer_email} in thread {thread_id or 'new'}")
            sent_message = self.service.users().messages().send(userId="me", body=create_message).execute()
            logger.info(f"Gmail message sent successfully! Message ID: {sent_message.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Error sending Gmail message: {e}", exc_info=True)
            return False
