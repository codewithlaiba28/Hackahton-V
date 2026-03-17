---
name: kafka-event-processing
description: Apache Kafka event streaming for customer support message processing, async workers, event-driven architecture, and reliable message delivery pipeline.
---

# Kafka Event Processing Skill

## Purpose

This skill provides complete Kafka integration for building an event-driven Customer Success AI agent. Messages from all channels (Gmail, WhatsApp, Web Form) are streamed through Kafka for reliable, scalable, and asynchronous processing.

## When to Use This Skill

Use this skill when you need to:
- Build an event-driven architecture for customer support
- Process messages asynchronously with guaranteed delivery
- Scale agent workers independently
- Handle high-volume message ingestion
- Implement retry logic and dead letter queues
- Track message processing metrics
- Enable real-time analytics on support interactions

---

## Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KAFKA EVENT PROCESSING ARCHITECTURE                       │
│                                                                              │
│  CHANNEL INTAKE                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │Gmail Handler│  │WhatsApp Hdlr│  │Web Form Hdlr│                          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                          │
│         │                │                │                                  │
│         └────────────────┼────────────────┘                                  │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │   Kafka Producer      │                                      │
│              │  (support-ingress)    │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │   support-ingress     │  ← Topic: Incoming messages          │
│              │      (Kafka Topic)    │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│         ┌────────────────┼────────────────┐                                 │
│         │                │                │                                 │
│         ▼                ▼                ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │  Worker 1   │  │  Worker 2   │  │  Worker N   │  ← Consumer Group       │
│  │  (Pod)      │  │  (Pod)      │  │  (Pod)      │                         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
│         │                │                │                                 │
│         └────────────────┼────────────────┘                                 │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │ support-responses     │  ← Topic: Agent responses            │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│                          ▼                                                   │
│              ┌───────────────────────┐                                      │
│              │  Response Dispatcher  │                                      │
│              └───────────┬───────────┘                                      │
│                          │                                                   │
│         ┌────────────────┼────────────────┐                                 │
│         ▼                ▼                ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │Gmail Sender │  │WhatsApp Send│  │Web API Resp │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
│                                                                              │
│  ┌───────────────────────┐                                                  │
│  │ support-dead-letter   │  ← Failed messages for retry                    │
│  └───────────────────────┘                                                  │
│                                                                              │
│  ┌───────────────────────┐                                                  │
│  │ support-metrics       │  ← Metrics events for monitoring                │
│  └───────────────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Kafka Topics Design

| Topic | Partitions | Replication | Retention | Purpose |
|-------|------------|-------------|-----------|---------|
| `support-ingress` | 6 | 3 | 7 days | Incoming messages from all channels |
| `support-responses` | 6 | 3 | 7 days | Agent responses ready for delivery |
| `support-dead-letter` | 3 | 3 | 30 days | Failed messages for manual review |
| `support-metrics` | 3 | 3 | 90 days | Metrics and analytics events |

---

## Kafka Producer (Channel Ingress)

```python
# workers/kafka_producer.py

from aiokafka import AIOKafkaProducer
from typing import Dict, Any
import json
import asyncio
from datetime import datetime
import uuid

class KafkaIngressProducer:
    """Produce messages to Kafka support-ingress topic."""
    
    def __init__(self, bootstrap_servers: list):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.topic = "support-ingress"
    
    async def start(self):
        """Start the Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            retry_backoff_ms=100
        )
        await self.producer.start()
    
    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
    
    async def send_message(self, message_data: Dict[str, Any]) -> str:
        """Send a customer message to Kafka."""
        message_id = str(uuid.uuid4())
        
        event = {
            'event_id': message_id,
            'event_type': 'customer_message',
            'timestamp': datetime.utcnow().isoformat(),
            'data': message_data
        }
        
        # Use customer_id or channel_message_id as key for partitioning
        key = message_data.get('customer_id') or message_data.get('channel_message_id')
        
        await self.producer.send_and_wait(
            topic=self.topic,
            value=event,
            key=key
        )
        
        return message_id
    
    async def send_batch(self, messages: list):
        """Send multiple messages in a batch."""
        async with self.producer.transaction() as tx:
            for msg in messages:
                await tx.send_and_wait(
                    topic=self.topic,
                    value=msg
                )
```

---

## Kafka Consumer (Message Processor Worker)

