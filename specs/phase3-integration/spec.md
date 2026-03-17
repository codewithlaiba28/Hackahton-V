# Feature Specification: Phase 3 Integration Testing

**Feature Branch**: `phase3-integration`
**Created**: 2026-03-17
**Status**: Draft
**Input**: Complete specification for Phase 3 — Integration Testing, Load Testing, and 24-Hour Continuous Operation Test

---

## User Scenarios & Testing

### User Story 1 - Web Form Full Lifecycle (Priority: P1) 🎯

A customer submits the web support form. The system processes the submission through Kafka, the agent generates a response, and the customer can check their ticket status.

**Why this priority**: Web form is the primary self-service channel for customers.

**Independent Test**: Submit form → verify ticket created → verify response stored → verify status endpoint shows "responded".

**Acceptance Scenarios**:

1. **Given** valid form submission, **When** POST to `/support/submit`, **Then** returns 200 with ticket_id within 500ms
2. **Given** ticket created, **When** query PostgreSQL, **Then** `SELECT * FROM tickets WHERE id = '<ticket_id>'` shows status = 'open' or 'responded'
3. **Given** ticket processed, **When** wait 60 seconds, **Then** `GET /support/ticket/<ticket_id>` shows status = 'responded' with agent message
4. **Given** conversation complete, **When** query messages table, **Then** has 2 rows (inbound + outbound)
5. **Given** outbound message, **When** check channel, **Then** channel = 'web_form' and delivery_status = 'sent'
6. **Given** message processed, **When** query agent_metrics, **Then** has message_processed event for channel = 'web_form'

---

### User Story 2 - Email Channel Full Lifecycle (Priority: P1)

A customer sends an email to the support inbox. The system processes it through Kafka, the agent generates a formal email response with greeting and signature.

**Why this priority**: Email is the most common business communication channel.

**Independent Test**: Inject email to Kafka → verify agent processes → verify email formatting (greeting + signature) → verify DB updated.

**Acceptance Scenarios**:

1. **Given** Kafka message with channel = 'email', **When** consumed from fte.tickets.incoming, **Then** agent creates ticket with source_channel = 'email'
2. **Given** email response generated, **When** check formatting, **Then** contains email greeting ("Dear") and signature
3. **Given** email response, **When** check length, **Then** ≤ 2000 characters
4. **Given** response sent, **When** check delivery status, **Then** messages.delivery_status = 'sent' (or 'queued' in sandbox)

---

### User Story 3 - WhatsApp Channel Full Lifecycle (Priority: P1)

A customer sends a WhatsApp message. The system processes it and responds with a concise, conversational message under 300 characters.

**Why this priority**: WhatsApp is the fastest-growing customer support channel.

**Independent Test**: Inject WhatsApp to Kafka → verify agent processes → verify conversational tone → verify length ≤ 300 chars.

**Acceptance Scenarios**:

1. **Given** Kafka message with channel = 'whatsapp', **When** consumed from fte.tickets.incoming, **Then** processed without error
2. **Given** WhatsApp response, **When** check length, **Then** ≤ 300 characters
3. **Given** WhatsApp response, **When** check tone, **Then** conversational (no formal greeting)
4. **Given** WhatsApp response, **When** check content, **Then** contains support prompt (e.g., "Type 'human' for live support")
5. **Given** response sent, **When** check delivery status, **Then** messages.delivery_status = 'sent' (or 'queued' in sandbox)

---

### User Story 4 - Cross-Channel Customer Unification (Priority: P1)

A customer contacts via web form (email), then WhatsApp is linked to the same email. The system unifies them into a single customer record.

**Why this priority**: Customers expect continuity across channels.

**Independent Test**: Web form submission → WhatsApp contact with same email → verify single customer record with both identifiers.

**Acceptance Scenarios**:

