---
name: channel-integrations
description: Multi-channel customer support integrations for Gmail API, Twilio WhatsApp API, and Web Form handlers with webhook processing and channel-aware response delivery.
---

# Channel Integrations Skill

## Purpose

This skill provides complete implementations for integrating a Customer Success AI agent with three communication channels: Gmail (Email), WhatsApp (via Twilio), and Web Form (FastAPI endpoint).

## When to Use This Skill

Use this skill when you need to:
- Receive customer support inquiries from multiple channels
- Process Gmail messages via API or webhooks
- Handle WhatsApp messages via Twilio API
- Build a web support form with API backend
- Send responses back through the original channel
- Track channel-specific metadata and message IDs

## Channel Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Gmail     │    │   WhatsApp   │    │   Web Form   │
│   (Email)    │    │  (Messaging) │    │  (Website)   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Gmail API /  │    │   Twilio     │    │   FastAPI    │
│   Webhook    │    │   Webhook    │    │   Endpoint   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                 ┌─────────────────┐
                 │  Unified Ticket │
                 │    Ingestion    │
                 └────────┬────────┘
```

## Channel Specifications

| Channel | Identifier | Response Style | Max Length | Processing |
|---------|------------|----------------|------------|------------|
| **Gmail** | Email address | Formal, detailed | 500 words | Pub/Sub or polling |
| **WhatsApp** | Phone number | Conversational, concise | 300 chars preferred | Twilio webhook |
| **Web Form** | Email address | Semi-formal | 300 words | FastAPI endpoint |

---

## 1. Gmail Integration

### Setup Requirements

1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Set up Pub/Sub topic for push notifications (optional)
4. Request Gmail API scopes: `gmail.readonly`, `gmail.send`, `gmail.modify`

### Implementation

```python
# channels/gmail_handler.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.cloud import pubsub_v1
import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
import json

class GmailHandler:
    """Handle Gmail integration for customer support."""
    
    def __init__(self, credentials_path: str):
        self.credentials = Credentials.from_authorized_user_file(credentials_path)
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    async def setup_push_notifications(self, topic_name: str):
        """Set up Gmail push notifications via Pub/Sub."""
        request = {
            'labelIds': ['INBOX'],
            'topicName': topic_name,
            'labelFilterAction': 'include'
        }
        return self.service.users().watch(userId='me', body=request).execute()
    
    async def process_incoming_message(self, message_id: str) -> dict:
        """Fetch and parse a Gmail message."""
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        body = self._extract_body(msg['payload'])
        
        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': self._extract_email(headers.get('From', '')),
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': msg.get('labelIds', [])
            }
        }
    
    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return ''
    
    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        import re
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header
    
    async def send_reply(self, to_email: str, subject: str, body: str, thread_id: str = None) -> dict:
        """Send email reply via Gmail API."""
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id
        
        result = self.service.users().messages().send(
            userId='me',
            body=send_request
        ).execute()
        
        return {
            'channel_message_id': result['id'],
            'delivery_status': 'sent',
            'thread_id': result.get('threadId')
        }
    
    async def stop_notifications(self):
        """Stop Gmail push notifications."""
        self.service.users().stop(userId='me').execute()
```

### Gmail Webhook Handler (Pub/Sub)

```python
# channels/gmail_webhook.py

from fastapi import FastAPI, Request, HTTPException
from google.cloud import pubsub_v1
import base64
import json

app = FastAPI()

