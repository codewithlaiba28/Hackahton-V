# Feature Specification: Phase 2 Specialization

**Feature Branch**: `phase2-specialization`
**Created**: 2026-03-17
**Status**: Draft
**Input**: Transform Phase 1 prototype into production-grade Digital FTE

---

## User Scenarios & Testing

### User Story 1 - Real Email via Gmail Pub/Sub (Priority: P1) 🎯

A customer sends a real email to the company's Gmail inbox. Gmail pushes a notification to Cloud Pub/Sub, which calls the `/webhooks/gmail` endpoint. The FTE processes the email, creates a ticket in PostgreSQL, and replies via Gmail API.

**Why this priority**: Email is the most common business communication channel; must work reliably with thread preservation.

**Independent Test**: Send real email → verify webhook receives, processes, and replies with correct thread ID.

**Acceptance Scenarios**:

1. **Given** Gmail Pub/Sub webhook receives notification, **When** validated, **Then** email content extracted (From, Subject, Body, Thread ID)
2. **Given** valid email, **When** processed, **Then** message published to `fte.channels.email.inbound` Kafka topic
3. **Given** Kafka event, **When** agent worker consumes, **Then** processes via OpenAI Agents SDK
4. **Given** agent response, **When** sent via Gmail API, **Then** reply includes correct thread ID (preserves email thread)
5. **Given** completed interaction, **When** stored in PostgreSQL, **Then** full conversation in messages, conversations, tickets tables
6. **Given** webhook receipt, **When** reply sent, **Then** end-to-end latency < 30 seconds

---

### User Story 2 - Real WhatsApp via Twilio Sandbox (Priority: P1)

A customer sends a WhatsApp message to the Twilio Sandbox number. Twilio sends a webhook POST to `/webhooks/whatsapp`. The FTE validates the Twilio signature, processes the message, and replies via Twilio API.

**Why this priority**: WhatsApp is the fastest-growing customer support channel; requires signature validation and async response.

**Independent Test**: Send WhatsApp message → verify signature validation, Kafka publishing, concise reply.

**Acceptance Scenarios**:

1. **Given** Twilio webhook POST, **When** received, **Then** X-Twilio-Signature header validated
2. **Given** valid webhook, **When** processed, **Then** message published to `fte.channels.whatsapp.inbound` Kafka topic
3. **Given** agent response, **When** sent via Twilio API, **Then** response concise (≤300 chars)
4. **Given** WhatsApp message, **When** customer identified, **Then** by phone number with cross-channel history retrieved
5. **Given** Twilio webhook, **When** processed, **Then** TwiML empty response returned immediately (agent replies asynchronously)
6. **Given** delivery status callback, **When** received from Twilio, **Then** status updated in database

---

### User Story 3 - Web Support Form Submission (Priority: P1)

A customer fills out the web support form and submits. The React form POSTs to `/support/submit`. A ticket ID is shown immediately; the FTE processes the request and emails a response.

**Why this priority**: Required deliverable per hackathon; self-service channel for customers who prefer web forms.

**Independent Test**: Submit web form → verify ticket ID shown within 500ms, status lookup works.

**Acceptance Scenarios**:

1. **Given** React form, **When** rendered, **Then** includes: name, email, subject, category, priority, message fields
2. **Given** form submission, **When** client-side validation runs, **Then** prevents invalid submissions
3. **Given** valid POST to `/support/submit`, **When** processed, **Then** returns ticket_id within 500ms
4. **Given** form submission, **When** processed, **Then** message published to `fte.channels.webform.inbound` Kafka topic
5. **Given** agent processing, **When** complete, **Then** sends response via email (confirmation)
6. **Given** ticket ID, **When** queried at `/support/ticket/{ticket_id}`, **Then** returns current status
7. **Given** successful submission, **When** complete, **Then** form shows success screen with ticket ID

---

### User Story 4 - Cross-Channel Customer Identification (Priority: P1)

A customer who previously emailed now sends a WhatsApp message. The FTE identifies them by phone-to-email lookup and retrieves their full history.

**Why this priority**: Customers expect continuity across channels; critical for personalized support.

**Independent Test**: Send WhatsApp from known customer → verify full email history retrieved and acknowledged.

