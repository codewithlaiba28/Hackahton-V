# Implementation Plan: Phase 3 Integration Testing

**Branch**: `phase3-integration` | **Date**: 2026-03-17 | **Spec**: specs/phase3-integration/spec.md

**Input**: Complete specification for Phase 3 — Integration Testing, Load Testing, and 24-Hour Continuous Operation Test

---

## Summary

Build comprehensive test infrastructure for Phase 3 validation:
- Multi-channel E2E tests (7 scenarios: A1-A5, B1-B2)
- Escalation path tests (5 scenarios: C1-C5)
- Agent behavior tests (5 scenarios: D1-D5)
- Load tests with Locust (2 scenarios: E1-E2)
- Resilience tests (3 scenarios: F1-F3)
- 24-hour continuous operation test with chaos injection (G1)
- Complete documentation suite (10 deliverables)

---

## Technical Context

**Test Framework**: pytest (unit/integration), Locust (load), custom scripts (chaos)
**Live System**: Docker Compose or Kubernetes deployment
**Evidence Collection**: PostgreSQL queries, kubectl logs, Locust HTML reports
**Performance Goals**: 0% failure rate, P95 < 3s latency, > 99.9% uptime
**Constraints**: All tests run against live deployed system (no mocks except external APIs)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 3 Constitution (v3.0.0) Compliance

- [x] **Test Reality, Not Mocks**: All tests run against live Docker Compose/Kubernetes
- [x] **Evidence-First Validation**: All metrics from PostgreSQL agent_metrics and messages tables
- [x] **Failure is Information**: All failures documented in specs/phase3-test-results.md
- [x] **SLA Targets are Hard Floors**: All 6 hard floors enforced (uptime, latency, loss, escalation, ID accuracy, web form latency)
- [x] **Chaos Is Required**: Pod kills every 2 hours for 24-hour test
- [x] **Documentation Completes the System**: All 10 deliverables required

### Phase 2 Constitution (v2.0.0) Compliance

- [x] **No Single Point of Failure**: Tested via pod kill scenarios
- [x] **Async-First Mandate**: All test helpers use async/await
- [x] **Channel Isolation**: Each channel tested independently
- [x] **Secret Management Law**: Test credentials in .env (not committed)
- [x] **Observability Requirement**: All metrics collected and validated
- [x] **Graceful Degradation Law**: Retries and DLQ tested
- [x] **Web Form Required**: Web form tests included

### Phase 1 Constitution (v1.0.0) Compliance

- [x] **Specification-First Law**: This plan follows approved spec
- [x] **Channel-Awareness Mandate**: All channels tested
- [x] **Director-Agent Contract**: Developer reviews test results
- [x] **Documentation-Concurrent**: Test docs written with tests
- [x] **Fail-Safe by Default**: Error handling tested
- [x] **Data Integrity Rules**: Cross-channel ID tested
- [x] **Guardrail Constraints**: All escalations tested

**Constitution Status**: ✅ ALL GATES PASS

---

## Project Structure

### Test Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3 TEST ARCHITECTURE                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   TEST RUNNER LAYER                       │   │
│  │   pytest (unit/integration)  |  Locust (load)            │   │
│  │   simulate_24h.py (chaos)    |  kubectl (K8s ops)        │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │               LIVE SYSTEM UNDER TEST                       │  │
│  │                                                            │  │
│  │   FastAPI (3 pods)    Worker (3 pods)    PostgreSQL        │  │
│  │   Kafka               pgvector           HPA               │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────▼────────────────────────────────────┐  │
│  │               EVIDENCE COLLECTION LAYER                    │  │
│  │                                                            │  │
│  │   specs/phase3-test-results.md    (failures log)          │  │
│  │   specs/24h-metrics-report.md     (SQL query results)     │  │
│  │   kubectl logs                    (pod logs)              │  │
│  │   Locust HTML report              (load test evidence)    │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Test Execution Order

| Phase | Tests | Hours | Blocking Gate |
|-------|-------|-------|---------------|
| **3A** | Pre-flight checks | 41.0–41.5 | All systems green |
| **3B** | Channel integration tests (A1–A5) | 41.5–42.5 | All A-tests pass |
| **3C** | Cross-channel + escalation tests (B1–B2, C1–C5) | 42.5–43.5 | All B,C-tests pass |
| **3D** | Agent behavior + edge cases (D1–D5) | 43.5–44.0 | All D-tests pass |
| **3E** | Load tests (E1–E2) | 44.0–45.0 | All SLA targets met |
| **3F** | Resilience tests (F1–F3) | 45.0–46.0 | All F-tests pass |
| **3G** | 24-hour setup + launch | 46.0–46.5 | Simulation running |
| **3H** | Documentation sprint | 46.5–48.0 | All docs complete |
| **3I** | 24-hour metrics validation | Hour 48+ | All G1 criteria met |