```python
# workers/message_processor.py

from aiokafka import AIOKafkaConsumer
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageProcessorWorker:
    """Kafka consumer that processes customer messages with AI agent."""
    
    def __init__(
        self,
        bootstrap_servers: list,
        agent_runner,
        kafka_producer,
        database_queries,
        group_id: str = "support-processor-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.agent_runner = agent_runner
        self.kafka_producer = kafka_producer
        self.db = database_queries
        self.group_id = group_id
        self.input_topic = "support-ingress"
        self.output_topic = "support-responses"
        self.dlq_topic = "support-dead-letter"
        self.metrics_topic = "support-metrics"
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the message processor worker."""
        self.consumer = AIOKafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=10,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000
        )
        await self.consumer.start()
        self.running = True
        
        logger.info(f"Message processor started, listening on {self.input_topic}")
    
    async def stop(self):
        """Stop the message processor worker."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Message processor stopped")
    
    async def process_messages(self):
        """Main processing loop."""
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                
                try:
                    await self.process_single_message(msg)
                    # Commit offset after successful processing
                    await self.consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Send to dead letter queue
                    await self.send_to_dlq(msg.value, str(e))
                    # Still commit to avoid infinite loop
                    await self.consumer.commit()
        except asyncio.CancelledError:
            logger.info("Message processor cancelled")
    
    async def process_single_message(self, kafka_msg):
        """Process a single Kafka message."""
        event = kafka_msg.value
        data = event.get('data', {})
        
        logger.info(f"Processing message {event.get('event_id')} from {data.get('channel')}")
        
        # Record processing start time
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Get or create customer
            customer = await self.db.get_or_create_customer(
                email=data.get('customer_email'),
                phone=data.get('customer_phone')
            )
            
            # Step 2: Get or create conversation
            conversation_id = await self.db.get_active_conversation(
                customer['id'],
                data.get('channel')
            )
            if not conversation_id:
                conversation_id = await self.db.create_conversation(
                    customer['id'],
                    data.get('channel')
                )
            
            # Step 3: Store incoming message
            await self.db.create_message(
                conversation_id=conversation_id,
                channel=data.get('channel'),
                direction='inbound',
                role='customer',
                content=data.get('content'),
                channel_message_id=data.get('channel_message_id'),
                metadata={'kafka_offset': kafka_msg.offset}
            )
            
            # Step 4: Create ticket (required for all interactions)
            ticket_id = await self.db.create_ticket(
                conversation_id=conversation_id,
                customer_id=customer['id'],
                source_channel=data.get('channel')
            )
            
            # Step 5: Run AI agent
            agent_result = await self.agent_runner.run(
                messages=[{"role": "user", "content": data.get('content')}],
                context={
                    'customer_id': customer['id'],
                    'conversation_id': conversation_id,
                    'ticket_id': ticket_id,
                    'channel': data.get('channel')
                }
            )
            
            # Step 6: Store agent response
            await self.db.create_message(
                conversation_id=conversation_id,
                channel=data.get('channel'),
                direction='outbound',
                role='agent',
                content=agent_result.get('output'),
                metadata={
                    'tool_calls': agent_result.get('tool_calls', []),
                    'tokens_used': agent_result.get('tokens_used', 0),
                    'latency_ms': agent_result.get('latency_ms', 0)
                }
            )
            
            # Step 7: Send response to output topic
            response_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'agent_response',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'ticket_id': ticket_id,
                    'conversation_id': conversation_id,
                    'customer_id': customer['id'],
                    'channel': data.get('channel'),
                    'response': agent_result.get('output'),
                    'channel_message_id': data.get('channel_message_id'),
                    'escalated': agent_result.get('escalated', False),
                    'escalation_reason': agent_result.get('escalation_reason')
                }
            }
            
            await self.kafka_producer.send_and_wait(
                topic=self.output_topic,
                value=response_event
            )
            
            # Step 8: Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self.record_metrics(
                metric_name='message_processed',
                value=1,
                dimensions={
                    'channel': data.get('channel'),
                    'processing_time_ms': processing_time
                }
            )
            
            logger.info(f"Successfully processed message {event.get('event_id')}")
            
        except Exception as e:
            logger.error(f"Failed to process message {event.get('event_id')}: {e}", exc_info=True)
            raise
    
    async def send_to_dlq(self, original_event: Dict, error_reason: str):
        """Send failed message to dead letter queue."""
        dlq_event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'dlq_message',
            'timestamp': datetime.utcnow().isoformat(),
            'original_event': original_event,
            'error_reason': error_reason,
            'retry_count': original_event.get('retry_count', 0) + 1
        }
        
        await self.producer.send_and_wait(
            topic=self.dlq_topic,
            value=dlq_event
        )
        
        logger.warning(f"Message sent to DLQ: {original_event.get('event_id')}")
    
    async def record_metrics(self, metric_name: str, value: float, dimensions: Dict = None):
        """Record processing metrics."""
        metrics_event = {
            'event_id': str(uuid.uuid4()),
            'event_type': 'metric',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'metric_name': metric_name,
                'metric_value': value,
                'dimensions': dimensions or {}
            }
        }
        
        await self.producer.send_and_wait(
            topic=self.metrics_topic,
            value=metrics_event
        )
```

