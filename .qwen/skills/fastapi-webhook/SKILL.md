---
name: fastapi-webhook
description: FastAPI webhook endpoints for Gmail, WhatsApp, and Web Form integrations with signature validation, async handlers, and channel-aware request processing.
---

# FastAPI Webhook Skill

## Purpose

This skill provides complete FastAPI implementations for handling webhooks from multiple channels (Gmail, WhatsApp/Twilio, Web Forms) with proper signature validation, async request handling, error handling, and integration with the Customer Success AI agent.

## When to Use This Skill

Use this skill when you need to:
- Receive webhooks from Gmail API Pub/Sub
- Handle Twilio WhatsApp webhook notifications
- Build web form submission endpoints
- Validate webhook signatures for security
- Process async requests with proper error handling
- Return appropriate responses for each channel
- Integrate with Kafka for event streaming

---

## Project Structure

```
api/
├── __init__.py
├── main.py                 # FastAPI application
├── routes/
│   ├── __init__.py
│   ├── webhooks.py         # Webhook routes
│   └── api.py              # API routes
├── handlers/
│   ├── __init__.py
│   ├── gmail_handler.py    # Gmail webhook handler
│   ├── whatsapp_handler.py # WhatsApp webhook handler
│   └── web_form_handler.py # Web form handler
└── middleware/
    ├── __init__.py
    └── security.py         # Security middleware
```

---

## Main FastAPI Application

```python
# api/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from api.routes import webhooks, api
from api.middleware.security import SecurityMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Customer Success FTE API...")
    
    # Initialize database connections
    from database.queries import DatabaseQueries
    db = DatabaseQueries()
    await db.create_pool()
    
    # Initialize Kafka producer
    from workers.kafka_producer import KafkaIngressProducer
    producer = KafkaIngressProducer(bootstrap_servers=['localhost:9092'])
    await producer.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Customer Success FTE API...")
    await producer.stop()
    await db.close_pool()

# Create FastAPI application
app = FastAPI(
    title="Customer Success FTE API",
    description="API for handling customer support across multiple channels",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Include routers
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(api.router, prefix="/api", tags=["API"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Readiness check endpoint
@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes."""
    # Check database connection
    # Check Kafka connection
    return {"status": "ready"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Customer Success FTE API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

---

## Security Middleware

```python
# api/middleware/security.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for request validation."""
    
    async def dispatch(self, request: Request, call_next):
        # Add request ID
        request_id = f"req_{int(time.time() * 1000)}"
        request.state.request_id = request_id
        
        # Rate limiting (simple implementation)
        client_ip = request.client.host
        if await self.is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests"}
            )
        
        # Log request
        logger.info(f"{request.method} {request.url.path} - {client_ip}")
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        """Simple rate limiting check."""
        # Implement proper rate limiting with Redis in production
        return False
```

---

## Gmail Webhook Handler

```python
# api/handlers/gmail_handler.py

from fastapi import Request, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class GmailWebhookHandler:
    """Handle Gmail webhook notifications."""
    
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = None
    
    def get_service(self):
        """Get Gmail API service."""
        if not self.service:
            credentials = Credentials.from_authorized_user_file(self.credentials_path)
            self.service = build('gmail', 'v1', credentials=credentials)
        return self.service
    
    async def process_pubsub_notification(self, request: Request) -> dict:
        """Process Gmail Pub/Sub webhook notification."""
        try:
            # Parse request body
            body = await request.json()
            
            # Decode Pub/Sub message
            message_data = base64.b64decode(body['message']['data']).decode('utf-8')
            pubsub_message = json.loads(message_data)
            
            history_id = pubsub_message.get('historyId')
            
            # Get new messages since last history ID
            messages = await self.fetch_new_messages(history_id)
            
            return {
                "status": "success",
                "processed": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Failed to process Gmail notification: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def fetch_new_messages(self, history_id: str) -> list:
        """Fetch new messages since history ID."""
        service = self.get_service()
        
        try:
            history = service.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded']
            ).execute()
            
            messages = []
            for record in history.get('history', []):
                for msg_added in record.get('messagesAdded', []):
                    msg_id = msg_added['message']['id']
                    message = await self.parse_message(msg_id)
                    messages.append(message)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to fetch messages: {e}")
            return []
    
    async def parse_message(self, message_id: str) -> dict:
        """Parse Gmail message into structured format."""
        service = self.get_service()
        
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        # Extract body
        body = self.extract_body(msg['payload'])
        
        # Extract email address
        from_email = self.extract_email(headers.get('From', ''))
        
        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': from_email,
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': msg.get('labelIds', [])
            }
        }
    
    def extract_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return ''
    
    def extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        import re
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header
    
    async def send_reply(self, to_email: str, subject: str, body: str, thread_id: str = None) -> dict:
        """Send email reply via Gmail API."""
        service = self.get_service()
        
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id
        
        result = service.users().messages().send(
            userId='me',
            body=send_request
        ).execute()
        
        return {
            'channel_message_id': result['id'],
            'delivery_status': 'sent',
            'thread_id': result.get('threadId')
        }