---

## Phase 0: Research & Test Infrastructure Setup

### Research Tasks

1. **Locust Load Testing Best Practices**
   - Research optimal user simulation patterns
   - Document weight/wait_time configuration
   - Identify HTML report generation options

2. **Kubernetes Chaos Testing Patterns**
   - Research kubectl pod delete patterns
   - Document self-healing verification strategies
   - Identify metrics to track during chaos

3. **PostgreSQL Percentile Queries**
   - Research PERCENTILE_CONT syntax
   - Document P95/P99 query patterns
   - Identify performance optimization for large datasets

4. **Kafka Message Injection Patterns**
   - Research aiokafka producer best practices
   - Document idempotent message injection
   - Identify offset management strategies

### Research Output: research.md

All research findings consolidated in `research.md` with:
- Decision: What was chosen
- Rationale: Why chosen
- Alternatives considered: What else evaluated

---

## Phase 1: Test Infrastructure & Contracts

### Test Helper Utilities

#### 3.1 Kafka Message Injector (`tests/helpers/kafka_injector.py`)

For tests that simulate email and WhatsApp without real API credentials:

```python
# tests/helpers/kafka_injector.py

from kafka_client import FTEKafkaProducer, TOPICS
from datetime import datetime
import uuid

class KafkaMessageInjector:
    """Inject test messages directly into Kafka topics, bypassing webhook handlers."""

    def __init__(self):
        self.producer = FTEKafkaProducer()

    async def inject_email(self, email: str, subject: str, body: str,
                            name: str = "Test User") -> str:
        """Inject a simulated email message into the processing pipeline."""
        message_id = str(uuid.uuid4())
        await self.producer.publish(TOPICS['tickets_incoming'], {
            "channel": "email",
            "channel_message_id": message_id,
            "customer_email": email,
            "customer_name": name,
            "subject": subject,
            "content": body,
            "received_at": datetime.utcnow().isoformat(),
            "thread_id": f"thread-{message_id}",
            "metadata": {"injected": True, "test": True},
        })
        return message_id

    async def inject_whatsapp(self, phone: str, body: str,
                               profile_name: str = "Test WA User") -> str:
        """Inject a simulated WhatsApp message into the processing pipeline."""
        message_id = str(uuid.uuid4())
        await self.producer.publish(TOPICS['tickets_incoming'], {
            "channel": "whatsapp",
            "channel_message_id": message_id,
            "customer_phone": phone,
            "content": body,
            "received_at": datetime.utcnow().isoformat(),
            "metadata": {
                "profile_name": profile_name,
                "injected": True,
                "test": True,
            },
        })
        return message_id

    async def inject_bulk(self, messages: list[dict]) -> list[str]:
        """Inject multiple messages for load/chaos testing."""
        ids = []
        for msg in messages:
            channel = msg["channel"]
            if channel == "email":
                mid = await self.inject_email(**{k: v for k, v in msg.items() if k != "channel"})
            elif channel == "whatsapp":
                mid = await self.inject_whatsapp(**{k: v for k, v in msg.items() if k != "channel"})
            ids.append(mid)
        return ids
```

#### 3.2 DB Assertion Helpers (`tests/helpers/db_assertions.py`)

