# Implementation Plan: Phase 2 Specialization

**Branch**: `phase2-specialization` | **Date**: 2026-03-17 | **Spec**: specs/phase2-specialization/spec.md

**Input**: Transform Phase 1 prototype into production-grade Digital FTE using OpenAI Agents SDK, FastAPI, PostgreSQL, Kafka, and Kubernetes

---

## Summary

Build production-grade Customer Success FTE with:
- Real channel integrations (Gmail API, Twilio WhatsApp, React Web Form)
- PostgreSQL CRM with pgvector for semantic search
- Kafka event streaming for reliable message processing
- Kubernetes deployment with auto-scaling workers
- OpenAI Agents SDK replacing Phase 1 MCP server

---

## Technical Context

**Language/Version**: Python 3.11+ (async-first)
**Primary Dependencies**: OpenAI Agents SDK, FastAPI, asyncpg, aiokafka, pgvector
**Storage**: PostgreSQL 16 + pgvector 0.5+ (CRM/ticketing system)
**Testing**: pytest + pytest-asyncio + httpx + Locust (load testing)
**Target Platform**: Kubernetes 1.28+ (local: minikube/kind, cloud: GKE/EKS)
**Project Type**: Backend API + Worker services + React frontend component
**Performance Goals**: P95 latency < 3s, uptime > 99.9%, zero message loss
**Constraints**: < $1,000/year operating cost, 30s email SLA, 15s WhatsApp SLA
**Scale/Scope**: 100 concurrent requests, auto-scaling to 30 worker pods

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 2 Constitution Compliance (v2.0.0)

- [x] **No Single Point of Failure**: PostgreSQL + Kafka architecture
- [x] **Async-First Mandate**: All I/O operations async/await
- [x] **Channel Isolation**: Independent handlers per channel
- [x] **Secret Management Law**: Kubernetes Secrets only
- [x] **Observability Requirement**: Metrics for all operations
- [x] **Graceful Degradation Law**: Retries + DLQ implemented
- [x] **Web Form Required**: React/Next.js component included

### Phase 1 Constitution Compliance (v1.0.0)

- [x] **Specification-First Law**: This plan follows approved spec
- [x] **Channel-Awareness Mandate**: All responses channel-aware
- [x] **Director-Agent Contract**: Developer reviews each phase
- [x] **Documentation-Concurrent**: Docs written with code
- [x] **Fail-Safe by Default**: Error handling in all tools
- [x] **Data Integrity Rules**: Email primary, phone secondary
- [x] **Guardrail Constraints**: Pricing/refund/legal escalation

**Constitution Status**: ✅ ALL GATES PASS

---

## Project Structure

### Documentation (this feature)

```text
specs/phase2-specialization/
├── plan.md                 # This file
├── research.md             # Phase 0 output (technology decisions)
├── data-model.md           # Phase 1 output (PostgreSQL schema)
├── quickstart.md           # Phase 1 output (setup guide)
├── contracts/              # Phase 1 output (API schemas)
│   ├── openapi.yaml        # FastAPI endpoints
│   └── kafka-topics.yaml   # Kafka topic definitions
└── tasks.md                # Phase 2 output (task breakdown)
```

### Source Code (production directory)

```text
production/
├── agent/
│   ├── __init__.py
│   ├── customer_success_agent.py    # OpenAI Agents SDK agent
│   ├── tools.py                     # @function_tool decorated functions
│   ├── prompts.py                   # System prompts (from Phase 1)
│   └── formatters.py                # Channel-specific formatting
│
├── channels/
│   ├── __init__.py
│   ├── gmail_handler.py             # Gmail API + Pub/Sub
│   ├── whatsapp_handler.py          # Twilio WhatsApp API
│   └── web_form_handler.py          # FastAPI router + React form
│
├── workers/
│   ├── __init__.py
│   ├── message_processor.py         # Kafka consumer + agent runner
│   └── metrics_collector.py         # Background metrics aggregation
│
├── api/
│   ├── __init__.py
│   └── main.py                      # FastAPI application
│
├── database/
│   ├── __init__.py
│   ├── schema.sql                   # PostgreSQL schema (8 tables)
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── queries.py                   # Database access functions
│
├── web-form/
│   ├── SupportForm.jsx              # React component (required deliverable)
│   ├── package.json
│   └── README.md                    # Embedding instructions
│
├── tests/
│   ├── test_agent.py                # Agent unit tests
│   ├── test_channels.py             # Channel handler tests
│   ├── test_e2e.py                  # End-to-end integration tests
│   ├── test_multichannel_e2e.py     # Multi-channel specific tests
│   └── load_test.py                 # Locust load test scripts
│
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml                 # Template only (no real values)
│   ├── deployment-api.yaml
│   ├── deployment-worker.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
│
├── Dockerfile
├── docker-compose.yml               # Local development stack
├── docker-compose.dev.yml           # Dev overrides
├── pyproject.toml
├── requirements.txt
└── .env.example                     # Template with all required env vars
```

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **OpenAI Agents SDK Migration**
   - Research MCP → OpenAI SDK tool migration patterns
   - Document @function_tool decorator usage with Pydantic models
   - Identify breaking changes from Phase 1 MCP implementation

