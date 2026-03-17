"""Kafka client for Phase 2."""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Topic names
TOPICS = {
    "email_inbound": "fte.channels.email.inbound",
    "whatsapp_inbound": "fte.channels.whatsapp.inbound",
    "webform_inbound": "fte.channels.webform.inbound",
    "tickets_incoming": "fte.tickets.incoming",
    "email_outbound": "fte.channels.email.outbound",
    "whatsapp_outbound": "fte.channels.whatsapp.outbound",
    "escalations": "fte.escalations",
    "metrics": "fte.metrics",
    "dlq": "fte.dlq",
}


class FTEKafkaProducer:
    """Kafka producer for publishing events."""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        ).split(",")
        self.producer = None
        self.enabled = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
    
    async def start(self):
        """Start the producer."""
        if not self.enabled:
            logger.info("Kafka disabled, using file-based fallback")
            return
        
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
        )
        await self.producer.start()
        logger.info("Kafka producer started")
    
    async def stop(self):
        """Stop the producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def publish(self, topic: str, event: Dict[str, Any]):
        """Publish an event to a topic."""
        event["timestamp"] = datetime.utcnow().isoformat()
        
        if not self.enabled or not self.producer:
            # Fallback: log to file
            logger.info(f"[KAFKA FALLBACK] {topic}: {event}")
            return
        
        try:
            await self.producer.send_and_wait(topic, event)
            logger.debug(f"Published to {topic}: {event.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            # Publish to DLQ
            await self.publish_dlq(event, str(e))
    
    async def publish_dlq(self, event: Dict[str, Any], error: str):
        """Publish to dead letter queue."""
        dlq_event = {
            "original_event": event,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.publish(TOPICS["dlq"], dlq_event)


class FTEKafkaConsumer:
    """Kafka consumer for processing events."""
    
    def __init__(self, topics: list, group_id: str):
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        ).split(",")
        self.topics = topics
        self.group_id = group_id
        self.consumer = None
        self.enabled = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
    
    async def start(self):
        """Start the consumer."""
        if not self.enabled:
            logger.info("Kafka disabled, consumer not started")
            return
        
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=False,
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started (topics: {self.topics})")
    
    async def stop(self):
        """Stop the consumer."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def consume(self, handler: Callable):
        """Consume messages and call handler for each."""
        if not self.enabled or not self.consumer:
            logger.warning("Kafka not enabled, consumer not running")
            return
        
        async for msg in self.consumer:
            try:
                await handler(msg.topic, msg.value)
                # Commit offset ONLY after successful processing
                await self.consumer.commit()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Do NOT commit offset - message will be redelivered


# Global producer instance
kafka_producer = FTEKafkaProducer()