```python
# tests/helpers/db_assertions.py

import asyncpg
import os
from typing import Optional

async def get_ticket_by_channel_message_id(channel_message_id: str) -> Optional[dict]:
    """Wait for a ticket to appear in DB after message injection."""
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT t.*, m.content AS last_message, m.delivery_status
            FROM tickets t
            JOIN messages m ON m.conversation_id = t.conversation_id
            WHERE m.channel_message_id = $1
            ORDER BY m.created_at DESC LIMIT 1
        """, channel_message_id)
        return dict(row) if row else None

async def wait_for_ticket_status(ticket_id: str, expected_status: str,
                                  timeout_seconds: int = 60) -> bool:
    """Poll until ticket reaches expected status or timeout."""
    import asyncio
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    while asyncio.get_event_loop().time() < deadline:
        async with pool.acquire() as conn:
            status = await conn.fetchval(
                "SELECT status FROM tickets WHERE id = $1", ticket_id
            )
            if status == expected_status:
                return True
        await asyncio.sleep(2)
    return False

async def count_messages_for_conversation(conversation_id: str) -> dict:
    """Return inbound + outbound message counts for a conversation."""
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT direction, COUNT(*) as cnt
            FROM messages WHERE conversation_id = $1
            GROUP BY direction
        """, conversation_id)
        return {r["direction"]: r["cnt"] for r in rows}

async def get_channel_p95_latency() -> dict:
    """Return P95 latency per channel from the messages table."""
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT channel,
                   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms,
                   COUNT(*) AS total_messages
            FROM messages
            WHERE direction = 'outbound' AND latency_ms IS NOT NULL
            GROUP BY channel
        """)
        return {r["channel"]: {"p95_ms": float(r["p95_ms"]), "count": r["total_messages"]}
                for r in rows}

async def get_escalation_rate() -> float:
    """Return escalation rate as a percentage."""
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'escalated') * 100.0 / NULLIF(COUNT(*), 0)
                AS escalation_rate
            FROM tickets
        """)
        return float(result["escalation_rate"] or 0)

async def get_cross_channel_accuracy() -> float:
    """Return cross-channel identification accuracy (customers with multiple identifiers)."""
    pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT customer_id) FILTER (
                    WHERE identifier_count > 1
                ) * 100.0 / NULLIF(COUNT(DISTINCT customer_id), 0) AS accuracy
            FROM (
                SELECT customer_id, COUNT(*) AS identifier_count
                FROM customer_identifiers
                GROUP BY customer_id
            ) sub
        """)
        return float(result["accuracy"] or 0)
```

#### 3.3 Locust Load Test Configuration (`tests/load_test.py`)

```python
# tests/load_test.py

from locust import HttpUser, task, between, events
import random
import json
import time

CATEGORIES = ['general', 'technical', 'billing', 'feedback', 'bug_report']
PRIORITIES = ['low', 'medium', 'high']
MESSAGES = [
    "How do I reset my API key?",
    "I'm getting a 401 unauthorized error on all my API calls.",
    "Can you explain how OAuth 2.0 works with your platform?",
    "What is the rate limit for the free plan?",
    "How do I export my data as CSV?",
    "I'm having trouble setting up webhooks. They're not firing.",
    "What happens if I exceed my quota?",
    "Can I have multiple API keys per account?",
    "How do I rotate my API key without downtime?",
    "Your webhook retry logic isn't working as documented.",
]

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Load test starting against Customer Success FTE")

class WebFormUser(HttpUser):
    """Simulates customers submitting support forms."""
    wait_time = between(2, 10)
    weight = 3

    @task(5)
    def submit_support_form(self):
        payload = {
            "name": f"Load Test User {random.randint(1, 99999)}",
            "email": f"loadtest{random.randint(1, 99999)}@example.com",
            "subject": f"Load Test - {random.choice(MESSAGES)[:40]}",
            "category": random.choice(CATEGORIES),
            "priority": random.choice(PRIORITIES),
            "message": random.choice(MESSAGES),
        }
        with self.client.post(
            "/support/submit",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "ticket_id" not in data:
                    response.failure("Response missing ticket_id")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def check_health(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")
            elif response.json().get("status") != "healthy":
                response.failure("Status not healthy")

    @task(1)
    def check_channel_metrics(self):
        self.client.get("/metrics/channels")


class PowerUser(HttpUser):
    """Simulates API-heavy users who also check ticket status."""
    wait_time = between(5, 15)
    weight = 1
    ticket_ids: list = []

    @task(3)
    def submit_and_track(self):
        payload = {
            "name": "Power User",
            "email": f"power{random.randint(1, 9999)}@example.com",
            "subject": "API integration question",
            "category": "technical",
            "priority": "high",
            "message": "I need help integrating your API with our production system. Can you walk me through the OAuth setup?",
        }
        response = self.client.post("/support/submit", json=payload)
        if response.status_code == 200:
            ticket_id = response.json().get("ticket_id")
            if ticket_id:
                self.ticket_ids.append(ticket_id)

    @task(1)
    def check_ticket_status(self):
        if self.ticket_ids:
            ticket_id = random.choice(self.ticket_ids)
            self.client.get(f"/support/ticket/{ticket_id}")
```

#### 3.4 24-Hour Simulation Script (`tests/simulate_24h.py`)