1. **Given** web form submission, **When** creates customer, **Then** customers record with email = 'customer@test.com'
2. **Given** WhatsApp contact, **When** same customer, **Then** adds customer_identifiers row with identifier_type = 'whatsapp'
3. **Given** customer lookup, **When** GET /customers/lookup?email=customer@test.com, **Then** returns customer with both identifiers
4. **Given** customer history request, **When** call get_customer_history tool, **Then** returns messages from BOTH channels
5. **Given** cross-channel contacts, **When** check duplicates, **Then** no duplicate customer records

---

### User Story 5 - Pricing Escalation (Priority: P1)

A customer asks about pricing. The system escalates immediately without revealing any pricing information.

**Why this priority**: Pricing inquiries must always escalate to human sales team.

**Independent Test**: Send pricing question → verify escalation → verify no pricing in response.

**Acceptance Scenarios**:

1. **Given** message "What is the price of the Enterprise plan?", **When** processed, **Then** tickets.status = 'escalated'
2. **Given** pricing escalation, **When** check resolution_notes, **Then** contains "pricing_inquiry"
3. **Given** pricing escalation, **When** check Kafka, **Then** event published to fte.escalations with reason = 'pricing_inquiry'
4. **Given** pricing question, **When** check agent response, **Then** does NOT include any pricing information
5. **Given** pricing escalation, **When** check customer message, **Then** receives acknowledgment (not a price quote)

---

### User Story 6 - Legal Threat Escalation (Priority: P1)

A customer threatens legal action. The system escalates immediately with empathy, without engaging the legal threat.

**Why this priority**: Legal threats require immediate human legal team involvement.

**Independent Test**: Send legal threat → verify escalation → verify empathetic response → verify no engagement with threat.

**Acceptance Scenarios**:

1. **Given** message "I'll sue your company", **When** processed, **Then** tickets.status = 'escalated'
2. **Given** legal threat, **When** check escalation reason, **Then** = 'legal_threat'
3. **Given** legal threat, **When** check agent response, **Then** is empathetic
4. **Given** legal threat, **When** check engagement, **Then** does not engage with legal threat

---

### User Story 7 - Negative Sentiment Escalation (Priority: P1)

A customer sends an angry message with multiple anger signals. The system detects negative sentiment (< 0.3) and escalates.

**Why this priority**: Angry customers need immediate human attention to prevent churn.

**Independent Test**: Send angry message → verify sentiment < 0.3 → verify escalation.

**Acceptance Scenarios**:

1. **Given** message with multiple anger signals, **When** sentiment analyzed, **Then** sentiment score < 0.3
2. **Given** negative sentiment, **When** check conversation, **Then** conversations.sentiment_score updated to < 0.3
3. **Given** negative sentiment, **When** check ticket, **Then** tickets.status = 'escalated' with reason = 'negative_sentiment'

---

### User Story 8 - Human Requested Escalation (Priority: P1)

A WhatsApp customer types "I want to talk to a human". The system escalates immediately with no further AI responses.

**Why this priority**: Customers who explicitly request humans must be escalated immediately.

**Independent Test**: Send human request → verify immediate escalation → verify no further AI responses.

**Acceptance Scenarios**:

1. **Given** WhatsApp message "I want to talk to a human", **When** processed, **Then** immediate escalation
2. **Given** human request, **When** check agent responses, **Then** no further agent responses on this ticket after escalation
3. **Given** human request, **When** check ticket status, **Then** tickets.status = 'escalated' with reason = 'human_requested'

---

### User Story 9 - Tool Call Order Enforcement (Priority: P2)

For any new customer inquiry, the agent follows the correct tool call order: create_ticket first, get_customer_history before search, send_response last.

**Why this priority**: Correct tool order ensures data integrity and proper conversation tracking.

**Independent Test**: Send new inquiry → verify tool call order → verify create_ticket first, send_response last.

**Acceptance Scenarios**:

1. **Given** new customer inquiry, **When** check tool calls, **Then** first tool call MUST be create_ticket
2. **Given** new customer inquiry, **When** check tool calls, **Then** get_customer_history called BEFORE search_knowledge_base
3. **Given** any inquiry, **When** check tool calls, **Then** send_response is always the LAST tool call
4. **Given** product question, **When** check tool calls, **Then** search_knowledge_base called
5. **Given** no relevant docs, **When** check response, **Then** contains acknowledgment + escalation offer

---

### User Story 10 - Load Test: Zero Failure Rate (Priority: P2)

50 concurrent users submit web forms simultaneously. The system processes all with 0% failure rate and meets latency SLAs.

**Why this priority**: Production systems must handle concurrent load without failures.

**Independent Test**: Run Locust load test (50 users, 5 minutes) → verify 0% failures → verify latency SLAs.

**Acceptance Scenarios**:

1. **Given** 50 concurrent users, **When** 5-minute run, **Then** 0% HTTP failure rate on /support/submit
2. **Given** 50 concurrent users, **When** 5-minute run, **Then** 0% HTTP failure rate on /health
3. **Given** load test, **When** check latency, **Then** P95 latency for /support/submit < 500ms
4. **Given** load test, **When** check latency, **Then** P99 latency for /health < 100ms
5. **Given** load test, **When** check pods, **Then** no OOM kills during load test

---

### User Story 11 - Resilience: Worker Pod Kill (Priority: P2)

A worker pod is killed during message processing. The system recovers automatically, reprocesses the message, and sends no duplicates.

**Why this priority**: Production systems must survive pod failures without message loss.

**Independent Test**: Kill worker pod mid-processing → verify Kubernetes restarts within 30s → verify message reprocessed → verify no duplicates.

**Acceptance Scenarios**:

1. **Given** worker pod processing, **When** `kubectl delete pod <worker-pod>`, **Then** Kubernetes restarts pod within 30 seconds
2. **Given** in-flight message, **When** pod killed, **Then** message reprocessed after restart (Kafka offset not committed)
3. **Given** pod kill, **When** check responses, **Then** no duplicate responses sent to customer
4. **Given** pod kill, **When** check DLQ, **Then** no messages lost (DLQ empty after recovery)
5. **Given** worker pod kill, **When** check API, **Then** API pod continues serving traffic during worker restart

---

### User Story 12 - 24-Hour Continuous Operation (Priority: P1) 🎯

The system runs for 24 hours with multi-channel traffic and chaos injection (pod kills every 2 hours). All SLAs are met.

**Why this priority**: This is the final acceptance test proving production readiness.

**Independent Test**: Run 24-hour test with traffic + chaos → verify uptime > 99.9% → verify all messages processed → verify all SLAs met.

**Acceptance Scenarios**:

1. **Given** 24-hour test, **When** check uptime, **Then** system uptime > 99.9% (≤ 86 seconds total downtime)
2. **Given** 24-hour test, **When** check messages, **Then** all ≥ 200 messages processed (none in DLQ at end)
3. **Given** 24-hour test, **When** check latency, **Then** P95 latency < 3,000ms across all channels
4. **Given** 24-hour test, **When** check escalations, **Then** escalation rate < 25% of all tickets
5. **Given** 24-hour test, **When** check cross-channel, **Then** cross-channel identification accuracy > 95%
6. **Given** 24-hour test, **When** check API pods, **Then** 0 crashes not followed by automatic recovery
7. **Given** 24-hour test, **When** check worker pods, **Then** recovered within 30 seconds of each kill

---

### Edge Cases

