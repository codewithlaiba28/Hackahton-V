"""FastAPI application for Phase 2."""

import os
from dotenv import load_dotenv

# Disable ALL OpenAI Agents tracing BEFORE any imports
# This is the CORRECT way to disable tracing in OpenAI Agents SDK
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"
os.environ["OTEL_SERVICE_NAME"] = "customer-success-fte"

# Load environment variables FIRST
load_dotenv()

import sys
import httpx
import openai
from openai import AsyncOpenAI, OpenAI

# Force Cerebras settings globally (NOT OpenAI)
CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_URL = "https://api.cerebras.ai/v1"

if not CEREBRAS_KEY:
    logger.error("❌ CEREBRAS_API_KEY is missing from environment variables!")
    # We don't raise here yet to allow the app to start and show health errors, 
    # but we will fail agent runs.

if CEREBRAS_KEY:
    os.environ["OPENAI_API_KEY"] = CEREBRAS_KEY
    os.environ["OPENAI_BASE_URL"] = CEREBRAS_URL
    os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
    os.environ["OTEL_TRACES_EXPORTER"] = "none"

    # Ultimate Patch: Force every OpenAI & AsyncOpenAI client to use Cerebras
    _orig_async_init = AsyncOpenAI.__init__
    def _new_async_init(self, *args, **kwargs):
        kwargs['api_key'] = CEREBRAS_KEY
        kwargs['base_url'] = CEREBRAS_URL
        if 'http_client' in kwargs: del kwargs['http_client']
        _orig_async_init(self, *args, **kwargs)

    _orig_sync_init = OpenAI.__init__
    def _new_sync_init(self, *args, **kwargs):
        kwargs['api_key'] = CEREBRAS_KEY
        kwargs['base_url'] = CEREBRAS_URL
        if 'http_client' in kwargs: del kwargs['http_client']
        _orig_sync_init(self, *args, **kwargs)

    AsyncOpenAI.__init__ = _new_async_init
    OpenAI.__init__ = _new_sync_init

    # Also patch the global default clients if they exist
    openai.api_key = CEREBRAS_KEY
    openai.base_url = CEREBRAS_URL

    print(f"DEBUG: ALL OpenAI Clients (Sync/Async) Forced to Cerebras: {CEREBRAS_URL}")
    print(f"DEBUG: Using Key: {CEREBRAS_KEY[:5]}...{CEREBRAS_KEY[-5:] if CEREBRAS_KEY else 'None'}")
    print(f"DEBUG: Tracing DISABLED via OPENAI_AGENTS_DISABLE_TRACING=1")

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional


from database.queries import get_pool, close_pool
from src.agent.sentiment import SentimentAnalyzer

sentiment_analyzer = SentimentAnalyzer()

from kafka_client import kafka_producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import asyncio

async def poll_gmail_loop():
    """Background task to poll Gmail every 60 seconds."""
    from src.channels.gmail_handler import GmailHandler
    try:
        handler = GmailHandler()
        while True:
            try:
                # Fetch only unread messages (default query)
                messages = await handler.fetch_messages(query="is:unread")
                if messages:
                    for msg in messages:
                        logger.info(f"Background Gmail fetched message from {msg.customer_email}")
                        ticket_id, outbound = await process_direct_message(
                            channel="email",
                            content=msg.content,
                            customer_email=msg.customer_email,
                            customer_name=msg.customer_email.split('@')[0],
                            subject=msg.subject or "Support Inquiry",
                            thread_id=msg.metadata.get("thread_id"),
                            in_reply_to=msg.channel_message_id,
                            cc=msg.metadata.get("cc")
                        )
                        logger.info(f"Processed Gmail message: ticket {ticket_id}")
                else:
                    logger.debug("No unread Gmail messages found")
            except Exception as loop_e:
                logger.error(f"Error in Gmail poll loop: {loop_e}")
            await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"Failed to start Gmail background poller: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Customer Success FTE API...")
    bg_tasks = []
    try:
        await kafka_producer.start()
        await get_pool()
        # Start Gmail poller
        if os.getenv("GMAIL_POLLING_ENABLED", "true").lower() == "true":
            gmail_task = asyncio.create_task(poll_gmail_loop())
            bg_tasks.append(gmail_task)
            logger.info("Started Gmail background polling.")
        
        logger.info("API startup complete")
    except Exception as e:
        logger.error(f"Startup dependency error: {e}. Continuing in limited mode.")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Customer Success FTE API...")
    for t in bg_tasks:
        t.cancel()
    await kafka_producer.stop()
    await close_pool()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Customer Success FTE API",
    description="API for handling customer support across multiple channels",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }




async def process_direct_message(channel: str, content: str, customer_email: str = None, customer_phone: str = None, customer_name: str = "Unknown", subject: str = "Support Inquiry", thread_id: str = None, in_reply_to: str = None, cc: str = None, channel_message_id: str = None):
    """
    Helper function to process messages without Kafka.

    Pipeline:
    1. Resolve customer (get or create)
    2. Get or create conversation
    3. Store inbound message
    4. Run agent
    5. Store outbound message
    6. Send external response via channel (Gmail/WhatsApp)
    7. Record metrics
    """
    from agent.customer_success_agent import run_agent
    from database.queries import (
        create_customer, find_customer_by_email, find_customer_by_phone,
        create_conversation, store_message, record_metric,
        update_conversation_sentiment
    )
    from src.channels.gmail_handler import GmailHandler
    from src.channels.whatsapp_handler import WhatsAppHandler

    logger.info(f"🚀 Starting process_direct_message for {channel} from {customer_email or customer_phone}")
    
    start_time = datetime.utcnow()
    
    # Get database pool
    try:
        pool = await get_pool()
        logger.info(f"✅ Database pool obtained")
    except Exception as db_error:
        logger.error(f"❌ Failed to get database pool: {db_error}", exc_info=True)
        raise
    
    async with pool.acquire() as conn:
        # 1. Resolve customer
        customer = None
        if customer_email:
            customer = await find_customer_by_email(conn, customer_email)
        elif customer_phone:
            customer = await find_customer_by_phone(conn, customer_phone)

        if not customer:
            customer_id = await create_customer(conn, email=customer_email, phone=customer_phone, name=customer_name)
        else:
            customer_id = str(customer['id'])

        # 2. Start conversation
        conv_id = await create_conversation(conn, customer_id, channel)

        # 3. Store inbound
        role = "customer"
        await store_message(conn, conv_id, channel, "inbound", role, content)

        # 3.5 Sentiment Analysis
        sentiment_score, sentiment_label = sentiment_analyzer.analyze(content)
        await update_conversation_sentiment(conn, conv_id, sentiment_score)

        # 4. Run agent
        agent_result = await run_agent(
            message=content,
            context={"customer_id": customer_id, "conversation_id": conv_id, "channel": channel}
        )

        # 5. Store outbound
        outbound_content = agent_result.get("output", "")
        await store_message(
            conn=conn,
            conversation_id=conv_id,
            channel=channel,
            direction="outbound",
            role="agent",
            content=outbound_content,
            sentiment_score=sentiment_score
        )

        # 6. Explicit Ticket Creation (Sentiment-based or first message)
        # Check if conversation already has a ticket
        from database.queries import get_recent_tickets, create_ticket as db_create_ticket

        should_create_ticket = sentiment_analyzer.should_escalate(sentiment_score)

        if should_create_ticket:
            logger.info(f"Auto-creating ticket for {channel} due to sentiment {sentiment_score}")
            await db_create_ticket(
                conn=conn,
                customer_id=customer_id,
                conversation_id=conv_id,
                channel=channel,
                issue=subject if channel == "email" else content[:100],
                priority="high" if sentiment_score < 0.2 else "medium",
                category="sentiment_escalation"
            )

        # 7. Send External Response via Channel
        logger.info(f"📤 Attempting to send response via {channel}...")
        try:
            if channel == "email" and customer_email:
                gmail = GmailHandler()
                email_sent = await gmail.send_reply(
                    customer_email=customer_email,
                    subject=subject,
                    body=outbound_content,
                    thread_id=thread_id,
                    in_reply_to=in_reply_to,
                    cc=cc
                )
                if email_sent:
                    logger.info(f"✅ Email response sent to {customer_email}")
                else:
                    logger.warning(f"❌ Failed to send email response to {customer_email}")

            elif channel == "whatsapp" and customer_phone:
                logger.info(f"📱 Initializing WhatsApp handler...")
                whatsapp = WhatsAppHandler()
                
                logger.info(f"📱 Customer phone: {customer_phone}")
                logger.info(f"📱 Response body: {outbound_content[:100]}...")

                if channel_message_id:
                    await whatsapp.mark_message_read(channel_message_id)

                logger.info(f"📱 Sending WhatsApp message...")
                whatsapp_sent = await whatsapp.send_message(
                    customer_phone=customer_phone,
                    body=outbound_content
                )
                if whatsapp_sent:
                    logger.info(f"✅ WhatsApp response sent to {customer_phone}")
                else:
                    logger.warning(f"❌ Failed to send WhatsApp response to {customer_phone}")

            elif channel == "web_form":
                # For web form, send confirmation email if provided
                if customer_email:
                    gmail = GmailHandler()
                    email_sent = await gmail.send_reply(
                        customer_email=customer_email,
                        subject=f"Support Ticket: {subject}",
                        body=outbound_content
                    )
                    if email_sent:
                        logger.info(f"✅ Web form confirmation email sent to {customer_email}")
        except Exception as resp_error:
            logger.error(f"❌ Failed to send external response via {channel}: {resp_error}", exc_info=True)
            # Don't fail the whole process if response sending fails

        # 8. Record metric
        # 7. Record metrics
        try:
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            await record_metric(conn, "sentiment_score", sentiment_score, channel)
            await record_metric(conn, "latency_ms", float(latency_ms), channel)
            await record_metric(conn, "message_processed_direct", 1.0, channel)
            logger.info(f"Recorded metrics for {channel}: sentiment={sentiment_score}, latency={latency_ms}ms")
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

        return f"tkt_{conv_id[:8]}", outbound_content