```python
# tests/simulate_24h.py
"""
24-hour continuous operation test.
Injects realistic traffic across all channels with built-in chaos testing.

Usage:
    python tests/simulate_24h.py --duration 86400 --chaos-interval 7200
    python tests/simulate_24h.py --duration 600 --chaos-interval 120  # 10-min test run
"""

import asyncio
import argparse
import random
import subprocess
import logging
from datetime import datetime
from tests.helpers.kafka_injector import KafkaMessageInjector

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

CROSS_CHANNEL_CUSTOMERS = [
    {"email": f"crosschannel{i}@example.com", "phone": f"+1555{i:07d}"}
    for i in range(1, 11)
]

WEB_FORM_MESSAGES = [
    ("How do I rotate my API key?", "technical"),
    ("Getting 429 rate limit errors", "technical"),
    ("Need help with webhook setup", "technical"),
    ("How do I export my data?", "general"),
    ("Onboarding checklist question", "general"),
    ("How do OAuth scopes work?", "technical"),
    ("Can I have multiple webhooks?", "technical"),
    ("What is the data retention policy?", "general"),
]

EMAIL_MESSAGES = [
    ("API Authentication Issue", "I am experiencing a 401 Unauthorized error when calling your REST API. I have double-checked my API key and it appears correct. Please advise on troubleshooting steps."),
    ("Webhook Not Firing", "Our production webhook endpoint has not received any events in the last 2 hours despite confirmed activity in our account. Can you help diagnose this?"),
    ("Data Export Request", "I need to export our complete interaction history in JSON format for compliance purposes. Could you guide me through the data export process?"),
]

WHATSAPP_MESSAGES = [
    ("hey how do i reset my key", "+15551234567"),
    ("getting auth error help", "+15557654321"),
    ("is there a free tier limit", "+15559876543"),
    ("webhook not working", "+15553456789"),
    ("how to export data", "+15551357924"),
]


async def run_web_form_traffic(injector: KafkaMessageInjector,
                                duration_seconds: int, interval_seconds: float):
    """Inject web form submissions at regular intervals."""
    import httpx
    end_time = asyncio.get_event_loop().time() + duration_seconds
    count = 0
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        while asyncio.get_event_loop().time() < end_time:
            msg, category = random.choice(WEB_FORM_MESSAGES)
            try:
                resp = await client.post("/support/submit", json={
                    "name": f"SimUser {count}",
                    "email": f"simuser{count}@example.com",
                    "subject": msg[:40],
                    "category": category,
                    "priority": "medium",
                    "message": msg,
                }, timeout=10.0)
                status = "OK" if resp.status_code == 200 else f"FAIL({resp.status_code})"
                logger.info(f"[WEB_FORM #{count}] {status}")
                count += 1
            except Exception as e:
                logger.error(f"[WEB_FORM] Failed: {e}")
            await asyncio.sleep(interval_seconds)
    logger.info(f"Web form simulation complete. Total submitted: {count}")


async def run_email_traffic(injector: KafkaMessageInjector,
                             duration_seconds: int, interval_seconds: float):
    """Inject email messages into Kafka at regular intervals."""
    await injector.producer.start()
    end_time = asyncio.get_event_loop().time() + duration_seconds
    count = 0
    while asyncio.get_event_loop().time() < end_time:
        subject, body = random.choice(EMAIL_MESSAGES)
        email = f"emailtest{count}@example.com"
        try:
            await injector.inject_email(email=email, subject=subject, body=body,
                                         name=f"Email User {count}")
            logger.info(f"[EMAIL #{count}] Injected: {subject[:30]}")
            count += 1
        except Exception as e:
            logger.error(f"[EMAIL] Injection failed: {e}")
        await asyncio.sleep(interval_seconds)
    logger.info(f"Email simulation complete. Total injected: {count}")


async def run_whatsapp_traffic(injector: KafkaMessageInjector,
                                duration_seconds: int, interval_seconds: float):
    """Inject WhatsApp messages into Kafka at regular intervals."""
    end_time = asyncio.get_event_loop().time() + duration_seconds
    count = 0
    while asyncio.get_event_loop().time() < end_time:
        body, phone = random.choice(WHATSAPP_MESSAGES)
        unique_phone = phone[:-4] + f"{count:04d}"
        try:
            await injector.inject_whatsapp(phone=unique_phone, body=body)
            logger.info(f"[WHATSAPP #{count}] Injected from {unique_phone}")
            count += 1
        except Exception as e:
            logger.error(f"[WHATSAPP] Injection failed: {e}")
        await asyncio.sleep(interval_seconds)
    logger.info(f"WhatsApp simulation complete. Total injected: {count}")


async def run_cross_channel_traffic(injector: KafkaMessageInjector, duration_seconds: int):
    """Simulate customers who contact via multiple channels."""
    end_time = asyncio.get_event_loop().time() + duration_seconds
    import httpx
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        while asyncio.get_event_loop().time() < end_time:
            customer = random.choice(CROSS_CHANNEL_CUSTOMERS)
            # First: web form
            await client.post("/support/submit", json={
                "name": "Cross Channel User",
                "email": customer["email"],
                "subject": "Initial contact",
                "category": "general",
                "priority": "low",
                "message": "First contact via web form about API keys",
            }, timeout=10.0)
            await asyncio.sleep(30)
            # Then: WhatsApp from same customer
            await injector.inject_whatsapp(
                phone=customer["phone"],
                body="hey following up on my api key question",
                profile_name="Cross Channel User",
            )
            logger.info(f"[CROSS_CHANNEL] {customer['email']} contacted via web + WhatsApp")
            await asyncio.sleep(300)  # 5 minutes between cross-channel events


async def run_chaos(chaos_interval_seconds: int, duration_seconds: int):
    """Kill a random worker pod every chaos_interval_seconds."""
    end_time = asyncio.get_event_loop().time() + duration_seconds
    kill_count = 0
    await asyncio.sleep(chaos_interval_seconds)  # First kill after one interval
    while asyncio.get_event_loop().time() < end_time:
        try:
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", "customer-success-fte",
                "-l", "component=message-processor",
                "-o", "jsonpath={.items[0].metadata.name}"
            ], capture_output=True, text=True)
            pod_name = result.stdout.strip()
            if pod_name:
                subprocess.run([
                    "kubectl", "delete", "pod", pod_name,
                    "-n", "customer-success-fte"
                ])
                kill_count += 1
                logger.info(f"[CHAOS #{kill_count}] Killed pod: {pod_name} at {datetime.utcnow()}")
        except Exception as e:
            logger.error(f"[CHAOS] Pod kill failed: {e}")
        await asyncio.sleep(chaos_interval_seconds)
    logger.info(f"Chaos testing complete. Total kills: {kill_count}")


async def main(duration: int, chaos_interval: int):
    injector = KafkaMessageInjector()
    await injector.producer.start()

    # Calculate per-channel intervals to hit traffic targets over duration
    web_interval = duration / 100       # 100 web form submissions
    email_interval = duration / 50      # 50 email messages
    whatsapp_interval = duration / 50   # 50 WhatsApp messages

    logger.info(f"Starting 24-hour simulation: duration={duration}s, chaos={chaos_interval}s")
    logger.info(f"Traffic intervals — web:{web_interval:.0f}s, email:{email_interval:.0f}s, wa:{whatsapp_interval:.0f}s")

    await asyncio.gather(
        run_web_form_traffic(injector, duration, web_interval),
        run_email_traffic(injector, duration, email_interval),
        run_whatsapp_traffic(injector, duration, whatsapp_interval),
        run_cross_channel_traffic(injector, duration),
        run_chaos(chaos_interval, duration),
    )

    await injector.producer.stop()
    logger.info("Simulation complete. Run validation queries to check results.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=86400)
    parser.add_argument("--chaos-interval", type=int, default=7200)
    args = parser.parse_args()
    asyncio.run(main(args.duration, args.chaos_interval))
```

