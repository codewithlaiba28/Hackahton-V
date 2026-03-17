"""FastAPI application for Phase 2."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

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
        
        # Publish to Kafka
        event = {
            "type": "web_form_submission",
            "data": data,
        }
        await kafka_producer.publish("fte.channels.webform.inbound", event)
        
        # Create ticket (simplified - full implementation would use agent)
        ticket_id = f"ticket_{data['email']}_{id(event)}"
        
        return {
            "ticket_id": ticket_id,
            "message": "Thank you! Your support request has been submitted.",
            "estimated_response_time": "Within 24 hours"
        }
        
    except Exception as e:
        logger.error(f"Support form submission failed: {e}")
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


# Include channel routers (would be implemented in separate files)
# from channels.web_form_handler import router as web_form_router
# app.include_router(web_form_router, prefix="/api")