@app.post("/support/submit")
async def submit_support_form(request: Request):
    """Web form submission endpoint."""
    try:
        data = await request.json()
        
        # Validate required fields
        required = ["name", "email", "subject", "message"]
        for field in required:
            if field not in data or not data[field]:
                raise HTTPException(status_code=422, detail=f"Missing required field: {field}")
        
        # Publish to Kafka or process directly
        event = {
            "type": "web_form_submission",
            "data": data,
        }
        
        kafka_enabled = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
        
        if kafka_enabled:
            await kafka_producer.publish("fte.channels.webform.inbound", event)
            ticket_id = f"ticket_{data['email']}_{id(event)}"
        else:
            # DIRECT PROCESSING (Kafka Bypass)
            logger.info(f"Direct processing web form for {data['email']}")
            ticket_id, outbound = await process_direct_message(
                channel="web_form",
                content=data['message'],
                customer_email=data['email'],
                customer_name=data['name']
            )
        
        return {
            "ticket_id": ticket_id,
            "message": "Your support request has been processed.",
            "response": outbound,
            "estimated_response_time": "Immediate" if not kafka_enabled else "Within 24 hours"
        }
        
    except Exception as e:
        logger.error(f"Support form submission failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/agent/chat")
async def agent_chat(request: Request):
    """Chat directly with the AI Agent."""
    try:
        data = await request.json()
        message = data.get("message")
        channel = data.get("channel", "web_form")
        
        # We can accept customer_id (UUID), email, or phone
        customer_id = data.get("customer_id")
        email = data.get("email")
        phone = data.get("phone")
        name = data.get("name", "Web User")
        
        if not message:
            raise HTTPException(status_code=422, detail="Missing message")
            
        from agent.customer_success_agent import run_agent
        from database.queries import (
            get_pool, create_conversation, store_message, 
            find_customer_by_email, find_customer_by_phone, create_customer
        )
        
        pool = await get_pool()
        async with pool.acquire() as conn:
            # 1. Resolve Customer ID (must be a UUID in the DB)
            resolved_customer_id = None
            
            # Try by provided ID if it looks like a UUID
            if customer_id:
                try:
                    import uuid
                    uuid.UUID(customer_id)
                    resolved_customer_id = customer_id
                except ValueError:
                    pass # Not a UUID, ignore it
            
            # Try by email if ID failed
            if not resolved_customer_id and email:
                cust = await find_customer_by_email(conn, email)
                if cust:
                    resolved_customer_id = str(cust['id'])
            
            # Try by phone
            if not resolved_customer_id and phone:
                cust = await find_customer_by_phone(conn, phone)
                if cust:
                    resolved_customer_id = str(cust['id'])
            
            # Fallback: Create a new customer or use a default one for web chat
            if not resolved_customer_id:
                # Use a stable email for "Anonymous Web User" if none provided
                web_email = email or f"web_{uuid.uuid4().hex[:8]}@anonymous.com"
                resolved_customer_id = await create_customer(
                    conn, 
                    email=web_email, 
                    name=name
                )
            
            # 2. Ensure conversation exists
            conv_id = await create_conversation(conn, resolved_customer_id, channel)
            
            # 3. Store inbound
            await store_message(conn, conv_id, channel, "inbound", "customer", message)
            
            # 4. Run Agent
            agent_result = await run_agent(
                message=message,
                context={
                    "customer_id": resolved_customer_id,
                    "conversation_id": conv_id,
                    "channel": channel
                }
            )
            
            # 5. Store outbound
            output = agent_result.get("output", "")
            await store_message(conn, conv_id, channel, "outbound", "agent", output)
            
            # 6. Extract tool names for frontend
            tool_calls = agent_result.get("tool_calls", [])
            tool_names = [tc.function.name for tc in tool_calls] if hasattr(tool_calls, "__iter__") else []
            
            return {
                "response": output,
                "tools": tool_names,
                "conversation_id": conv_id,
                "customer_id": resolved_customer_id,
                "ticket_id": f"TK-{conv_id[:8].upper()}"
            }
            
    except Exception as e:
        logger.error(f"Agent chat failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/support/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get ticket status by ID."""
    from database.queries import get_ticket_with_messages
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        ticket = await get_ticket_with_messages(conn, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "ticket_id": ticket_id,
        "status": ticket.get("status", "unknown"),
        "created_at": ticket.get("created_at"),
        "messages": ticket.get("messages", [])
    }


@app.get("/tickets")
async def get_tickets(limit: int = 50):
    """Get list of recent tickets."""
    from database.queries import get_recent_tickets
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        tickets = await get_recent_tickets(conn, limit)
    
    # Optional formatting for frontend, datetime to string
    for t in tickets:
        if 'time' in t and hasattr(t['time'], 'isoformat'):
            t['time'] = t['time'].isoformat()
            
    return {"tickets": tickets}


@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get channel metrics for the dashboard."""
    from database.queries import get_channel_metrics_last_24h
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        metrics = await get_channel_metrics_last_24h(conn)
            
    return {"metrics": metrics}


@app.get("/metrics/advanced")
async def get_advanced_analytics():
    """Get advanced metrics for the analytics dashboard."""
    from database.queries import get_advanced_metrics
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        metrics = await get_advanced_metrics(conn)
            
    return metrics


@app.get("/customers")
async def get_customers_list(limit: int = 50):
    """Get list of real customers."""
    from database.queries import get_real_customers
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        customers = await get_real_customers(conn, limit)
        
    for c in customers:
        if 'last_contact' in c and hasattr(c['last_contact'], 'isoformat'):
            c['last_contact'] = c['last_contact'].isoformat()
            
    return {"customers": customers}



@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook endpoint for Twilio WhatsApp.

    IMPORTANT: Twilio requires a TwiML XML response from webhooks.
    We return an empty <Response/> because the actual reply is sent
    via the Twilio REST API in process_direct_message().
    """
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
             form_data = await request.json()
        else:
             form_data = dict(await request.form())

        from src.channels.whatsapp_handler import WhatsAppHandler
        handler = WhatsAppHandler()

        msg = handler.parse_webhook(form_data)
        logger.info(f"📥 Received WhatsApp webhook from {msg.customer_phone}: {msg.content}")

        kafka_enabled = os.getenv("KAFKA_ENABLED", "true").lower() == "true"

        if kafka_enabled:
            event = {
                "type": "whatsapp_webhook",
                "data": {
                    "channel": "whatsapp",
                    "content": msg.content,
                    "customer_phone": msg.customer_phone,
                    "customer_name": msg.customer_name or "WhatsApp User",
                    "channel_message_id": msg.channel_message_id
                }
            }
            await kafka_producer.publish("fte.channels.whatsapp.inbound", event)
            logger.info(f"WhatsApp message published to Kafka")
            ticket_id = "pending_kafka"
            outbound = "Processing..."
        else:
            logger.info(f"🔄 Processing WhatsApp message directly (Kafka disabled)...")
            import asyncio
            # Run in the background to prevent Twilio webhook timeouts (requires response in <15s)
            asyncio.create_task(
                process_direct_message(
                    channel="whatsapp",
                    content=msg.content,
                    customer_phone=msg.customer_phone,
                    customer_name=msg.customer_name or "WhatsApp User",
                    channel_message_id=msg.channel_message_id
                )
            )
            logger.info("✅ WhatsApp processing started in background to prevent Twilio timeout.")

        # Return empty TwiML response — Twilio requires XML, not JSON.
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(content=twiml, media_type="text/xml")
        
    except Exception as e:
        logger.error(f"WhatsApp webhook failed: {e}", exc_info=True)
        # Even on error, return valid TwiML so Twilio doesn't retry
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(content=twiml, media_type="text/xml")


@app.get("/webhook/gmail/poll")
async def manual_gmail_poll(q: str = "is:unread"):
    """Manually trigger Gmail polling."""
    from src.channels.gmail_handler import GmailHandler
    try:
        handler = GmailHandler()
        messages = await handler.fetch_messages(query=q)

        kafka_enabled = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
        processed = []

        for msg in messages:
            logger.info(f"Polled Gmail message from {msg.customer_email}")
            
            if kafka_enabled:
                event = {
                    "type": "gmail_inbound",
                    "data": {
                        "channel": "email",
                        "content": msg.content,
                        "customer_email": msg.customer_email,
                        "customer_name": msg.customer_email.split('@')[0],
                        "subject": msg.subject or "Support Inquiry",
                        "thread_id": msg.metadata.get("thread_id"),
                        "in_reply_to": msg.channel_message_id,
                        "cc": msg.metadata.get("cc")
                    }
                }
                await kafka_producer.publish("fte.channels.email.inbound", event)
                processed.append({"id": msg.channel_message_id, "status": "published_to_kafka"})
            else:
                ticket_id, outbound = await process_direct_message(
                    channel="email",
                    content=msg.content,
                    customer_email=msg.customer_email,
                    customer_name=msg.customer_email.split('@')[0],
                    subject=msg.subject or "Support Inquiry",
                    thread_id=msg.metadata.get("thread_id"),
                    in_reply_to=msg.channel_message_id,
                    cc=msg.metadata.get("cc")
                )
                processed.append({
                    "id": msg.channel_message_id, 
                    "ticket_id": ticket_id,
                    "from": msg.customer_email,
                    "subject": msg.subject
                })

        return {
            "status": "success", 
            "total_fetched": len(messages), 
            "processed_count": len(processed), 
            "mode": "kafka" if kafka_enabled else "direct",
            "messages": processed
        }
    except Exception as e:
        logger.error(f"Manual Gmail poll failed: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}

# Include channel routers (would be implemented in separate files)
# from channels.web_form_handler import router as web_form_router
# app.include_router(web_form_router, prefix="/api")