2. **PostgreSQL + pgvector Setup**
   - Research pgvector extension installation and configuration
   - Document IVFFlat index configuration for semantic search
   - Identify optimal `lists` parameter for knowledge base size

3. **Async Database Patterns**
   - Research asyncpg connection pool best practices
   - Document transaction management for idempotent processing
   - Identify timeout and retry strategies

4. **Kafka Consumer Group Patterns**
   - Research consumer group rebalancing strategies
   - Document offset commit strategies (after DB write)
   - Identify DLQ patterns for unrecoverable failures

5. **Gmail API Integration**
   - Research Gmail Pub/Sub push notification setup
   - Document thread-preserving reply patterns
   - Identify rate limits and quota management

6. **Twilio WhatsApp Integration**
   - Research Twilio webhook signature validation
   - Document async response patterns (TwiML immediate + callback later)
   - Identify delivery status callback handling

7. **Kubernetes HPA Configuration**
   - Research HPA metrics (CPU vs custom metrics)
   - Document min/max replica configuration
   - Identify scale-down stabilization windows

### Research Output: research.md

All research findings consolidated in `research.md` with:
- Decision: What was chosen
- Rationale: Why chosen
- Alternatives considered: What else evaluated

---

## Phase 1: Design & Contracts

### Data Model Design (data-model.md)

**8 PostgreSQL Tables**:

1. **customers**
   - Fields: id (UUID), email (UNIQUE), phone, name, created_at, metadata (JSONB)
   - Validation: email format, phone E.164 format
   - Relationships: 1:N customer_identifiers, 1:N conversations

2. **customer_identifiers**
   - Fields: id (UUID), customer_id (FK), identifier_type, identifier_value (UNIQUE), verified, created_at
   - Validation: type IN ('email', 'phone', 'whatsapp')
   - Relationships: N:1 customers

3. **conversations**
   - Fields: id (UUID), customer_id (FK), initial_channel, started_at, ended_at, status, sentiment_score, resolution_type, escalated_to, metadata (JSONB)
   - Validation: channel IN ('email', 'whatsapp', 'web_form'), status IN ('active', 'closed', 'escalated')
   - Relationships: N:1 customers, 1:N messages, 1:N tickets

4. **messages**
   - Fields: id (UUID), conversation_id (FK), channel, direction, role, content, created_at, tokens_used, latency_ms, tool_calls (JSONB), channel_message_id, delivery_status, sentiment_score, metadata (JSONB)
   - Validation: direction IN ('inbound', 'outbound'), role IN ('customer', 'agent', 'system'), delivery_status IN ('pending', 'sent', 'delivered', 'failed')
   - Relationships: N:1 conversations

5. **tickets**
   - Fields: id (UUID), conversation_id (FK), customer_id (FK), source_channel, category, priority, status, created_at, resolved_at, resolution_notes, assigned_to, sla_deadline, metadata (JSONB)
   - Validation: priority IN ('low', 'medium', 'high', 'critical'), status IN ('open', 'in_progress', 'waiting', 'resolved', 'closed', 'escalated')
   - Relationships: N:1 conversations, N:1 customers

6. **knowledge_base**
   - Fields: id (UUID), title, content, category, embedding (VECTOR(1536)), tags (TEXT[]), created_at, updated_at, is_active, view_count, helpful_count
   - Validation: embedding dimension = 1536
   - Indexes: IVFFlat on embedding (lists=100)

7. **channel_configs**
   - Fields: id (UUID), channel (UNIQUE), enabled, config (JSONB), response_template, max_response_length, created_at, updated_at
   - Validation: channel IN ('email', 'whatsapp', 'web_form')

8. **agent_metrics**
   - Fields: id (UUID), metric_name, metric_value (DECIMAL), channel, dimensions (JSONB), recorded_at
   - Indexes: ON (metric_name, recorded_at)

**Critical Constraints**:
- `customers.email` — UNIQUE, primary cross-channel identifier
- `customer_identifiers` — UNIQUE on (identifier_type, identifier_value)
- `messages.channel` — tracks which channel message arrived on
- `messages.channel_message_id` — external ID (Gmail Message-ID, Twilio SID)
- `tickets.source_channel` — originated channel

**pgvector Setup**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- IVFFlat index for approximate nearest-neighbor search
CREATE INDEX idx_knowledge_embedding
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### API Contracts (contracts/openapi.yaml)

