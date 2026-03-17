<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 2.0.0 (Major - Production engineering principles added)
Added sections:
  - Phase 2 Identity (Production Agent)
  - 7 Production Engineering Principles
  - Technology Stack (Locked for Phase 2)
  - Phase 2 Gate Requirements
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Phase 2 alignment pending)
  - ✅ .specify/templates/spec-template.md (Phase 2 alignment pending)
  - ⚠️ .specify/templates/tasks-template.md (needs Phase 2 task categories)
Follow-up TODOs:
  - TODO(PHASE2_PLAN): Create Phase 2 implementation plan
  - TODO(PHASE2_TASKS): Create Phase 2 task breakdown
  - TODO(POSTGRES_SCHEMA): Create PostgreSQL schema with pgvector
  - TODO(KAFKA_TOPICS): Define Kafka topics and partitions
  - TODO(K8S_MANIFESTS): Create Kubernetes deployment manifests
-->

# Customer Success FTE Constitution — Phase 2

**Extends Phase 1 Constitution** — All Phase 1 rules remain in force. These rules ADD to them.

---

## Phase Identity

**Project Name**: Customer Success FTE — Production Agent

**Phase**: 2 — Specialization + Integration

**Methodology**: Agent Maturity Model — Stage 2 (Custom Agent)

**Primary Stack**: OpenAI Agents SDK · FastAPI · PostgreSQL · Kafka · Kubernetes

**Developer Role**: Builder (engineering for reliability, scale, governance)

**Duration**: Hours 17–48 of a 48–72 hour hackathon

---

## Production Engineering Principles

### VIII. No Single Point of Failure

Every component must survive pod restarts without data loss.

**Non-negotiable rules:**
- PostgreSQL is the only source of truth for all state
- Kafka is the only message bus; no direct component-to-component calls
- All state must be persisted before acknowledgment
- In-memory caches are optional optimizations, not sources of truth

**Rationale**: Production systems must be resilient to failures. Stateless workers + persistent DB + durable message bus = reliability.

---

### IX. Async-First Mandate

All I/O operations (DB, Kafka, HTTP, LLM) MUST be async/await.

**Non-negotiable rules:**
- No blocking calls permitted in any request handler
- Use `asyncpg` for PostgreSQL; `aiokafka` for Kafka; `httpx` for HTTP
- LLM calls via OpenAI Agents SDK MUST be awaited
- All file I/O must use `aiofiles` or equivalent

**Code quality mandate:**
```python
# ✅ CORRECT
async def process_message(message: dict):
    conn = await pool.acquire()
    await conn.fetch("SELECT * FROM customers WHERE id = $1", customer_id)
    await producer.send_and_wait("topic", message)

# ❌ WRONG
def process_message(message: dict):
    conn = pool.acquire()  # Blocking!
    conn.fetch(...)  # Blocking!
```

**Rationale**: Async I/O enables high concurrency with fewer resources. Blocking calls kill throughput.

---

### X. Channel Isolation Principle

Channel handlers are completely independent modules.

**Non-negotiable rules:**
- A failure in the Gmail handler must NOT affect WhatsApp or Web Form
- Each channel has its own Kafka topic for inbound messages
- Channel-specific retries and error handling
- No shared state between channel handlers except PostgreSQL

**Architecture:**
```
Gmail Handler → Kafka: fte.ingress.email
WhatsApp Handler → Kafka: fte.ingress.whatsapp
Web Form Handler → Kafka: fte.ingress.web_form
```

**Rationale**: Fault isolation prevents cascading failures. One channel down ≠ all channels down.

---

### XI. Secret Management Law

Absolutely zero secrets in code or Docker images.

**Non-negotiable rules:**
- All secrets via Kubernetes Secrets (`fte-secrets`)
- All config via Kubernetes ConfigMaps (`fte-config`)
- Local dev uses `.env` file (never committed to git)
- `.env.example` is the only file committed with placeholder values

**Secrets required:**
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DATABASE_URL`
- `KAFKA_BOOTSTRAP_SERVERS`
- `GMAIL_CREDENTIALS` (JSON)
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`

**Rationale**: Leaked secrets = compromised production. Kubernetes Secrets provide encryption at rest and fine-grained access control.

---

### XII. Observability Requirement

Every processed message MUST emit observability data.

**Non-negotiable rules:**
- Every processed message MUST emit a Kafka metrics event to `fte.metrics`
- Every escalation MUST be logged to `agent_metrics` table
- Health check endpoint (`/health`) must respond in < 100ms at all times
- Latency per message tracked and stored in `messages.latency_ms`
- All errors logged with stack traces to structured logging

**Metrics to track:**
- Messages processed per channel (counter)
- Processing latency histogram (p50, p95, p99)
- Escalation rate per reason code
- LLM token usage per message
- Kafka consumer lag per partition
- Database query latency

**Rationale**: You can't improve what you can't measure. Observability enables proactive incident response.

---

### XIII. Graceful Degradation Law

Failures must be handled gracefully without crashing.

**Non-negotiable rules:**
- If LLM call fails: send canned apology + escalate (never crash)
- If DB write fails: retry 3x with exponential backoff; then DLQ
- If channel send fails: retry 3x; then store in `messages` with `delivery_status='failed'`
- Dead Letter Queue (DLQ) Kafka topic: `fte.dlq` — all unrecoverable events land here

