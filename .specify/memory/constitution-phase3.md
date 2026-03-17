<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 3.0.0 (Major - Phase 3 validation principles added)
Added sections:
  - Phase 3 Identity (Validation & Production Readiness)
  - 6 Immutable Principles for Phase 3
  - Phase Gate Requirements (from Phase 2)
  - SLA Hard Floors (6 metrics)
  - Chaos Testing Requirements
  - Documentation Completeness Requirements
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Phase 3 alignment)
  - ✅ .specify/templates/spec-template.md (validation criteria)
  - ✅ .specify/templates/tasks-template.md (test task categories)
Follow-up TODOs:
  - TODO(PHASE3_PLAN): Create Phase 3 integration test plan
  - TODO(PHASE3_TESTS): Create Phase 3 test execution scripts
  - TODO(PHASE3_RUNBOOK): Create operational runbook
  - TODO(24H_TEST): Create 24-hour continuous operation test script
-->

# Customer Success FTE Constitution — Phase 3

**Extends Phase 1 & Phase 2 Constitutions** — All previous rules remain fully in force. These rules ADD to them.

---

## Phase Identity

**Project Name**: Customer Success FTE — Validation & Production Readiness

**Phase**: 3 — Integration Testing, Load Testing, 24-Hour Continuous Operation

**Methodology**: Agent Maturity Model — Proof of Production Readiness

**Developer Role**: Quality Engineer + Operations Engineer

**Duration**: Hours 41–48 (minimum); 24-hour test runs beyond Hour 48

---

## Phase 3 Immutable Principles

### XV. Test Reality, Not Mocks

All Phase 3 tests run against the live deployed system (Docker Compose or Kubernetes).

**Non-negotiable rules:**
- Mocks are permitted only for external credentials (Gmail sandbox, Twilio sandbox)
- Tests that pass only in isolation and fail against the real stack are failures, not passes
- All tests must use real PostgreSQL, real Kafka, real agent processing
- Integration tests must process real messages end-to-end

**Rationale**: Mocks hide integration bugs. Production systems fail at integration points, not in isolated units. Real testing reveals real problems.

---

### XVI. Evidence-First Validation

Every acceptance criterion must be proven with a reproducible command or query.

**Non-negotiable rules:**
- "It worked when I tested it" is not evidence
- Logs, DB queries, and test output are evidence
- All metric measurements must be captured from PostgreSQL `agent_metrics` and `messages` tables
- No estimates — only actual measurements
- All test results documented in `specs/phase3-test-results.md`

**Evidence Requirements:**
```sql
-- Uptime evidence
SELECT MIN(recorded_at), MAX(recorded_at), COUNT(*) 
FROM agent_metrics 
WHERE recorded_at > NOW() - INTERVAL '24 hours';

-- P95 Latency evidence
SELECT channel,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency
FROM messages 
WHERE direction = 'outbound'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY channel;

-- Message loss evidence
SELECT COUNT(*) FILTER (WHERE delivery_status = 'failed') * 100.0 / COUNT(*) AS failure_rate
FROM messages
WHERE created_at > NOW() - INTERVAL '24 hours';
```

**Rationale**: Evidence is reproducible. Claims without evidence are opinions. Production decisions require evidence.

---

### XVII. Failure is Information

A failed test is a discovery, not a setback.

**Non-negotiable rules:**
- Every test failure must be documented in `specs/phase3-test-results.md`
- Documentation format: symptom, root cause, fix applied, re-test result
- Tests that reveal bugs in Phases 1 or 2 must be fixed in those layers before re-running Phase 3
- No test failures swept under the rug
- Failure documentation is mandatory, not optional

**Failure Documentation Template:**
```markdown
## Test Failure: [Test Name]

**Symptom**: What failed? (include error messages, logs)

**Root Cause**: Why did it fail? (deep dive analysis)

**Fix Applied**: What was changed? (code, config, infrastructure)

**Re-Test Result**: Did the fix work? (include evidence)

**Prevention**: How do we prevent this in the future?
```