**FastAPI Endpoints**:

1. **POST /webhooks/gmail**
   - Purpose: Gmail Pub/Sub webhook
   - Input: Pub/Sub message with Gmail history ID
   - Output: `{"status": "success", "processed": N}`
   - Auth: Google service account token validation

2. **POST /webhooks/whatsapp**
   - Purpose: Twilio WhatsApp webhook
   - Input: Twilio webhook form data
   - Output: TwiML response (empty message)
   - Auth: X-Twilio-Signature header validation

3. **POST /webhooks/whatsapp/status**
   - Purpose: Twilio delivery status callback
   - Input: Twilio status webhook
   - Output: 200 OK
   - Auth: X-Twilio-Signature header validation

4. **POST /support/submit**
   - Purpose: Web form submission
   - Input: `{name, email, subject, category, priority, message}`
   - Output: `{ticket_id: str}` within 500ms
   - Auth: CORS only

5. **GET /support/ticket/{ticket_id}**
   - Purpose: Ticket status lookup
   - Input: ticket_id (path parameter)
   - Output: `{ticket_id, status, created_at, messages[]}`
   - Auth: None (public for customer convenience)

6. **GET /conversations/{conversation_id}**
   - Purpose: Conversation history
   - Input: conversation_id (path parameter)
   - Output: `{conversation, messages[], customer}`
   - Auth: API key or session token

7. **GET /customers/lookup**
   - Purpose: Customer lookup by email or phone
   - Input: `?email=...` or `?phone=...`
   - Output: `{customer, identifiers[], recent_conversations[]}`
   - Auth: API key required

8. **GET /metrics/channels**
   - Purpose: Channel performance metrics (last 24h)
   - Input: Optional `?channel=email|whatsapp|web_form`
   - Output: `[{channel, total_conversations, avg_sentiment, escalations, p95_latency}]`
   - Auth: API key required (ops-only endpoint)

9. **GET /health**
   - Purpose: Health check for Kubernetes
   - Input: None
   - Output: `{status: "healthy", timestamp, version}`
   - Response time: < 100ms

### Kafka Topic Contracts (contracts/kafka-topics.yaml)

**Inbound Topics** (per-channel):
- `fte.channels.email.inbound` — Gmail webhook publishes here
- `fte.channels.whatsapp.inbound` — Twilio webhook publishes here
- `fte.channels.webform.inbound` — Web form endpoint publishes here

**Unified Topic**:
- `fte.tickets.incoming` — ALL channels merge here (main worker consumes)

**Outbound Topics**:
- `fte.channels.email.outbound` — Agent publishes outbound emails
- `fte.channels.whatsapp.outbound` — Agent publishes outbound WhatsApp
- `fte.escalations` — Escalation events for human agents
- `fte.metrics` — Performance and operational metrics
- `fte.dlq` — Dead letter queue (failed processing)

**Consumer Groups**:
- `fte-api-gmail` — consumes `fte.channels.email.inbound`
- `fte-api-whatsapp` — consumes `fte.channels.whatsapp.inbound`
- `fte-message-processor` — consumes `fte.tickets.incoming` (main worker group)
- `fte-metrics-collector` — consumes `fte.metrics`

### Quick Start Guide (quickstart.md)

**Local Development Setup**:

1. **Clone and setup**:
   ```bash
   cd production
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Start infrastructure (Docker Compose)**:
   ```bash
   docker-compose up -d postgres kafka zookeeper
   ```

3. **Initialize database**:
   ```bash
   psql postgresql://fte_user:password@localhost:5432/fte_db -f database/schema.sql
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run API server**:
   ```bash
   uvicorn api.main:app --reload
   ```

6. **Run workers**:
   ```bash
   python workers/message_processor.py
   ```