### Metrics Validation SQL Queries

All Phase 3 acceptance criteria are validated via these SQL queries against the live PostgreSQL database.

```sql
-- =====================================================================
-- PHASE 3 METRICS VALIDATION QUERIES
-- Run these after the 24-hour test completes
-- Save output to specs/24h-metrics-report.md
-- =====================================================================

-- Q1: Total messages processed (should equal injected count)
SELECT
    channel,
    direction,
    COUNT(*) AS count,
    COUNT(*) FILTER (WHERE delivery_status = 'sent') AS delivered,
    COUNT(*) FILTER (WHERE delivery_status = 'failed') AS failed
FROM messages
GROUP BY channel, direction
ORDER BY channel, direction;

-- Q2: P50, P95, P99 latency per channel (target: P95 < 3000ms)
SELECT
    channel,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms)::INT AS p50_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INT AS p95_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms)::INT AS p99_ms,
    MAX(latency_ms)::INT AS max_ms,
    COUNT(*) AS total
FROM messages
WHERE direction = 'outbound' AND latency_ms IS NOT NULL
GROUP BY channel;

-- Q3: Escalation rate (target: < 25%)
SELECT
    COUNT(*) AS total_tickets,
    COUNT(*) FILTER (WHERE status = 'escalated') AS escalated,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'escalated') * 100.0 / NULLIF(COUNT(*), 0), 2
    ) AS escalation_rate_pct
FROM tickets;

-- Q4: Escalation breakdown by reason
SELECT
    resolution_notes AS escalation_reason,
    COUNT(*) AS count
FROM tickets
WHERE status = 'escalated'
GROUP BY resolution_notes
ORDER BY count DESC;

-- Q5: Cross-channel customer identification
SELECT
    COUNT(DISTINCT c.id) AS total_customers,
    COUNT(DISTINCT ci.customer_id) AS customers_with_identifiers,
    COUNT(DISTINCT ci.customer_id) FILTER (
        WHERE identifier_count > 1
    ) AS multi_channel_customers
FROM customers c
LEFT JOIN (
    SELECT customer_id, COUNT(*) AS identifier_count
    FROM customer_identifiers
    GROUP BY customer_id
) ci ON c.id = ci.customer_id;

-- Q6: Processing continuity check (detect gaps > 5 minutes — uptime proxy)
SELECT
    recorded_at::DATE AS day,
    COUNT(*) AS metric_events,
    MIN(recorded_at) AS first_event,
    MAX(recorded_at) AS last_event,
    EXTRACT(EPOCH FROM (MAX(recorded_at) - MIN(recorded_at)))/3600 AS hours_covered
FROM agent_metrics
WHERE metric_name = 'message_processed'
GROUP BY recorded_at::DATE
ORDER BY day;

-- Q7: DLQ check (must be 0)
-- Run this against Kafka:
-- kafka-consumer-groups.sh --bootstrap-server localhost:9092
--   --describe --group fte-message-processor
-- Or check via:
SELECT COUNT(*) AS dlq_events
FROM agent_metrics
WHERE metric_name = 'dlq_event';

-- Q8: Web form response time distribution
SELECT
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms)::INT AS p50_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INT AS p95_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms)::INT AS p99_ms
FROM messages
WHERE channel = 'web_form' AND direction = 'outbound';

-- Q9: Tool call patterns (verify correct tool order)
SELECT
    (tool_calls->0->>'tool_name') AS first_tool,
    (tool_calls->-1->>'tool_name') AS last_tool,
    COUNT(*) AS occurrences
FROM messages
WHERE direction = 'outbound'
  AND jsonb_array_length(tool_calls) > 0
GROUP BY first_tool, last_tool
ORDER BY occurrences DESC;

-- Q10: Sentiment distribution
SELECT
    CASE
        WHEN sentiment_score >= 0.7 THEN 'positive'
        WHEN sentiment_score >= 0.3 THEN 'neutral'
        ELSE 'negative'
    END AS sentiment_label,
    COUNT(*) AS count,
    ROUND(AVG(sentiment_score), 3) AS avg_score
FROM conversations
WHERE sentiment_score IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC;
```

---

## Constitution Check (Post-Design)

*Re-evaluate after design complete:*

- [x] All tests run against live system (no mocks except external APIs)
- [x] All metrics collected from PostgreSQL tables
- [x] Failure documentation template created
- [x] All 6 SLA hard floors enforced
- [x] Chaos testing included (pod kills every 2 hours)
- [x] All 10 documentation deliverables defined

**Constitution Status**: ✅ ALL CHECKS PASS

---

## Key Design Decisions (ADR Summary)

| Decision | Choice | Reason |
|----------|--------|--------|
| Test Framework | pytest + Locust | Industry standard, good async support |
| Load Testing | Locust (not JMeter) | Python-based, code-defined tests |
| Chaos Testing | kubectl pod delete | Simple, effective, Kubernetes-native |
| Metrics Collection | PostgreSQL queries | Direct access to source of truth |
| Evidence Format | SQL query results + HTML reports | Reproducible, auditable |
| 24-Hour Test | Custom script (not JUnit) | Flexible chaos injection, traffic control |

---

## Next Step

**Ready for `/sp.tasks`** to create detailed task breakdown for Phase 3 implementation.