**Acceptance Scenarios**:

1. **Given** WhatsApp message, **When** phone number received, **Then** matched to email via `customer_identifiers` table
2. **Given** identified customer, **When** history retrieved, **Then** full conversation history from all channels
3. **Given** agent response, **When** generated, **Then** acknowledges prior context ("Following up on your email...")
4. **Given** cross-channel identification, **When** complete, **Then** no duplicate customer records created
5. **Given** 100 cross-channel customers, **When** measured, **Then** identification accuracy ≥ 95%

---

### User Story 5 - Concurrent Load Handling (Priority: P2)

100 support requests arrive simultaneously across all three channels. The system processes all within SLA without dropping any messages.

**Why this priority**: Production systems must handle traffic spikes without message loss.

**Independent Test**: Load test with 100 concurrent requests → verify zero message loss, all within SLA.

**Acceptance Scenarios**:

1. **Given** 100 concurrent messages, **When** sent to Kafka, **Then** all land in Kafka without loss
2. **Given** load spike, **When** detected, **Then** Kubernetes auto-scales worker pods
3. **Given** 100 messages processed, **When** measured, **Then** P95 latency (agent processing) < 3 seconds
4. **Given** processing complete, **When** checked, **Then** zero messages in DLQ (`fte.dlq`)
5. **Given** 100 responses, **When** sent, **Then** all delivered to correct customer + channel

---

### User Story 6 - Pod Failure Recovery (Priority: P2)

A worker pod crashes mid-processing. Kafka consumer group rebalances; the in-flight message is reprocessed.

**Why this priority**: Production systems must survive pod failures without message loss or duplicates.

**Independent Test**: Kill worker pod mid-processing → verify message reprocessed correctly, no duplicates.

**Acceptance Scenarios**:

1. **Given** Kafka consumer, **When** processing message, **Then** offset committed only AFTER successful DB write
2. **Given** pod crash mid-processing, **When** rebalanced, **Then** message reprocessed (idempotent processing)
3. **Given** reprocessing, **When** complete, **Then** no duplicate responses sent to customer
4. **Given** crashed pod, **When** restarted, **Then** via Kubernetes `restartPolicy: Always`

---

### User Story 7 - Daily Channel Metrics (Priority: P2)

An operator queries `/metrics/channels` to see yesterday's performance.

**Why this priority**: Operations team needs visibility into channel performance for capacity planning.

**Independent Test**: Query `/metrics/channels` → verify per-channel metrics returned within 500ms.

**Acceptance Scenarios**:

1. **Given** GET `/metrics/channels`, **When** queried, **Then** returns metrics per channel
2. **Given** channel metrics, **When** returned, **Then** includes: total_conversations, avg_sentiment, escalations
3. **Given** metrics query, **When** executed, **Then** data sourced from `agent_metrics` + `conversations` tables
4. **Given** metrics endpoint, **When** queried, **Then** response time < 500ms
5. **Given** metrics request, **When** processed, **Then** data is for last 24 hours by default

---

### Edge Cases

- What happens when Gmail Pub/Sub notification arrives with invalid token?
- How does system handle Twilio webhook with mismatched signature?
- What happens when Kafka broker is temporarily unavailable?
- How does system handle PostgreSQL connection pool exhaustion?
- What happens when LLM API returns rate limit error?
- How are duplicate emails (same Message-ID) handled?
- What happens when customer phone number not found in `customer_identifiers`?
- How does system handle very long email threads (100+ messages)?
- What happens when React form submitted with JavaScript disabled?
- How are special characters in customer names handled across channels?

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept real emails via Gmail Pub/Sub webhook
- **FR-002**: System MUST validate Twilio webhook signatures (HMAC-SHA1)
- **FR-003**: System MUST provide React Web Support Form with client-side validation
- **FR-004**: System MUST identify customers across channels via `customer_identifiers` table
- **FR-005**: System MUST publish all inbound messages to Kafka topics
- **FR-006**: System MUST persist all state in PostgreSQL (8 tables: customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics)
- **FR-007**: System MUST process messages via OpenAI Agents SDK (replacing Phase 1 MCP)
- **FR-008**: System MUST auto-scale worker pods based on CPU utilization (>70%)
- **FR-009**: System MUST provide `/metrics/channels` endpoint with per-channel metrics
- **FR-010**: System MUST implement Dead Letter Queue (`fte.dlq`) for unrecoverable failures
- **FR-011**: System MUST support idempotent message processing (safe retries)
- **FR-012**: System MUST preserve email thread IDs in Gmail API replies
- **FR-013**: System MUST return TwiML empty response immediately for WhatsApp webhooks
- **FR-014**: System MUST show ticket ID within 500ms for web form submissions
- **FR-015**: System MUST retrieve full cross-channel conversation history for identified customers