7. **Verify setup**:
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "healthy", ...}
   ```

---

## Phase 2: Implementation Ordering

### Phase 2A — DB Foundation (Hours 17-20)
**Components**: schema.sql, migrations/, queries.py, connection pool
**Gate**: All 8 tables created; queries tested with asyncpg
**Deliverables**:
- ✅ PostgreSQL schema with pgvector enabled
- ✅ Connection pool configured (min=2, max=20)
- ✅ All query functions implemented in queries.py
- ✅ Unit tests for all queries

### Phase 2B — Tool Migration (Hours 20-25)
**Components**: agent/tools.py with 5 @function_tool functions
**Gate**: Tool unit tests pass
**Deliverables**:
- ✅ `search_knowledge_base` with pgvector semantic search
- ✅ `create_ticket` with asyncpg INSERT
- ✅ `get_customer_history` with cross-channel JOIN
- ✅ `escalate_to_human` with Kafka publish + DB UPDATE
- ✅ `send_response` with real Gmail/Twilio API calls

### Phase 2C — Agent Definition (Hours 25-27)
**Components**: agent/customer_success_agent.py
**Gate**: Transition tests pass (Phase 1 edge cases)
**Deliverables**:
- ✅ OpenAI Agents SDK agent configured
- ✅ System prompt migrated from Phase 1
- ✅ All 5 tools attached to agent
- ✅ Agent processes test messages correctly

### Phase 2D — Channel Handlers (Hours 27-32)
**Components**: channels/gmail_handler.py, whatsapp_handler.py, web_form_handler.py
**Gate**: Webhook handlers return correct Kafka messages
**Deliverables**:
- ✅ Gmail handler validates Pub/Sub token, publishes to Kafka
- ✅ WhatsApp handler validates Twilio signature, publishes to Kafka
- ✅ Web form handler validates input, publishes to Kafka, returns ticket_id

### Phase 2E — Kafka Integration (Hours 32-35)
**Components**: workers/message_processor.py, Kafka consumer groups
**Gate**: Messages flow end-to-end through Kafka
**Deliverables**:
- ✅ Kafka producer configured in channel handlers
- ✅ Kafka consumer configured in message_processor.py
- ✅ Offset committed AFTER successful DB write
- ✅ DLQ handling for unrecoverable failures

### Phase 2F — FastAPI Service (Hours 35-37)
**Components**: api/main.py, all endpoints
**Gate**: All API tests pass
**Deliverables**:
- ✅ All 9 endpoints implemented
- ✅ CORS configured for known origins
- ✅ Health check responds in < 100ms
- ✅ Metrics endpoint returns last 24h data

### Phase 2G — Web Form UI (Hours 37-39)
**Components**: web-form/SupportForm.jsx
**Gate**: Form submits, ticket ID returned within 500ms
**Deliverables**:
- ✅ React form with all required fields
- ✅ Client-side validation
- ✅ POST to /support/submit
- ✅ Success screen with ticket ID

### Phase 2H — Kubernetes (Hours 39-42)
**Components**: k8s/*.yaml manifests
**Gate**: Pods running, HPA tested
**Deliverables**:
- ✅ Namespace, ConfigMap, Secrets templates
- ✅ API deployment (3 replicas, HPA 3-20)
- ✅ Worker deployment (3 replicas, HPA 3-30)
- ✅ Service, Ingress with TLS
- ✅ HPA configured (CPU > 70%)

### Phase 2I — Integration Tests (Hours 42-46)
**Components**: tests/test_e2e.py, test_multichannel_e2e.py, load_test.py
**Gate**: All tests pass; load test SLA met
**Deliverables**:
- ✅ End-to-end tests for all 7 user scenarios
- ✅ Multi-channel continuity tests
- ✅ Load test (100 concurrent requests)
- ✅ Chaos tests (pod failure, Kafka broker down)

### Phase 2J — 24-Hour Test (Hours 46-48+)
**Components**: Continuous operation validation
**Gate**: Metrics targets met
**Deliverables**:
- ✅ 24-hour continuous operation
- ✅ Uptime > 99.9%
- ✅ P95 latency < 3 seconds
- ✅ Zero messages in DLQ
- ✅ All performance budgets met

---

## Constitution Check (Post-Design)

*Re-evaluate after design complete:*

- [x] All components are channel-aware
- [x] Fail-safe defaults in all error handlers
- [x] Email as primary identifier enforced
- [x] Guardrails documented in escalation logic
- [x] Documentation concurrent with implementation
- [x] Director-Agent contract maintained
- [x] Async-first in all I/O operations
- [x] No secrets in code (Kubernetes Secrets only)
- [x] Observability via fte.metrics topic
- [x] DLQ for graceful degradation

**Constitution Status**: ✅ ALL CHECKS PASS

---

## Key Design Decisions (ADR Summary)

| Decision | Choice | Reason |
|----------|--------|--------|
| Agent Framework | OpenAI Agents SDK | Production-grade, @function_tool decorators, Pydantic validation |
| Database | PostgreSQL 16 + pgvector | Source of truth + vector search in one system |
| Message Broker | Apache Kafka 3.x | Durable, scalable, consumer group rebalancing |
| API Framework | FastAPI | Async-first, OpenAPI auto-generation, Pydantic validation |
| Frontend | React (Next.js) | Required deliverable, embeddable component |
| Orchestration | Kubernetes 1.28+ | Auto-scaling, HPA, Secrets management |
| DB Driver | asyncpg | Fastest async PostgreSQL driver |
| Kafka Client | aiokafka | Async Kafka client for Python |
| ORM Strategy | Raw SQL + asyncpg | No ORM overhead; full control over queries |
| Index Strategy | IVFFlat (lists=100) | Good balance of speed/accuracy for KB size |

---

## Next Step

**Ready for `/sp.tasks`** to create detailed task breakdown for Phase 2 implementation.