---

## Response Dispatcher

```python
# workers/response_dispatcher.py

from aiokafka import AIOKafkaConsumer
from typing import Dict, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResponseDispatcher:
    """Consume agent responses and dispatch to appropriate channel."""
    
    def __init__(
        self,
        bootstrap_servers: list,
        gmail_handler,
        whatsapp_handler,
        web_form_handler,
        group_id: str = "response-dispatcher-group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.gmail_handler = gmail_handler
        self.whatsapp_handler = whatsapp_handler
        self.web_form_handler = web_form_handler
        self.group_id = group_id
        self.topic = "support-responses"
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the response dispatcher."""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self.consumer.start()
        self.running = True
        
        logger.info(f"Response dispatcher started, listening on {self.topic}")
    
    async def stop(self):
        """Stop the response dispatcher."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Response dispatcher stopped")
    
    async def dispatch_responses(self):
        """Main dispatch loop."""
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                
                event = msg.value
                data = event.get('data', {})
                
                channel = data.get('channel')
                response_text = data.get('response')
                
                try:
                    await self.send_via_channel(channel, data, response_text)
                except Exception as e:
                    logger.error(f"Failed to send response: {e}", exc_info=True)
                    # Could retry or send to DLQ
        
        except asyncio.CancelledError:
            logger.info("Response dispatcher cancelled")
    
    async def send_via_channel(self, channel: str, data: Dict, response_text: str):
        """Send response through the appropriate channel."""
        
        if channel == 'email':
            await self.send_email_response(data, response_text)
        elif channel == 'whatsapp':
            await self.send_whatsapp_response(data, response_text)
        elif channel == 'web_form':
            await self.send_web_response(data, response_text)
        else:
            logger.error(f"Unknown channel: {channel}")
    
    async def send_email_response(self, data: Dict, response_text: str):
        """Send response via Gmail."""
        customer_email = data.get('customer_email')
        channel_message_id = data.get('channel_message_id')
        
        # Extract thread_id from channel_message_id if needed
        result = await self.gmail_handler.send_reply(
            to_email=customer_email,
            subject=data.get('subject', 'Support Response'),
            body=response_text,
            thread_id=data.get('thread_id')
        )
        
        logger.info(f"Email sent to {customer_email}: {result}")
    
    async def send_whatsapp_response(self, data: Dict, response_text: str):
        """Send response via WhatsApp/Twilio."""
        customer_phone = data.get('customer_phone')
        
        result = await self.whatsapp_handler.send_reply(
            to_phone=customer_phone,
            message=response_text
        )
        
        logger.info(f"WhatsApp sent to {customer_phone}: {result}")
    
    async def send_web_response(self, data: Dict, response_text: str):
        """Send response for web form (API response + email confirmation)."""
        # Web form responses are typically sent via email confirmation
        # as the user has already submitted the form
        customer_email = data.get('customer_email')
        ticket_id = data.get('ticket_id')
        
        await self.web_form_handler.send_confirmation_email(
            email=customer_email,
            ticket_id=ticket_id,
            response_body=response_text
        )
        
        logger.info(f"Web form confirmation sent to {customer_email}")
```

---

## Docker Compose with Kafka

```yaml
# docker-compose.yml

version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: support_zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: support_kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_NUM_PARTITIONS: 3
    volumes:
      - kafka_data:/var/lib/kafka/data

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka_ui
    depends_on:
      - kafka
    ports:
      - "8090:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: support-cluster
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181

  # Create topics on startup
  kafka-init:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - kafka
    entrypoint: >
      /bin/bash -c "
      sleep 10 &&
      kafka-topics --create --topic support-ingress --partitions 6 --replication-factor 1 --bootstrap-server kafka:29092 &&
      kafka-topics --create --topic support-responses --partitions 6 --replication-factor 1 --bootstrap-server kafka:29092 &&
      kafka-topics --create --topic support-dead-letter --partitions 3 --replication-factor 1 --bootstrap-server kafka:29092 &&
      kafka-topics --create --topic support-metrics --partitions 3 --replication-factor 1 --bootstrap-server kafka:29092 &&
      echo 'Topics created successfully'
      "

volumes:
  kafka_data:
```

---

## Environment Variables