### Key Entities

- **Customer**: Person submitting support requests; identified by email (primary) or phone (WhatsApp); stored in `customers` table
- **Customer Identifier**: Cross-channel mapping (email ↔ phone); stored in `customer_identifiers` table
- **Conversation**: Thread of messages between customer and FTE; may span multiple channels; stored in `conversations` table
- **Message**: Individual communication unit; has direction (inbound/outbound), channel, delivery status; stored in `messages` table
- **Ticket**: Support ticket with status, priority, category; stored in `tickets` table
- **Knowledge Base**: Product documentation with vector embeddings for semantic search; stored in `knowledge_base` table with pgvector
- **Channel Config**: Per-channel configuration (API keys, webhook URLs); stored in `channel_configs` table
- **Agent Metric**: Performance metrics (latency, sentiment, escalations); stored in `agent_metrics` table

---

## Success Criteria

### Quantitative Metrics

1. **Uptime**: > 99.9% (measured by Kubernetes pod restart count)
2. **P95 Processing Latency**: < 3 seconds (measured by `messages.latency_ms`)
3. **End-to-End Latency (Email)**: < 30 seconds (webhook receipt to Gmail send)
4. **End-to-End Latency (WhatsApp)**: < 15 seconds (webhook receipt to Twilio send)
5. **Message Loss**: 0% (DLQ message count = 0)
6. **Cross-Channel ID Accuracy**: > 95% (customer_identifiers match rate)
7. **Escalation Rate**: < 25% (tickets.status = 'escalated' rate)
8. **Web Form Response Time**: < 500ms (FastAPI endpoint latency)
9. **Knowledge Base Accuracy**: > 85% (manual review of 20 test queries)
10. **Concurrent Load**: 100 messages processed without loss

### Qualitative Measures

1. **Customer Experience**: Responses feel personalized with cross-channel context awareness
2. **Operator Visibility**: Metrics dashboard provides clear channel performance insights
3. **Error Handling**: Graceful degradation with clear customer-facing messages
4. **Thread Preservation**: Email replies maintain proper thread hierarchy
5. **Form Usability**: Web form is intuitive with clear validation feedback

---

## Assumptions

1. Gmail account has Pub/Sub enabled and service account configured
2. Twilio Sandbox number is provisioned and webhook URL configured
3. Kubernetes cluster (1.28+) is available (local: minikube/kind, or cloud: GKE/EKS)
4. PostgreSQL 16 with pgvector 0.5+ extension is available
5. Kafka 3.x cluster is available (local: Docker Compose, or cloud: Confluent Cloud)
6. OpenAI API key is available and has sufficient quota
7. Domain name is configured for Ingress TLS termination
8. React/Next.js frontend can be served via same Ingress or separately

---

## Out of Scope (Phase 2)

- Mobile app integrations (iOS/Android apps)
- Social media channels (Twitter, Facebook Messenger)
- Voice call support (IVR integration)
- Multi-language support (non-English languages)
- Advanced analytics dashboard (beyond `/metrics/channels`)
- Customer satisfaction surveys (CSAT, NPS)
- Automated quality assurance (QA) scoring
- Workforce management (WFM) integration
- Chatbot training interface (manual KB updates only)

---

## Dependencies

### External Dependencies

| Dependency | Purpose | Owner |
|------------|---------|-------|
| Gmail API + Pub/Sub | Email channel intake | Google Cloud |
| Twilio WhatsApp API | WhatsApp channel intake | Twilio |
| OpenAI API | LLM for agent responses | OpenAI |
| PostgreSQL + pgvector | Database + vector search | Self-managed or Cloud SQL |
| Apache Kafka | Event streaming | Self-managed or Confluent Cloud |
| Kubernetes | Container orchestration | Self-managed or GKE/EKS |