**Retry pattern:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def send_with_retry(message):
    await channel_handler.send(message)
```

**Rationale**: Transient failures are normal in distributed systems. Retries + DLQ = zero message loss.

---

### XIV. Web Form is a Required Deliverable

The React/Next.js Web Support Form is NOT optional.

**Non-negotiable rules:**
- Must include: client-side validation, submission, ticket ID confirmation, ticket status lookup
- Must be a standalone embeddable component (no surrounding website required)
- Must POST to FastAPI backend (`/api/support`)
- Must display success message with ticket ID upon submission

**Frontend structure:**
```
frontend/
├── app/
│   ├── components/
│   │   └── SupportForm.tsx      # Embeddable form component
│   └── api/
│       └── submit/route.ts      # API route handler
├── package.json
└── tsconfig.json
```

**Rationale**: Web form is the primary channel for customers who prefer self-service. Must be production-ready.

---

## Technology Stack (Phase 2 — Locked)

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| **Agent Framework** | OpenAI Agents SDK | Latest stable | Replaces MCP from Phase 1 |
| **API Server** | FastAPI + Uvicorn | 0.104+ | Async-first web framework |
| **Database/CRM** | PostgreSQL + pgvector | 16 + 0.5+ | Source of truth + vector search |
| **Message Broker** | Apache Kafka (or Confluent Cloud) | 3.x | Event streaming backbone |
| **Async DB Driver** | asyncpg | 0.29+ | Fastest async PostgreSQL driver |
| **Async Kafka** | aiokafka | 0.10+ | Async Kafka client |
| **Email Channel** | Gmail API (google-api-python-client) | Latest | Real Gmail integration |
| **WhatsApp Channel** | Twilio REST API | Latest | Real WhatsApp integration |
| **Web Form Frontend** | React (Next.js or standalone JSX) | 18+ | Embeddable support form |
| **Containerization** | Docker + Docker Compose | 24+ | Production containers |
| **Orchestration** | Kubernetes | 1.28+ | Auto-scaling workers |
| **Local K8s** | minikube OR kind | Latest | Local development |
| **ORM/Migrations** | Raw SQL + asyncpg | — | No ORM; raw SQL for performance |
| **Testing** | pytest + pytest-asyncio + httpx | Latest | Async test support |
| **Load Testing** | Locust | Latest | Performance validation |

**Phase 1 → Phase 2 Migrations:**
- MCP Server → OpenAI Agents SDK (`@function_tool` decorators)
- In-memory storage → PostgreSQL with pgvector
- Keyword search → Vector similarity search
- Simulated channels → Real Gmail + Twilio APIs
- Single-threaded → Async workers on Kafka
- Local execution → Kubernetes deployment

---

## Phase Gate: Must Have From Phase 1

Before any Phase 2 code is written, confirm these exist:

- [x] `specs/transition-checklist.md` — all items ✅
- [x] `specs/customer-success-fte-spec.md` — complete crystallized spec
- [x] `src/agent/prompts.py` — working system prompt extracted
- [x] `specs/discovery-log.md` — ≥10 edge cases documented
- [x] `src/skills_manifest.py` — 5 skills defined
- [x] All Phase 1 tests passing (`pytest tests/ -v`)

**Additional Phase 2 prerequisites:**
- [ ] PostgreSQL schema designed (`database/schema.sql`)
- [ ] Kafka topics defined (`fte.ingress.*`, `fte.responses`, `fte.dlq`, `fte.metrics`)
- [ ] Kubernetes manifests created (`k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/ingress.yaml`)
- [ ] Dockerfile multi-stage build ready (`Dockerfile`)
- [ ] Web form UI designed (`frontend/app/components/SupportForm.tsx`)

---

## Governance

This constitution supersedes all other practices for Phase 2.

**Amendment process:**
1. Propose amendment via `/sp.constitution` command
2. Director reviews and approves/rejects
3. If approved: increment version per semantic versioning
4. Document rationale in amendment log
5. Update dependent templates if principles change

**Versioning policy:**
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles added or existing principles expanded
- **PATCH**: Clarifications, wording improvements, typo fixes

**Compliance review:**
- All PRs and code reviews MUST verify constitution compliance
- Phase gates include constitution compliance checklist
- Violations MUST be documented and remediated before proceeding

**Version**: 2.0.0 | **Ratified**: 2026-03-17 | **Last Amended**: 2026-03-17

---

## Phase 1 → Phase 2 Handoff

**Artifacts from Phase 1:**

| Artifact | File | Use in Phase 2 |
|----------|------|----------------|
| System prompt | `src/agent/prompts.py` | Copied to `production/agent/prompts.py` |
| Tool logic | `src/agent/*.py` | Refactored into `@function_tool` decorated functions |
| DB schema hints | `specs/customer-success-fte-spec.md` | Drives PostgreSQL schema design |
| Edge cases | `specs/discovery-log.md` | Drives Phase 2 test suite (`test_transition.py`) |
| Skills manifest | `src/skills_manifest.py` | Drives OpenAI Agents SDK agent definition |
| Escalation rules | `context/escalation-rules.md` | Embedded in production system prompt |

**Next Step**: Begin Phase 2 Specialization with PostgreSQL schema design.