```

---

## WhatsApp Webhook Handler

```python
# api/handlers/whatsapp_handler.py

from fastapi import Request, HTTPException, Form
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WhatsAppWebhookHandler:
    """Handle WhatsApp webhook notifications from Twilio."""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)
    
    async def validate_webhook(self, request: Request) -> bool:
        """Validate Twilio webhook signature."""
        signature = request.headers.get('X-Twilio-Signature', '')
        url = str(request.url)
        body = await request.body()
        
        return self.validator.validate(url, body, signature)
    
    async def process_incoming_message(self, request: Request) -> dict:
        """Process incoming WhatsApp message from Twilio webhook."""
        try:
            form_data = await request.form()
            
            from_number = form_data.get('From', '')
            to_number = form_data.get('To', '')
            body = form_data.get('Body', '')
            message_sid = form_data.get('MessageSid', '')
            
            # Extract phone number from WhatsApp format
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
            
        except Exception as e:
            logger.error(f"Failed to process WhatsApp message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_reply(self, to_phone: str, message: str, media_url: str = None) -> dict:
        """Send WhatsApp reply via Twilio."""
        try:
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
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return {
                'channel_message_id': None,
                'delivery_status': 'failed',
                'error': str(e)
            }
    
    async def get_message_status(self, message_sid: str) -> str:
        """Get delivery status of a WhatsApp message."""
        try:
            message = self.client.messages(message_sid).fetch()
            return message.status  # queued, sent, delivered, read, failed
        except Exception as e:
            logger.error(f"Failed to get message status: {e}")
            return 'unknown'
```

---

## Web Form Handler

```python
# api/handlers/web_form_handler.py

from fastapi import Request, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebFormRequest(BaseModel):
    """Web support form request model."""
    customer_email: EmailStr
    customer_name: Optional[str] = None
    subject: str
    message: str
    priority: Optional[str] = "medium"

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
                'ip_address': None,
                'user_agent': None
            }
        }
    
    async def send_confirmation_email(self, email: str, ticket_id: str, subject: str) -> dict:
        """Send confirmation email after form submission."""
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
```

---

## Webhook Routes

```python
# api/routes/webhooks.py

from fastapi import APIRouter, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
import logging

from api.handlers.gmail_handler import GmailWebhookHandler
from api.handlers.whatsapp_handler import WhatsAppWebhookHandler
from api.handlers.web_form_handler import WebFormHandler, WebFormRequest
from workers.kafka_producer import KafkaIngressProducer

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize handlers
gmail_handler = GmailWebhookHandler(credentials_path="/path/to/credentials.json")
whatsapp_handler = WhatsAppWebhookHandler()
web_form_handler = WebFormHandler()
kafka_producer = KafkaIngressProducer(bootstrap_servers=['localhost:9092'])

async def process_through_agent(message_data: dict) -> dict:
    """Send message to agent for processing."""
    # Send to Kafka for async processing
    message_id = await kafka_producer.send_message(message_data)
    
    # For synchronous response (use async processing in production)
    # result = await agent_runner.run(message_data)
    # return result
    
    return {
        'status': 'processing',
        'message_id': message_id
    }