### Internal Dependencies

| Dependency | Purpose | Phase 1 Artifact |
|------------|---------|------------------|
| System prompt | Agent behavior | `src/agent/prompts.py` |
| Skills manifest | Agent capabilities | `src/skills_manifest.py` |
| Discovery log | Edge cases | `specs/discovery-log.md` |
| Crystallized spec | Functional requirements | `specs/customer-success-fte-spec.md` |
| Transition checklist | Phase 1→2 handoff | `specs/transition-checklist.md` |

---

## Security & Compliance

### Security Requirements

1. **Twilio Webhooks**: Validated via `RequestValidator` (HMAC-SHA1 signature)
2. **Gmail Pub/Sub**: Validated via Google service account token verification
3. **Secrets Management**: All secrets in Kubernetes Secrets (`fte-secrets`); never in env files on cluster
4. **CORS**: Configured for known origins only (production)
5. **PII Protection**: No customer PII logged in plaintext; emails truncated in logs
6. **Database Security**: Connections via connection pool (max 20 per pod); SSL required
7. **Network Policies**: Pod-to-pod communication restricted via Kubernetes NetworkPolicies
8. **Ingress TLS**: All external traffic encrypted via NGINX Ingress with TLS

### Compliance Considerations

1. **GDPR**: Customer data export and deletion capabilities (Phase 3)
2. **Data Retention**: Conversation history retained for 90 days (configurable)
3. **Audit Logging**: All escalations logged with reason codes
4. **Access Control**: Role-based access to `/metrics/channels` and admin endpoints

---

## Performance Budgets

| Metric | Budget | Measurement |
|--------|--------|-------------|
| Webhook to Kafka | < 100ms | `fte.channels.*.inbound` latency |
| Kafka to Agent Start | < 500ms | Consumer lag + processing start |
| Agent Processing | < 2 seconds (p95) | `messages.latency_ms` |
| DB Write | < 50ms | `agent_metrics` insert latency |
| Channel Send | < 1 second | Gmail API / Twilio API latency |
| End-to-End (Email) | < 30 seconds | Webhook receipt to Gmail send |
| End-to-End (WhatsApp) | < 15 seconds | Webhook receipt to Twilio send |
| Web Form Response | < 500ms | `/support/submit` latency |
| Metrics Endpoint | < 500ms | `/metrics/channels` latency |
| Health Check | < 100ms | `/health` latency |

---

## Testing Strategy

### Unit Tests

- Channel handlers (Gmail, WhatsApp, Web Form)
- Kafka producers and consumers
- PostgreSQL queries (asyncpg)
- OpenAI Agents SDK tool definitions
- React form validation

### Integration Tests

- End-to-end message flow (webhook → Kafka → agent → response)
- Cross-channel customer identification
- Kafka consumer group rebalancing
- PostgreSQL transaction isolation
- Gmail API thread preservation
- Twilio signature validation

### Load Tests

- 100 concurrent messages across all channels
- Kafka broker failure recovery
- PostgreSQL connection pool exhaustion
- Kubernetes HPA auto-scaling trigger
- LLM API rate limit handling

### Chaos Tests

- Worker pod termination mid-processing
- Kafka broker unavailability
- PostgreSQL connection failures
- Gmail API quota exceeded
- Twilio webhook timeout

---

## Phase 2 → Phase 3 Handoff

**Artifacts for Phase 3**:

| Artifact | File | Use in Phase 3 |
|----------|------|----------------|
| PostgreSQL schema | `database/schema.sql` | Production database setup |
| Kafka topics | `kafka/topics.yaml` | Topic configuration |
| Kubernetes manifests | `k8s/` | Production deployment |
| Dockerfile | `Dockerfile` | Container image build |
| React form | `frontend/app/components/SupportForm.tsx` | Production web form |
| Load test results | `tests/load/results.md` | Performance baseline |
| Runbooks | `docs/runbooks/` | Operational procedures |

---

**Status**: ✅ Ready for Planning (`/sp.plan`)
**Next Step**: Create technical implementation plan with architecture, component design, and task breakdown
