"""FastAPI application for Phase 2."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()  # Also try default .env

from database.queries import get_pool, close_pool

from kafka_client import kafka_producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Customer Success FTE API...")
    await kafka_producer.start()
    await get_pool()
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Customer Success FTE API...")
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


@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get channel performance metrics for last 24 hours."""
    from database.queries import get_channel_metrics_last_24h
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        metrics = await get_channel_metrics_last_24h(conn)
    
    return {"metrics": metrics}


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
            logger.info(f"Direct processing message for {data['email']}")
            from agent.customer_success_agent import run_agent
            from database.queries import create_customer, find_customer_by_email, create_conversation, store_message, record_metric
            
            pool = await get_pool()
            async with pool.acquire() as conn:
                # 1. Resolve customer
                customer = await find_customer_by_email(conn, data['email'])
                if not customer:
                    customer_id = await create_customer(conn, email=data['email'], name=data['name'])
                else:
                    customer_id = str(customer['id'])
                
                # 2. Start conversation
                conv_id = await create_conversation(conn, customer_id, "web_form")
                
                # 3. Store inbound
                await store_message(conn, conv_id, "web_form", "inbound", "customer", data['message'])
                
                # 4. Run agent
                agent_result = await run_agent(
                    message=data['message'],
                    context={"customer_id": customer_id, "conversation_id": conv_id, "channel": "web_form"}
                )
                
                # 5. Store outbound
                await store_message(conn, conv_id, "web_form", "outbound", "agent", agent_result.get("output", ""))
                
                # 6. Record metric
                await record_metric(conn, "message_processed_direct", 1.0, "web_form")
                
                # Extract ticket ID if created by tool (simplified)
                ticket_id = f"tkt_{conv_id[:8]}"
        
        return {
            "ticket_id": ticket_id,
            "message": "Thank you! Your support request has been submitted and processed.",
            "estimated_response_time": "Immediate" if not kafka_enabled else "Within 24 hours"
        }
        
    except Exception as e:
        logger.error(f"Support form submission failed: {e}")
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


# Include channel routers (would be implemented in separate files)
# from channels.web_form_handler import router as web_form_router
# app.include_router(web_form_router, prefix="/api")

