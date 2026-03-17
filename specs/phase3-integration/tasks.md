# Tasks: Phase 3 Integration Testing

**Input**: Design documents from `specs/phase3-integration/`
**Prerequisites**: plan.md (✅), spec.md (✅)

**Tests**: INCLUDED - Test-driven development mandatory per constitution

**Organization**: Tasks organized by milestone to enable incremental testing and validation

---

## Format: `[ID] [P?] [Milestone] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Milestone]**: Which milestone this task belongs to (e.g., [MILESTONE-A], [MILESTONE-B])
- Include exact file paths in descriptions

---

## Phase 1: Pre-Flight Checks (MILESTONE A)

**Purpose**: Verify entire Phase 2 deployment is operational before testing begins

### MILESTONE A: Pre-Flight Checks

- [ ] T001 [MILESTONE-A] Run full stack health check (Docker Compose, Database, KB, API, Kafka, K8s, Phase 2 tests)
- [ ] T002 [MILESTONE-A] Create test results tracking file (specs/phase3-test-results.md)

**Checkpoint**: All 7 pre-flight checks pass; tracking file ready

---

## Phase 2: Channel Integration Tests (MILESTONE B)

**Purpose**: Verify each channel processes messages correctly end-to-end

### MILESTONE B: Channel Integration Tests

- [ ] T003 [P] [MILESTONE-B] Run Test A1: Web Form Full Lifecycle (tests/test_multichannel_e2e.py::TestWebFormChannel)
- [ ] T004 [P] [MILESTONE-B] Run Test A2: Email Channel via Kafka Injection (tests/test_multichannel_e2e.py::TestEmailChannel)
- [ ] T005 [P] [MILESTONE-B] Run Test A3: WhatsApp Channel via Kafka Injection (tests/test_multichannel_e2e.py::TestWhatsAppChannel)
- [ ] T006 [P] [MILESTONE-B] Run Test A4: Gmail Webhook Endpoint (tests/test_multichannel_e2e.py::TestEmailChannel::test_gmail_webhook_processing)
- [ ] T007 [P] [MILESTONE-B] Run Test A5: WhatsApp Webhook Security (tests/test_multichannel_e2e.py::TestWhatsAppChannel::test_whatsapp_webhook_processing)

**Checkpoint**: All A-tests (A1-A5) pass; manual verification complete

---

## Phase 3: Cross-Channel & Escalation Tests (MILESTONE C)

**Purpose**: Verify cross-channel continuity and all escalation paths work correctly

### MILESTONE C: Cross-Channel & Escalation Tests

- [ ] T008 [P] [MILESTONE-C] Run Test B1: Cross-Channel Customer Unification (tests/test_multichannel_e2e.py::TestCrossChannelContinuity)
- [ ] T009 [P] [MILESTONE-C] Run Test B2: Cross-Channel History in Agent Response (tests/test_multichannel_e2e.py::TestCrossChannelContinuity)
- [ ] T010 [P] [MILESTONE-C] Create escalation test file (tests/test_escalation_paths.py)
- [ ] T011 [P] [MILESTONE-C] Run Test C1: Pricing Escalation (tests/test_escalation_paths.py::test_pricing_escalation)
- [ ] T012 [P] [MILESTONE-C] Run Test C2: Legal Threat Escalation (tests/test_escalation_paths.py::test_legal_threat_escalation)
- [ ] T013 [P] [MILESTONE-C] Run Test C3: Negative Sentiment Escalation (tests/test_escalation_paths.py::test_negative_sentiment_escalation)
- [ ] T014 [P] [MILESTONE-C] Run Test C4: Human Requested Escalation (tests/test_escalation_paths.py::test_human_request_escalation)
- [ ] T015 [P] [MILESTONE-C] Run Test C5: Refund Request Escalation (tests/test_escalation_paths.py::test_refund_escalation)

**Checkpoint**: All B-tests (B1-B2) and C-tests (C1-C5) pass; DB verification complete

---

## Phase 4: Agent Behavior Tests (MILESTONE D)

**Purpose**: Verify agent follows correct tool call order and handles all edge cases

### MILESTONE D: Agent Behavior Tests

- [ ] T016 [MILESTONE-D] Run Test D1: Tool Call Order Enforcement (verify via SQL query)
- [ ] T017 [MILESTONE-D] Run Test D2: Edge Case - Empty Message (web form validation)
- [ ] T018 [MILESTONE-D] Run Test D3: Edge Case - Very Long Message (2000+ chars)
- [ ] T019 [MILESTONE-D] Run Test D4: Edge Case - Non-English Message
- [ ] T020 [MILESTONE-D] Run Test D5: Edge Case - Duplicate Submission

**Checkpoint**: All D-tests (D1-D5) pass; tool order verified in DB

---

## Phase 5: Load Tests (MILESTONE E)

**Purpose**: Verify system meets SLA targets under concurrent load

### MILESTONE E: Load Tests

- [ ] T021 [MILESTONE-E] Run Load Test E1: Zero Failure Rate (50 users, 5 minutes) via Locust
- [ ] T022 [MILESTONE-E] Run Load Test E2: Agent Processing Under Load (100 Kafka messages)
- [ ] T023 [MILESTONE-E] Generate Locust HTML report (specs/load-test-e1-report.html)
- [ ] T024 [MILESTONE-E] Validate P95 latency < 500ms for /support/submit
- [ ] T025 [MILESTONE-E] Validate P95 latency < 3000ms for agent processing

**Checkpoint**: All E-tests (E1-E2) pass; all SLA targets met

---

## Phase 6: Resilience Tests (MILESTONE F)