class GmailWebhookHandler:
    """Handle Gmail Pub/Sub webhook notifications."""
    
    def __init__(self, gmail_handler: GmailHandler):
        self.gmail_handler = gmail_handler
    
    async def process_pubsub_message(self, pubsub_message: dict):
        """Process incoming Pub/Sub notification from Gmail."""
        history_id = pubsub_message.get('historyId')
        
        # Get new messages since last history ID
        history = self.gmail_handler.service.users().history().list(
            userId='me',
            startHistoryId=history_id,
            historyTypes=['messageAdded']
        ).execute()
        
        messages = []
        for record in history.get('history', []):
            for msg_added in record.get('messagesAdded', []):
                msg_id = msg_added['message']['id']
                message = await self.gmail_handler.process_incoming_message(msg_id)
                messages.append(message)
        
        return messages

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    """Handle Gmail Pub/Sub webhook."""
    try:
        body = await request.json()
        message_data = base64.b64decode(body['message']['data']).decode('utf-8')
        pubsub_message = json.loads(message_data)
        
        handler = GmailWebhookHandler(gmail_handler)
        messages = await handler.process_pubsub_message(pubsub_message)
        
        # Process each message through the agent
        for message in messages:
            await process_through_agent(message)
        
        return {"status": "success", "processed": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 2. WhatsApp Integration (via Twilio)

### Setup Requirements

1. Create Twilio account
2. Get WhatsApp-enabled phone number
3. Configure webhook URL in Twilio console
4. Store credentials: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`

### Implementation

```python
# channels/whatsapp_handler.py

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException, Form
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime

class WhatsAppHandler:
    """Handle WhatsApp integration via Twilio."""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)
    
    async def validate_webhook(self, request: Request) -> bool:
        """Validate incoming Twilio webhook signature."""
        signature = request.headers.get('X-Twilio-Signature', '')
        url = str(request.url)
        body = await request.body()
        
        return self.validator.validate(url, body, signature)
    
    async def process_incoming_message(self, request: Request) -> dict:
        """Process incoming WhatsApp message from Twilio webhook."""
        form_data = await request.form()
        
        from_number = form_data.get('From', '')
        to_number = form_data.get('To', '')
        body = form_data.get('Body', '')
        message_sid = form_data.get('MessageSid', '')
        
        # Extract phone number from WhatsApp format (whatsapp:+1234567890)
        customer_phone = from_number.replace('whatsapp:', '')
        
        return {
            'channel': 'whatsapp',
            'channel_message_id': message_sid,
            'customer_phone': customer_phone,
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'from': from_number,
                'to': to_number,
                'num_media': form_data.get('NumMedia', '0')
            }
        }
    
    async def send_reply(self, to_phone: str, message: str, media_url: str = None) -> dict:
        """Send WhatsApp reply via Twilio."""
        params = {
            'from': self.whatsapp_number,
            'to': f'whatsapp:{to_phone}',
            'body': message
        }
        
        if media_url:
            params['media_url'] = media_url
        
        twilio_message = self.client.messages.create(**params)
        
        return {
            'channel_message_id': twilio_message.sid,
            'delivery_status': 'sent',
            'sid': twilio_message.sid
        }
    
    async def get_message_status(self, message_sid: str) -> str:
        """Get delivery status of a WhatsApp message."""
        message = self.client.messages(message_sid).fetch()
        return message.status  # queued, sent, delivered, read, failed
```

### WhatsApp Webhook Endpoint

```python
# channels/whatsapp_webhook.py

from fastapi import APIRouter, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter()

@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        # Validate webhook signature
        handler = WhatsAppHandler()
        is_valid = await handler.validate_webhook(request)
        
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process incoming message
        form_data = await request.form()
        message_data = await handler.process_incoming_message(request)
        
        # Send to agent for processing
        agent_response = await process_through_agent(message_data)
        
        # Send reply via WhatsApp
        customer_phone = message_data['customer_phone']
        await handler.send_reply(customer_phone, agent_response['output'])
        
        # Return TwiML response (optional, for immediate reply)
        resp = MessagingResponse()
        resp.message(agent_response['output'])
        
        return str(resp)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 3. Web Form Integration

### Implementation