**Rationale**: Failures teach us about the system. Documented failures prevent recurrence. Undocumented failures will repeat.

---

### XVIII. SLA Targets are Hard Floors

The following are minimum thresholds, not aspirational goals.

**Non-negotiable rules:**
- All 6 hard floors MUST be met for production readiness
- If any hard floor is not met, the system is not production-ready
- Debug and retest until all floors are met
- No exceptions, no "close enough"

| Metric | Hard Floor | Measurement |
|--------|------------|-------------|
| **System uptime** (during 24h test) | > 99.9% (max 86 seconds downtime) | `agent_metrics` uptime tracking |
| **P95 processing latency** (all channels) | < 3,000 ms | `messages.latency_ms` |
| **Message loss rate** | 0% (zero tolerance) | `messages.delivery_status` |
| **Escalation rate** | < 25% | `tickets.status = 'escalated'` |
| **Cross-channel identification accuracy** | > 95% | `customer_identifiers` match rate |
| **Web form endpoint latency P95** | < 500 ms | API response time tracking |

**Rationale**: SLAs are promises to customers. Hard floors ensure we can keep those promises. Soft targets lead to production failures.

---

### XIX. Chaos Is Required

Pod kill testing is not optional.

**Non-negotiable rules:**
- The 24-hour test MUST include random pod kills every 2 hours
- The system must self-heal via Kubernetes `restartPolicy: Always` without human intervention
- Any message that was in-flight during a pod kill must be processed exactly once (no duplicates, no drops)
- Chaos testing is mandatory for production readiness

**Chaos Test Script:**
```bash
#!/bin/bash
# Kill a random worker pod every 2 hours
while true; do
  sleep 7200  # 2 hours
  POD=$(kubectl get pods -n customer-success-fte \
        -l component=message-processor \
        -o jsonpath='{.items[0].metadata.name}')
  kubectl delete pod $POD -n customer-success-fte
  echo "Killed pod $POD at $(date)"
done &
```

**Success Criteria:**
- All pods restart automatically
- No messages lost during pod kills
- No duplicate message processing
- System continues processing throughout 24-hour test

**Rationale**: Production failures are inevitable. Systems that can't survive chaos aren't production-ready. Chaos testing builds confidence.

---

### XX. Documentation Completes the System

A system with no runbook is not production-ready.

**Non-negotiable rules:**
- Phase 3 is not complete until ALL documentation is written
- Required documentation:
  - Deployment guide (`README.md`)
  - API documentation (`docs/api.md`)
  - Operational runbook (`docs/runbook.md`)
  - Scoring checklist (`specs/phase3-validation-checklist.md`)
- Documentation must be tested (followed by a fresh developer)
- Untested documentation is incomplete

**Required Documentation:**

| Document | Purpose | Owner |
|----------|---------|-------|
| `README.md` | Deployment guide, setup instructions | Engineering |
| `docs/api.md` | API endpoint documentation | Engineering |
| `docs/runbook.md` | Operational procedures, troubleshooting | Operations |
| `specs/phase3-validation-checklist.md` | Validation scoring checklist | Quality |
| `specs/phase3-test-results.md` | Test results, failures, fixes | Quality |

**Rationale**: Documentation is how knowledge transfers. Undocumented systems depend on individuals. Documented systems survive team changes.

---

## Phase Gate: Must Have From Phase 2

Before Phase 3 testing begins, ALL of the following must be confirmed:

### Code Readiness
- [ ] All Phase 2 tests pass (`pytest tests/ -v` — zero failures)
- [ ] Full Docker Compose stack starts without errors (`docker compose up -d`)
- [ ] Kubernetes deployment active (all pods Running in `customer-success-fte` namespace)
- [ ] `/health` endpoint responds < 100ms
- [ ] At least one real end-to-end web form submission processed by the agent

