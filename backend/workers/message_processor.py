"""Kafka message processor worker."""

import asyncio
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

from database.queries import (
    get_pool,
    find_customer_by_email,
    find_customer_by_phone,
    create_customer,
    add_customer_identifier,
    get_active_conversation,
    create_conversation,
    store_message,
    create_ticket as db_create_ticket,
    record_metric,
)
from agent.customer_success_agent import run_agent
from kafka_client import FTEKafkaConsumer, kafka_producer, TOPICS
from src.channels.gmail_handler import GmailHandler
from src.channels.whatsapp_handler import WhatsAppHandler
from src.agent.sentiment import SentimentAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageProcessor:
    """Process messages from Kafka and run the agent."""
    
    def __init__(self):
        self.consumer = FTEKafkaConsumer(
            topics=[TOPICS["tickets_incoming"]],
            group_id="fte-message-processor"
        )
        # Initialize handlers
        self.gmail_handler = GmailHandler()
        self.whatsapp_handler = WhatsAppHandler()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def start(self):
        """Start the message processor."""
        await self.consumer.start()
        await self.consumer.consume(self.process_message)
    
    async def stop(self):
        """Stop the message processor."""
        await self.consumer.stop()
    
    async def process_message(self, topic: str, message: dict):
        """
        Process a single message from Kafka.
        
        Pipeline:
        1. Resolve customer (get or create)
        2. Get or create conversation
        3. Store inbound message
        4. Run agent
        5. Store outbound message
        6. Record metrics
        7. Commit Kafka offset (only after successful DB write)
        """
        start_time = datetime.utcnow()
        
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                # Extract message data
                data = message.get("data", {})
                channel = data.get("channel", "web_form")
                content = data.get("content", "")
                customer_email = data.get("customer_email")
                customer_phone = data.get("customer_phone")
                
                # Step 1: Resolve customer
                customer = await self.resolve_customer(
                    conn, customer_email, customer_phone
                )
                customer_id = customer["id"]
                
                # Step 2: Get or create conversation
                conv_id = await self.get_or_create_conversation(
                    conn, customer_id, channel
                )
                
                # Step 3: Store inbound message
                await store_message(
                    conn=conn,
                    conversation_id=conv_id,
                    channel=channel,
                    direction="inbound",
                    role="customer",
                    content=content,
                )
                
                # Step 3.5: Sentiment Analysis
                sentiment_score, sentiment_label = self.sentiment_analyzer.analyze(content)
                
                # Step 4: Run agent
                agent_result = await run_agent(
                    message=content,
                    context={
                        "customer_id": customer_id,
                        "conversation_id": conv_id,
                        "channel": channel,
                    }
                )
                
                # Step 5: Store outbound message
                latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                await store_message(
                    conn=conn,
                    conversation_id=conv_id,
                    channel=channel,
                    direction="outbound",
                    role="agent",
                    content=agent_result.get("output", ""),
                    latency_ms=latency_ms,
                    sentiment_score=sentiment_score
                )
                
                # Step 5.5: Implicit Escalation Check
                if self.sentiment_analyzer.should_escalate(sentiment_score):
                    logger.warning(f"Implicit escalation for customer {customer_id} due to sentiment {sentiment_score}")
                    await db_create_ticket(
                        conn=conn,
                        customer_id=customer_id,
                        conversation_id=conv_id,
                        channel=channel,
                        issue=f"Implicit Escalation: {content[:100]}",
                        priority="high",
                        category="sentiment_escalation"
                    )

                # Step 6: Send Response (External)
                await self.send_external_response(
                    channel=channel,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    subject=data.get("subject", "Support Update"),
                    body=agent_result.get("output", ""),
                    thread_id=data.get("thread_id")
                )

                # Step 7: Record metrics
                await record_metric(
                    conn=conn,
                    metric_name="message_processed",
                    metric_value=1.0,
                    channel=channel,
                    dimensions={"latency_ms": latency_ms}
                )
                
                logger.info(f"Processed message for customer {customer_id} in {latency_ms}ms")
                
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            # Do NOT commit offset - message will be redelivered
            raise
    
    async def send_external_response(self, channel, customer_email, customer_phone, subject, body, thread_id=None):
        """Send response back to the customer channel."""
        try:
            if channel == "email" and customer_email:
                await self.gmail_handler.send_response(customer_email, subject, body, thread_id)
            elif channel == "whatsapp" and customer_phone:
                await self.whatsapp_handler.send_response(customer_phone, body)
            elif channel == "web_form":
                # For web form, the response is typically retrieved via status API
                # but we can also send a confirmation email if provided
                if customer_email:
                    await self.gmail_handler.send_response(customer_email, f"Support Ticket: {subject}", body)
            
            logger.info(f"Response sent to {channel}")
        except Exception as e:
            logger.error(f"Failed to send external response to {channel}: {e}")

    async def resolve_customer(self, conn, email: str = None, phone: str = None):
        """Get or create customer by email or phone."""
        # Try to find by email
        if email:
            customer = await find_customer_by_email(conn, email)
            if customer:
                return customer
        
        # Try to find by phone
        if phone:
            customer = await find_customer_by_phone(conn, phone)
            if customer:
                return customer
        
        # Create new customer
        customer_id = await create_customer(
            conn=conn,
            email=email,
            phone=phone,
        )
        
        # Add identifiers for cross-channel lookup
        if email:
            await add_customer_identifier(conn, customer_id, "email", email)
        if phone:
            await add_customer_identifier(conn, customer_id, "phone", phone)
        
        return {"id": customer_id, "email": email, "phone": phone}
    
    async def get_or_create_conversation(self, conn, customer_id: str, channel: str):
        """Get active conversation or create new one."""
        conv = await get_active_conversation(conn, customer_id, channel)
        
        if conv:
            return str(conv["id"])
        
        return await create_conversation(conn, customer_id, channel)


async def main():
    """Main entry point."""
    processor = MessageProcessor()
    
    try:
        await processor.start()
    except KeyboardInterrupt:
        await processor.stop()


if __name__ == "__main__":
    asyncio.run(main())