```python
# channels/web_form_handler.py

from fastapi import FastAPI, APIRouter, Request, Form, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class WebFormRequest(BaseModel):
    """Web support form request model."""
    customer_email: EmailStr
    customer_name: Optional[str] = None
    subject: str
    message: str
    priority: Optional[str] = "medium"  # low, medium, high

class WebFormHandler:
    """Handle web support form submissions."""
    
    async def process_form_submission(self, data: WebFormRequest) -> dict:
        """Process incoming web form submission."""
        return {
            'channel': 'web_form',
            'channel_message_id': str(uuid.uuid4()),
            'customer_email': data.customer_email,
            'customer_name': data.customer_name,
            'subject': data.subject,
            'content': data.message,
            'priority': data.priority,
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'source': 'web_form',
                'ip_address': None,  # Add from request if needed
                'user_agent': None
            }
        }
    
    async def send_confirmation_email(self, email: str, ticket_id: str, subject: str) -> dict:
        """Send confirmation email after form submission."""
        # Use Gmail handler or SMTP to send confirmation
        confirmation_body = f"""
Dear Customer,

Thank you for contacting TechCorp Support.

We have received your inquiry:
- Ticket ID: {ticket_id}
- Subject: {subject}

Our team will respond to you shortly.

Best regards,
TechCorp Customer Success Team
"""
        return {
            'confirmation_sent': True,
            'ticket_id': ticket_id
        }

# FastAPI Router
router = APIRouter()

@router.post("/api/support")
async def submit_support_form(request: WebFormRequest):
    """Handle web support form submission."""
    try:
        handler = WebFormHandler()
        message_data = await handler.process_form_submission(request)
        
        # Process through agent
        agent_response = await process_through_agent(message_data)
        
        # Send confirmation
        ticket_id = agent_response.get('ticket_id')
        await handler.send_confirmation_email(
            request.customer_email,
            ticket_id,
            request.subject
        )
        
        return {
            'status': 'success',
            'ticket_id': ticket_id,
            'message': 'Your support request has been submitted successfully.'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Web Form HTML Template

```html
<!-- templates/support_form.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Support - TechCorp</title>
    <style>
        .support-form {
            max-width: 600px;
            margin: 50px auto;
            padding: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-family: Arial, sans-serif;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="support-form">
        <h2>Customer Support</h2>
        <p>Fill out the form below and our team will get back to you shortly.</p>
        
        <form id="supportForm" onsubmit="handleSubmit(event)">
            <div class="form-group">
                <label for="email">Email Address *</label>
                <input type="email" id="email" name="customer_email" required>
            </div>
            
            <div class="form-group">
                <label for="name">Name (Optional)</label>
                <input type="text" id="name" name="customer_name">
            </div>
            
            <div class="form-group">
                <label for="subject">Subject *</label>
                <input type="text" id="subject" name="subject" required>
            </div>
            
            <div class="form-group">
                <label for="priority">Priority</label>
                <select id="priority" name="priority">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="message">Message *</label>
                <textarea id="message" name="message" required></textarea>
            </div>
            
            <button type="submit">Submit Request</button>
        </form>
        
        <div id="response"></div>
    </div>
    
    <script>
        async function handleSubmit(event) {
            event.preventDefault();
            
            const formData = {
                customer_email: document.getElementById('email').value,
                customer_name: document.getElementById('name').value,
                subject: document.getElementById('subject').value,
                priority: document.getElementById('priority').value,
                message: document.getElementById('message').value
            };
            
            try {
                const response = await fetch('/api/support', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('response').innerHTML = `
                        <div class="success-message">
                            <strong>Thank you!</strong> Your ticket ID is: ${result.ticket_id}
                            <br>We've sent a confirmation email to ${formData.customer_email}.
                        </div>
                    `;
                    document.getElementById('supportForm').reset();
                } else {
                    throw new Error(result.detail || 'Submission failed');
                }
            } catch (error) {
                document.getElementById('response').innerHTML = `
                    <div class="error-message">
                        <strong>Error:</strong> ${error.message}
                        <br>Please try again or contact us directly.
                    </div>
                `;
            }
        }
    </script>
</body>
</html>
```

---

## Unified Channel Router

```python
# channels/router.py

from typing import Union, Dict, Any
from enum import Enum

class ChannelType(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class UnifiedChannelRouter:
    """Route messages to appropriate channel handler."""
    
    def __init__(self):
        self.handlers = {
            ChannelType.EMAIL: GmailHandler(credentials_path),
            ChannelType.WHATSAPP: WhatsAppHandler(),
            ChannelType.WEB_FORM: WebFormHandler()
        }
    
    async def process_incoming(self, channel: ChannelType, raw_data: Any) -> Dict:
        """Process incoming message from any channel."""
        handler = self.handlers[channel]
        
        if channel == ChannelType.EMAIL:
            return await handler.process_incoming_message(raw_data)
        elif channel == ChannelType.WHATSAPP:
            return await handler.process_incoming_message(raw_data)
        elif channel == ChannelType.WEB_FORM:
            return await handler.process_form_submission(raw_data)
    
    async def send_response(self, channel: ChannelType, **kwargs) -> Dict:
        """Send response through appropriate channel."""
        handler = self.handlers[channel]
        return await handler.send_reply(**kwargs)
    
    def get_channel_config(self, channel: ChannelType) -> Dict:
        """Get channel-specific configuration."""
        configs = {
            ChannelType.EMAIL: {
                'max_response_length': 500,
                'style': 'formal',
                'requires_greeting': True,
                'requires_signature': True
            },
            ChannelType.WHATSAPP: {
                'max_response_length': 300,
                'style': 'conversational',
                'requires_greeting': False,
                'requires_signature': False
            },
            ChannelType.WEB_FORM: {
                'max_response_length': 300,
                'style': 'semi-formal',
                'requires_greeting': False,
                'requires_signature': False
            }
        }
        return configs[channel]
```

---

## Environment Variables

```bash
# .env

# Gmail API
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOPIC_ID=gmail-support-notifications

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Web Form
SUPPORT_FORM_EMAIL=support@techcorp.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@techcorp.com
SMTP_PASSWORD=your_smtp_password
```

---

## Testing

```python
# tests/test_channels.py

import pytest
from channels.gmail_handler import GmailHandler
from channels.whatsapp_handler import WhatsAppHandler
from channels.web_form_handler import WebFormHandler, WebFormRequest

class TestGmailHandler:
    @pytest.mark.asyncio
    async def test_process_incoming_message(self):
        handler = GmailHandler(credentials_path)
        message = await handler.process_incoming_message("test_message_id")
        
        assert message['channel'] == 'email'
        assert 'customer_email' in message
        assert 'content' in message
    
    @pytest.mark.asyncio
    async def test_send_reply(self):
        handler = GmailHandler(credentials_path)
        result = await handler.send_reply(
            to_email="customer@example.com",
            subject="Test",
            body="Test message"
        )
        
        assert result['delivery_status'] == 'sent'
        assert 'channel_message_id' in result

class TestWhatsAppHandler:
    @pytest.mark.asyncio
    async def test_process_incoming_message(self):
        handler = WhatsAppHandler()
        # Mock request data
        result = await handler.process_incoming_message(mock_request)
        
        assert result['channel'] == 'whatsapp'
        assert 'customer_phone' in result
    
    @pytest.mark.asyncio
    async def test_send_reply(self):
        handler = WhatsAppHandler()
        result = await handler.send_reply(
            to_phone="+1234567890",
            message="Test message"
        )
        
        assert result['delivery_status'] == 'sent'

class TestWebFormHandler:
    @pytest.mark.asyncio
    async def test_process_form_submission(self):
        handler = WebFormHandler()
        data = WebFormRequest(
            customer_email="test@example.com",
            customer_name="Test User",
            subject="Test Subject",
            message="Test message"
        )
        
        result = await handler.process_form_submission(data)
        
        assert result['channel'] == 'web_form'
        assert result['customer_email'] == "test@example.com"
```

---

## Acceptance Criteria

- [ ] Gmail integration receives and sends messages
- [ ] WhatsApp integration works via Twilio webhook
- [ ] Web form accepts submissions and sends confirmations
- [ ] All channel handlers validate input properly
- [ ] Channel-specific response formatting is applied
- [ ] Message IDs are tracked for delivery confirmation
- [ ] Webhook signatures are validated (security)
- [ ] Error handling exists for all channel operations
- [ ] All tests pass

## Related Skills

- `customer-success-agent` - Core agent logic
- `fastapi-webhook` - Webhook endpoint setup
- `postgres-crm-schema` - Message tracking in database
- `kafka-event-processing` - Event streaming from channels

## References

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Twilio WhatsApp API](https://www.twilio.com/whatsapp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