### Data Readiness
- [ ] PostgreSQL has ≥ 8 knowledge base entries with embeddings
- [ ] All 8 database tables created and accessible
- [ ] Kafka topics created and accessible
- [ ] Connection pool configured and working

### Documentation Readiness
- [ ] `specs/transition-checklist.md` fully completed from Phase 1
- [ ] `specs/phase2-validation-report.md` complete
- [ ] All Phase 2 documentation complete

### Test Readiness
- [ ] All 5 test suites created and passing:
  - `test_queries.py` (5 tests)
  - `test_tools.py` (8 tests)
  - `test_agent.py` (8 tests)
  - `test_channels.py` (9 tests)
  - `test_e2e.py` (8 tests)
- [ ] Test environment configured (Docker Compose or Kubernetes)
- [ ] Test data prepared (sample tickets, knowledge base entries)

**Gate Status**: ALL items must be ✅ before Phase 3 begins.

---

## Phase 3 Test Execution Plan

### Exercise 3.1: Multi-Channel E2E Tests (3-4 hours)

**Objective**: Validate all 7 production scenarios work end-to-end.

**Test Scenarios**:
1. Web form submission → ticket created → status retrievable
2. Gmail webhook (sandbox) → email processed → reply sent
3. WhatsApp webhook (sandbox) → message processed → reply sent
4. Cross-channel customer → web form + email lookup → same customer
5. Channel metrics endpoint → returns breakdown per channel
6. Health check → all channels report "active"
7. Customer lookup → returns customer with history

**Acceptance Criteria**:
- All 7 scenarios pass
- Zero test failures
- All evidence documented

---

### Exercise 3.2: Load Testing (2-3 hours)

**Objective**: Validate system handles concurrent load within SLA.

**Load Parameters**:
- 50 concurrent users
- 5-minute sustained load
- Mix of operations: 60% web form, 30% health checks, 10% metrics

**Success Criteria**:
- 0% failure rate on web form submissions
- P95 latency < 500ms for `/support/submit`
- P99 latency < 100ms for `/health`
- No OOM kills on worker pods during load

**Tool**: Locust

---

### Exercise 3.3: 24-Hour Continuous Operation (24 hours + setup)

**Objective**: Validate system operates continuously without degradation.

**Test Parameters**:
- 24-hour continuous operation
- Traffic pattern: 100+ web form submissions, 50+ email simulations, 50+ WhatsApp simulations
- Chaos injection: Pod kills every 2 hours
- Metrics collection: Continuous

**Success Criteria**:
- Uptime > 99.9% (max 86 seconds downtime)
- P95 latency < 3000ms for all channels
- Zero messages in DLQ
- All pods healthy at end of test

---

### Exercise 3.4: Documentation Validation (1 hour)

**Objective**: Validate all documentation is complete and accurate.

**Validation Steps**:
1. Fresh developer follows deployment guide
2. Fresh developer follows runbook for common troubleshooting
3. All documentation gaps identified and filled

**Success Criteria**:
- Fresh developer can deploy in < 30 minutes
- Fresh developer can troubleshoot common issues
- All documentation gaps filled

---

## Phase 3 → Production Handoff

**Artifacts for Production**:

| Artifact | File | Use in Production |
|----------|------|-------------------|
| Deployment Guide | `README.md` | Production deployment |
| API Documentation | `docs/api.md` | API consumers |
| Runbook | `docs/runbook.md` | Operations team |
| Validation Checklist | `specs/phase3-validation-checklist.md` | Production sign-off |
| Test Results | `specs/phase3-test-results.md` | Quality assurance |
| Phase 2 Artifacts | All Phase 2 files | Production codebase |

---

**Version**: 3.0.0 | **Ratified**: 2026-03-17 | **Last Amended**: 2026-03-17

**Status**: Phase 3 Constitution Ready for Execution