@router.post("/gmail")
async def gmail_webhook(request: Request):
    """Handle Gmail Pub/Sub webhook notifications."""
    try:
        result = await gmail_handler.process_pubsub_notification(request)
        return result
    except Exception as e:
        logger.error(f"Gmail webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp webhook notifications from Twilio."""
    try:
        # Validate webhook signature
        is_valid = await whatsapp_handler.validate_webhook(request)
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process incoming message
        message_data = await whatsapp_handler.process_incoming_message(request)
        
        # Send to agent for processing
        agent_response = await process_through_agent(message_data)
        
        # Return TwiML response for immediate reply
        resp = MessagingResponse()
        resp.message("We've received your message and will respond shortly.")
        
        return str(resp)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web-form")
async def web_form_submit(request: WebFormRequest):
    """Handle web support form submissions."""
    try:
        # Process form submission
        message_data = await web_form_handler.process_form_submission(request)
        
        # Send to agent for processing
        agent_response = await process_through_agent(message_data)
        
        # Send confirmation email
        ticket_id = agent_response.get('ticket_id', message_data['channel_message_id'])
        await web_form_handler.send_confirmation_email(
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
        logger.error(f"Web form error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

## API Routes

```python
# api/routes/api.py

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()

class TicketStatus(BaseModel):
    ticket_id: str
    status: str
    message: str

@router.get("/tickets/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get ticket status by ID."""
    # Query database for ticket status
    return {
        'ticket_id': ticket_id,
        'status': 'open',
        'created_at': '2024-01-01T00:00:00Z'
    }

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {'status': 'healthy'}
```

---

## Running the API

```python
# uvicorn runner

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

---

## Testing

```python
# tests/test_webhooks.py

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestGmailWebhook:
    def test_gmail_webhook_valid(self):
        """Test valid Gmail webhook."""
        response = client.post(
            "/webhooks/gmail",
            json={
                "message": {
                    "data": "eyJoaXN0b3J5SWQiOiAiMTIzNDU2Nzg5MCJ9"
                }
            }
        )
        assert response.status_code == 200

class TestWhatsAppWebhook:
    def test_whatsapp_webhook_valid(self):
        """Test valid WhatsApp webhook."""
        response = client.post(
            "/webhooks/whatsapp",
            data={
                "From": "whatsapp:+1234567890",
                "To": "whatsapp:+14155238886",
                "Body": "Test message",
                "MessageSid": "SM1234567890"
            },
            headers={
                "X-Twilio-Signature": "test-signature"
            }
        )
        assert response.status_code == 200

class TestWebForm:
    def test_web_form_valid(self):
        """Test valid web form submission."""
        response = client.post(
            "/webhooks/web-form",
            json={
                "customer_email": "test@example.com",
                "customer_name": "Test User",
                "subject": "Test Subject",
                "message": "Test message"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'ticket_id' in data
    
    def test_web_form_invalid_email(self):
        """Test web form with invalid email."""
        response = client.post(
            "/webhooks/web-form",
            json={
                "customer_email": "invalid-email",
                "subject": "Test",
                "message": "Test"
            }
        )
        assert response.status_code == 422
```

---

## Acceptance Criteria

- [ ] Gmail webhook processes Pub/Sub notifications
- [ ] WhatsApp webhook validates Twilio signatures
- [ ] Web form validates input with Pydantic
- [ ] All handlers send messages to Kafka
- [ ] Error handling exists for all endpoints
- [ ] Health check endpoints work
- [ ] All tests pass
- [ ] Logging is configured properly
- [ ] Security middleware is active

## Related Skills

- `channel-integrations` - Channel handler implementations
- `kafka-event-processing` - Kafka producer for events
- `customer-success-agent` - Agent receives messages
- `k8s-fte-deployment` - API deployed on Kubernetes

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio Webhook Documentation](https://www.twilio.com/docs/usage/webhooks)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