**Purpose**: Verify system recovers from pod kills, DB restarts without message loss

### MILESTONE F: Resilience Tests

- [ ] T026 [MILESTONE-F] Create resilience test script (tests/resilience/test_worker_kill.sh)
- [ ] T027 [MILESTONE-F] Run Test F1: Worker Pod Kill (kubectl delete pod, verify restart + message processed)
- [ ] T028 [MILESTONE-F] Run Test F2: API Pod Kill (delete all 3 API pods, verify restart)
- [ ] T029 [MILESTONE-F] Run Test F3: DB Connection Recovery (docker compose restart postgres)
- [ ] T030 [MILESTONE-F] Verify no message loss during resilience tests (DLQ empty)

**Checkpoint**: All F-tests (F1-F3) pass; no duplicates, no message loss

---

## Phase 7: 24-Hour Test Launch (MILESTONE G)

**Purpose**: Launch 24-hour continuous operation test with chaos injection

### MILESTONE G: 24-Hour Test Launch

- [ ] T031 [MILESTONE-G] Pre-launch verification (clean DB state, note baseline pod states)
- [ ] T032 [MILESTONE-G] Launch 24-hour simulation (tests/simulate_24h.py --duration 86400 --chaos-interval 7200)
- [ ] T033 [MILESTONE-G] Set up monitoring (tmux session, log tailing)
- [ ] T034 [MILESTONE-G] Mid-test monitoring (run every few hours: SQL health check, pod status)

**Checkpoint**: Simulation running; Kafka topics show messages flowing; logs growing

---

## Phase 8: Documentation Sprint (MILESTONE H)

**Purpose**: Complete all required documentation deliverables

### MILESTONE H: Documentation Sprint

- [ ] T035 [P] [MILESTONE-H] Write Deployment Guide (docs/deployment-guide.md)
- [ ] T036 [P] [MILESTONE-H] Write API Reference (docs/api-reference.md)
- [ ] T037 [P] [MILESTONE-H] Write Incident Runbook (docs/runbook.md)
- [ ] T038 [P] [MILESTONE-H] Write Web Form Integration Guide (docs/web-form-integration.md)

**Checkpoint**: All 4 documentation deliverables complete

---

## Phase 9: Final Validation (MILESTONE I)

**Purpose**: Validate 24-hour test results and complete final scoring

### MILESTONE I: Final Validation

- [ ] T039 [MILESTONE-I] Execute 10 SQL validation queries (specs/24h-metrics-report.md)
- [ ] T040 [MILESTONE-I] Record all SLA metrics (uptime, latency, loss, escalation, ID accuracy)
- [ ] T041 [MILESTONE-I] Complete Final Scoring Checklist (specs/final-scoring-checklist.md)
- [ ] T042 [MILESTONE-I] Calculate total score (___ / 100)
- [ ] T043 [MILESTONE-I] Document gaps and improvements

**Checkpoint**: All SLA targets pass; final score calculated; Phase 3 complete

---

## Dependency Graph

```
MILESTONE A (Pre-Flight)
    ↓
MILESTONE B (Channel Integration)
    ↓
MILESTONE C (Cross-Channel + Escalation)
    ↓
MILESTONE D (Agent Behavior)
    ↓
MILESTONE E (Load Tests)
    ↓
MILESTONE F (Resilience Tests)
    ↓
MILESTONE G (24-Hour Launch)
    ↓
MILESTONE H (Documentation)
    ↓
MILESTONE I (Final Validation)
```

---

## Parallel Execution Opportunities

**Within MILESTONE B**:
- T003-T007 (A1-A5 tests) can run in parallel

**Within MILESTONE C**:
- T008-T009 (B1-B2) can run in parallel
- T011-T015 (C1-C5) can run in parallel

**Within MILESTONE D**:
- T017-T020 (D2-D5 edge cases) can run in parallel

**Within MILESTONE H**:
- T035-T038 (all documentation) can run in parallel

---

## Implementation Strategy

**MVP First**: MILESTONE A + MILESTONE B

- Pre-flight checks pass
- All channel integration tests (A1-A5) pass
- Ready for escalation testing

**Increment 1**: Add MILESTONE C (Escalation Tests)

- All 5 escalation paths verified (C1-C5)
- Cross-channel continuity verified (B1-B2)

**Increment 2**: Add MILESTONE D + E (Agent + Load)

- Agent behavior verified (D1-D5)
- Load tests pass (E1-E2)

**Increment 3**: Add MILESTONE F + G (Resilience + 24-Hour)

- Resilience tests pass (F1-F3)
- 24-hour test launched

**Full Delivery**: All milestones complete with documentation

---

## Task Summary

| Milestone | Tasks | Testable Increment |
|-----------|-------|-------------------|
| MILESTONE A: Pre-Flight | 2 | All systems green |
| MILESTONE B: Channel Integration | 5 | All A-tests pass |
| MILESTONE C: Cross-Channel + Escalation | 8 | All B,C-tests pass |
| MILESTONE D: Agent Behavior | 5 | All D-tests pass |
| MILESTONE E: Load Tests | 5 | All SLA targets met |
| MILESTONE F: Resilience Tests | 5 | All F-tests pass |
| MILESTONE G: 24-Hour Launch | 4 | Simulation running |
| MILESTONE H: Documentation | 4 | All docs complete |
| MILESTONE I: Final Validation | 5 | All G1 criteria met |

**Total Tasks**: 43
**Total Milestones**: 9 (A-I)

---

**Next Step**: Begin implementation with `/sp.implement` command, starting with MILESTONE A (Pre-Flight Checks)