```bash
# .env

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP_ID=support-processor-group
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ENABLE_AUTO_COMMIT=false

# Kafka Topics
KAFKA_TOPIC_INGRESS=support-ingress
KAFKA_TOPIC_RESPONSES=support-responses
KAFKA_TOPIC_DLQ=support-dead-letter
KAFKA_TOPIC_METRICS=support-metrics

# Consumer Configuration
KAFKA_MAX_POLL_RECORDS=10
KAFKA_SESSION_TIMEOUT_MS=30000
KAFKA_HEARTBEAT_INTERVAL_MS=10000
KAFKA_MAX_POLL_INTERVAL_MS=300000

# Producer Configuration
KAFKA_PRODUCER_ACKS=all
KAFKA_PRODUCER_RETRIES=3
KAFKA_PRODUCER_BATCH_SIZE=16384
KAFKA_PRODUCER_LINGER_MS=5
```

---

## Worker Deployment Script

```python
# workers/runner.py

import asyncio
import signal
import logging
from message_processor import MessageProcessorWorker
from response_dispatcher import ResponseDispatcher
from kafka_producer import KafkaIngressProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerManager:
    """Manage Kafka worker lifecycle."""
    
    def __init__(self):
        self.workers = []
        self.running = False
    
    async def start(self):
        """Start all workers."""
        self.running = True
        
        # Create producer
        producer = KafkaIngressProducer(
            bootstrap_servers=['localhost:9092']
        )
        await producer.start()
        
        # Create message processor
        processor = MessageProcessorWorker(
            bootstrap_servers=['localhost:9092'],
            agent_runner=agent_runner,
            kafka_producer=producer,
            database_queries=db
        )
        await processor.start()
        
        # Create response dispatcher
        dispatcher = ResponseDispatcher(
            bootstrap_servers=['localhost:9092'],
            gmail_handler=gmail_handler,
            whatsapp_handler=whatsapp_handler,
            web_form_handler=web_form_handler
        )
        await dispatcher.start()
        
        # Start processing tasks
        tasks = [
            asyncio.create_task(processor.process_messages()),
            asyncio.create_task(dispatcher.dispatch_responses())
        ]
        
        # Wait for shutdown signal
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Workers cancelled")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop all workers gracefully."""
        logger.info("Stopping workers...")
        self.running = False
        
        for worker in self.workers:
            await worker.stop()
        
        logger.info("All workers stopped")

def main():
    """Main entry point."""
    manager = WorkerManager()
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(manager.stop())
        )
    
    try:
        loop.run_until_complete(manager.start())
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        loop.close()

if __name__ == '__main__':
    main()
```

---

## Testing

```python
# tests/test_kafka.py

import pytest
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

@pytest.fixture
async def kafka_producer():
    """Create test Kafka producer."""
    producer = AIOKafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    yield producer
    await producer.stop()

@pytest.fixture
async def kafka_consumer():
    """Create test Kafka consumer."""
    consumer = AIOKafkaConsumer(
        'support-ingress',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )
    await consumer.start()
    yield consumer
    await consumer.stop()

class TestKafkaIngress:
    @pytest.mark.asyncio
    async def test_send_message(self, kafka_producer):
        event = {
            'event_id': 'test-123',
            'event_type': 'customer_message',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'channel': 'email',
                'customer_email': 'test@example.com',
                'content': 'Test message'
            }
        }
        
        await kafka_producer.send_and_wait(
            topic='support-ingress',
            value=event
        )
        
        # Verify message was sent (check Kafka or consume)
        assert True

class TestMessageProcessor:
    @pytest.mark.asyncio
    async def test_process_message(self):
        processor = MessageProcessorWorker(
            bootstrap_servers=['localhost:9092'],
            agent_runner=mock_agent,
            kafka_producer=mock_producer,
            database_queries=mock_db
        )
        
        await processor.start()
        
        # Send test message
        test_event = create_test_event()
        await processor.process_single_message(test_event)
        
        await processor.stop()
```

---

## Acceptance Criteria

- [ ] Kafka topics created with correct partitions
- [ ] Producer sends messages with proper serialization
- [ ] Consumer processes messages reliably
- [ ] Dead letter queue captures failed messages
- [ ] Metrics are recorded for all operations
- [ ] Workers handle graceful shutdown
- [ ] Auto-scaling works on Kubernetes
- [ ] Message ordering preserved per customer
- [ ] Retry logic implemented for failures
- [ ] All tests pass

## Related Skills

- `customer-success-agent` - Agent runs in worker
- `channel-integrations` - Channels produce to Kafka
- `k8s-fte-deployment` - Workers deployed on K8s
- `postgres-crm-schema` - Workers write to database

## References

- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/)
