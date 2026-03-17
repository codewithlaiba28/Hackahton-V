"""Kafka message processor worker."""

import asyncio
import logging
from datetime import datetime

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageProcessor:
    """Process messages from Kafka and run the agent."""
    
    def __init__(self):
        self.consumer = FTEKafkaConsumer(
            topics=[TOPICS["tickets_incoming"]],
            group_id="fte-message-processor"
        )
    
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
                )
                
                # Step 6: Record metrics
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