- What happens when web form submitted with only whitespace? → 422 validation error
- How does system handle very long messages (2000+ chars)? → Accepted if valid, agent processes without timeout
- What happens with non-English messages? → Agent responds (may be in English), no crash
- How are duplicate web form submissions handled? → Creates TWO separate tickets (each independent)
- What happens with empty messages? → Agent asks for clarification, no crash
- How does system handle malformed Gmail Pub/Sub payloads? → 500 with error message, does not crash server
- What happens with WhatsApp messages containing media (images)? → Processed without crash (media ignored in Phase 2)
- How does system handle invalid Twilio signatures? → 403 Forbidden
- What happens when DB connection drops? → Connection pool recovers automatically, messages queued in Kafka processed after recovery
- How does system handle Kafka consumer rebalancing? → Messages reprocessed, no duplicates, no loss

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST process web form submissions end-to-end (form → Kafka → agent → response → DB)
- **FR-002**: System MUST process email channel messages with formal formatting (greeting + signature)
- **FR-003**: System MUST process WhatsApp channel messages with conversational tone (≤ 300 chars)
- **FR-004**: System MUST unify customers across channels into single customer record
- **FR-005**: System MUST escalate pricing inquiries immediately (reason: pricing_inquiry)
- **FR-006**: System MUST escalate legal threats immediately (reason: legal_threat)
- **FR-007**: System MUST escalate negative sentiment (< 0.3) immediately (reason: negative_sentiment)
- **FR-008**: System MUST escalate human requests immediately (reason: human_requested)
- **FR-009**: System MUST enforce tool call order (create_ticket first, send_response last)
- **FR-010**: System MUST handle 50 concurrent users with 0% failure rate
- **FR-011**: System MUST survive worker pod kills without message loss
- **FR-012**: System MUST survive API pod kills without data corruption
- **FR-013**: System MUST recover from DB connection drops automatically
- **FR-014**: System MUST run 24 hours continuously with > 99.9% uptime
- **FR-015**: System MUST validate web form inputs (reject whitespace-only, invalid emails)

### Key Entities

- **Test Scenario**: A complete end-to-end test flow with acceptance criteria
- **Load Test**: Concurrent user simulation with latency and failure rate metrics
- **Resilience Test**: Pod kill, DB restart, Kafka rebalancing tests
- **24-Hour Test**: Continuous operation test with chaos injection
- **Message**: Individual communication unit with channel, direction, content, delivery_status
- **Ticket**: Support ticket with status, escalation reason, resolution_notes
- **Customer**: Unified customer record with cross-channel identifiers
- **Metric**: Performance measurement (latency, uptime, escalation rate, etc.)

---

## Success Criteria

### Quantitative Metrics

1. **Web Form Response Time**: < 500ms (P95 latency for /support/submit)
2. **Health Check Latency**: < 100ms (P99 latency for /health)
3. **Agent Processing Latency**: < 3,000ms (P95 across all channels)
4. **System Uptime**: > 99.9% (≤ 86 seconds downtime in 24 hours)
5. **Message Processing Rate**: 100% (all messages processed, zero in DLQ)
6. **Failure Rate**: 0% (zero HTTP failures under 50-user load)
7. **Escalation Rate**: < 25% (of all tickets)
8. **Cross-Channel ID Accuracy**: > 95% (verified by DB query)
9. **Pod Recovery Time**: < 30 seconds (after pod kill)
10. **DB Recovery Time**: < 60 seconds (after DB restart)

### Qualitative Measures

1. **Customer Experience**: Responses feel personalized with cross-channel context awareness
2. **Operator Confidence**: Runbook provides clear troubleshooting steps
3. **System Resilience**: Automatic recovery from pod kills, DB restarts, Kafka rebalancing
4. **Documentation Completeness**: Fresh developer can deploy and troubleshoot in < 30 minutes
5. **Test Coverage**: All 7 user scenarios, 5 edge cases, 3 resilience tests covered

---

## Assumptions

1. Docker Compose stack starts without errors
2. Kubernetes cluster (minikube or production) is available
3. PostgreSQL with pgvector is running and accessible
4. Kafka cluster is running and accessible
5. Test data prepared (sample tickets, knowledge base entries ≥ 8)
6. Gmail sandbox credentials available (or simulated)
7. Twilio sandbox credentials available (or simulated)
8. OpenAI API key available with sufficient quota
9. Load testing tool (Locust) installed and configured
10. kubectl configured with access to customer-success-fte namespace

---

## Out of Scope (Phase 3)

- Real Gmail API integration (sandbox mode acceptable)
- Real Twilio WhatsApp API integration (sandbox mode acceptable)
- Production Kubernetes cluster (minikube acceptable for testing)
- Multi-language support (non-English messages can be processed in English)
- Advanced sentiment analysis (keyword-based acceptable)
- Custom dashboard UI (metrics queries via SQL acceptable)

---

## Dependencies

### External Dependencies

| Dependency | Purpose | Owner |
|------------|---------|-------|
| Docker Compose | Local development stack | Self-managed |
| Kubernetes | Container orchestration | Self-managed or Cloud |
| PostgreSQL + pgvector | Database + vector search | Self-managed |
| Apache Kafka | Event streaming | Self-managed |
| OpenAI API | LLM for agent responses | OpenAI |
| Locust | Load testing tool | Open source |

### Internal Dependencies

| Dependency | Purpose | Phase 2 Artifact |
|------------|---------|------------------|
| Database schema | 8 tables with indexes | backend/database/schema.sql |
| Database queries | 20+ query functions | backend/database/queries.py |
| Agent tools | 5 @function_tool functions | backend/agent/tools.py |
| Agent definition | OpenAI SDK agent | backend/agent/customer_success_agent.py |
| Channel handlers | Gmail, WhatsApp, Web Form | backend/channels/*.py |
| FastAPI app | 9 API endpoints | backend/api/main.py |
| Kafka client | Producer/consumer | backend/kafka_client.py |
| Message processor | Kafka consumer worker | backend/workers/message_processor.py |
| K8s manifests | Deployments, services, HPA | backend/k8s/*.yaml |
| React form | Web Support Form | frontend/app/components/SupportForm.tsx |

---

## Test Deliverables

| Deliverable | File | Required |
|-------------|------|----------|
| E2E test suite | backend/tests/test_multichannel_e2e.py | ✅ |
| Load test script | backend/tests/load_test.py | ✅ |
| 24h simulation script | backend/tests/simulate_24h.py | ✅ |
| Test results report | specs/phase3-test-results.md | ✅ |
| Deployment guide | docs/deployment-guide.md | ✅ |
| API documentation | docs/api-reference.md | ✅ |
| Incident runbook | docs/runbook.md | ✅ |
| Web form integration guide | docs/web-form-integration.md | ✅ |
| Final scoring checklist | specs/final-scoring-checklist.md | ✅ |
| 24-hour metrics report | specs/24h-metrics-report.md | ✅ |

---

## Testing Strategy

### Unit Tests (Already Complete in Phase 2)

- test_queries.py (5 tests)
- test_tools.py (8 tests)
- test_agent.py (8 tests)
- test_channels.py (9 tests)
- test_e2e.py (8 tests)

### Integration Tests (Phase 3)

- test_multichannel_e2e.py (7 scenarios: A1-A5, B1-B2)
- Escalation tests (5 scenarios: C1-C5)
- Agent behavior tests (5 scenarios: D1-D5)

### Load Tests (Phase 3)

- load_test.py (2 scenarios: E1-E2)
- 50 concurrent users, 5-minute run
- 100 Kafka messages, simultaneous injection

### Resilience Tests (Phase 3)

- Worker pod kill test (F1)
- API pod kill test (F2)
- DB connection recovery test (F3)

### 24-Hour Continuous Operation Test (Phase 3)

- simulate_24h.py (G1)
- Traffic pattern: 100+ web forms, 50+ emails, 50+ WhatsApp
- Chaos pattern: Pod kills every 2 hours (12 kills total)

---

**Status**: ✅ Ready for Planning (`/sp.plan`)
**Next Step**: Create Phase 3 implementation plan with test execution schedule
