# Tasks: Phase 2 Specialization

**Input**: Design documents from `specs/phase2-specialization/`
**Prerequisites**: plan.md (✅), spec.md (✅), data-model.md (✅), contracts/ (pending)

**Tests**: INCLUDED - Test-driven development mandatory per constitution

**Organization**: Tasks organized by milestone to enable incremental delivery and testing

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which milestone this task belongs to (e.g., [MILESTONE-A], [MILESTONE-B])
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Project structure and configuration

- [ ] T001 Create production/ directory structure per plan.md
- [ ] T002 Create production/agent/, production/channels/, production/workers/, production/api/, production/database/, production/web-form/, production/tests/, production/k8s/ directories
- [ ] T003 Create all __init__.py files in Python packages
- [ ] T004 Create production/.env.example with all required env vars (DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS, OPENAI_API_KEY, etc.)
- [ ] T005 Create production/requirements.txt with all Phase 2 dependencies
- [ ] T006 Create production/Dockerfile with multi-stage build (base, api, worker)
- [ ] T007 Create production/docker-compose.yml with postgres, kafka, zookeeper, api, worker services
- [ ] T008 Create production/docker-compose.dev.yml with dev overrides

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database foundation that ALL milestones depend on

### MILESTONE A: Database Foundation

- [ ] T009 [MILESTONE-A] Initialize PostgreSQL with pgvector via Docker Compose
- [ ] T010 [MILESTONE-A] Create production/database/schema.sql with all 8 tables
- [ ] T011 [MILESTONE-A] Create production/database/migrations/001_initial_schema.sql
- [ ] T012 [MILESTONE-A] Create production/database/migrate.py migration runner
- [ ] T013 [P] [MILESTONE-A] Implement customer queries in production/database/queries.py
- [ ] T014 [P] [MILESTONE-A] Implement conversation queries in production/database/queries.py
- [ ] T015 [P] [MILESTONE-A] Implement message queries in production/database/queries.py
- [ ] T016 [P] [MILESTONE-A] Implement ticket queries in production/database/queries.py
- [ ] T017 [P] [MILESTONE-A] Implement knowledge base queries in production/database/queries.py
- [ ] T018 [P] [MILESTONE-A] Implement metrics queries in production/database/queries.py
- [ ] T019 [MILESTONE-A] Create production/database/seed_knowledge_base.py script
- [ ] T020 [MILESTONE-A] Write tests/test_queries.py with 5 query test cases

**Checkpoint**: Database foundation ready - all tables created, queries tested, knowledge base seeded

---

## Phase 3: Tool Migration (MILESTONE B)

**Purpose**: Migrate 5 MCP tools to OpenAI SDK @function_tool

### MILESTONE B: Tool Migration

- [ ] T021 [MILESTONE-B] Implement Pydantic input models in production/agent/tools.py
- [ ] T022 [P] [MILESTONE-B] Implement @function_tool: search_knowledge_base in production/agent/tools.py
- [ ] T023 [P] [MILESTONE-B] Implement @function_tool: create_ticket in production/agent/tools.py
- [ ] T024 [P] [MILESTONE-B] Implement @function_tool: get_customer_history in production/agent/tools.py
- [ ] T025 [P] [MILESTONE-B] Implement @function_tool: escalate_to_human in production/agent/tools.py
- [ ] T026 [P] [MILESTONE-B] Implement @function_tool: send_response in production/agent/tools.py
- [ ] T027 [MILESTONE-B] Implement channel formatters in production/agent/formatters.py
- [ ] T028 [MILESTONE-B] Write tests/test_tools.py with tool unit tests

**Checkpoint**: All 5 tools migrated and tested with real PostgreSQL

---

## Phase 4: Agent Definition (MILESTONE C)

**Purpose**: Define production agent with OpenAI Agents SDK

### MILESTONE C: Agent Definition

- [ ] T029 [MILESTONE-C] Migrate system prompt to production/agent/prompts.py
- [ ] T030 [MILESTONE-C] Define production agent in production/agent/customer_success_agent.py
- [ ] T031 [MILESTONE-C] Write tests/test_agent.py with 6+ transition tests
- [ ] T032 [MILESTONE-C] Run transition test suite and fix failures

**Checkpoint**: Agent instantiated, all transition tests pass

---

## Phase 5: Channel Handlers (MILESTONE D)

**Purpose**: Real channel integrations (Gmail, WhatsApp, Web Form)

### MILESTONE D: Channel Handlers

- [ ] T033 [P] [MILESTONE-D] Implement Gmail handler in production/channels/gmail_handler.py
- [ ] T034 [P] [MILESTONE-D] Implement WhatsApp handler in production/channels/whatsapp_handler.py
- [ ] T035 [P] [MILESTONE-D] Implement web form handler in production/channels/web_form_handler.py
- [ ] T036 [MILESTONE-D] Build React Web Support Form in production/web-form/SupportForm.jsx
- [ ] T037 [MILESTONE-D] Create production/web-form/package.json
- [ ] T038 [MILESTONE-D] Write production/web-form/README.md with embedding instructions
- [ ] T039 [MILESTONE-D] Write tests/test_channels.py with channel handler tests

**Checkpoint**: All 3 channel handlers working, React form submits and displays ticket ID

---

## Phase 6: Kafka Integration (MILESTONE E)

**Purpose**: Event streaming backbone

### MILESTONE E: Kafka Integration

- [ ] T040 [MILESTONE-E] Set up Kafka client in production/kafka_client.py
- [ ] T041 [MILESTONE-E] Wire Gmail handler to Kafka in production/channels/gmail_handler.py
- [ ] T042 [MILESTONE-E] Wire WhatsApp handler to Kafka in production/channels/whatsapp_handler.py
- [ ] T043 [MILESTONE-E] Wire web form handler to Kafka in production/channels/web_form_handler.py
- [ ] T044 [MILESTONE-E] Implement unified message processor in production/workers/message_processor.py
- [ ] T045 [MILESTONE-E] Implement metrics collector in production/workers/metrics_collector.py
- [ ] T046 [MILESTONE-E] Write tests/test_kafka.py with Kafka integration tests

**Checkpoint**: Messages flow end-to-end through Kafka, offset committed after DB write

---

## Phase 7: FastAPI Service (MILESTONE F)

**Purpose**: API layer with all endpoints

### MILESTONE F: FastAPI Service

- [ ] T047 [MILESTONE-F] Build FastAPI application in production/api/main.py
- [ ] T048 [MILESTONE-F] Implement all 9 API endpoints
- [ ] T049 [MILESTONE-F] Configure CORS middleware
- [ ] T050 [MILESTONE-F] Implement startup/shutdown events (Kafka + DB pool)
- [ ] T051 [MILESTONE-F] Write tests/test_e2e.py with 8+ API integration tests

**Checkpoint**: All endpoints tested, /health responds < 100ms, Swagger UI shows all endpoints

---

## Phase 8: Kubernetes Deployment (MILESTONE G)

**Purpose**: Production orchestration

### MILESTONE G: Kubernetes Deployment

- [ ] T052 [MILESTONE-G] Write production/k8s/namespace.yaml
- [ ] T053 [MILESTONE-G] Write production/k8s/configmap.yaml
- [ ] T054 [MILESTONE-G] Write production/k8s/secrets.yaml (template only)
- [ ] T055 [MILESTONE-G] Write production/k8s/deployment-api.yaml
- [ ] T056 [MILESTONE-G] Write production/k8s/deployment-worker.yaml
- [ ] T057 [MILESTONE-G] Write production/k8s/service.yaml
- [ ] T058 [MILESTONE-G] Write production/k8s/ingress.yaml
- [ ] T059 [MILESTONE-G] Write production/k8s/hpa.yaml
- [ ] T060 [MILESTONE-G] Test local Kubernetes deployment with minikube

**Checkpoint**: All pods Running, HPA visible, /health reachable via port-forward

---

## Phase 9: Integration Testing (MILESTONE H)

**Purpose**: End-to-end validation

### MILESTONE H: Integration Testing & Validation

- [ ] T061 [MILESTONE-H] Write multi-channel E2E tests in tests/test_multichannel_e2e.py
- [ ] T062 [MILESTONE-H] Write load tests in tests/load_test.py (Locust)
- [ ] T063 [MILESTONE-H] Create 24-hour simulation script in tests/simulate_24h.py
- [ ] T064 [MILESTONE-H] Run load test and validate P95 latency < 500ms
- [ ] T065 [MILESTONE-H] Run 24-hour simulation and validate metrics
- [ ] T066 [MILESTONE-H] Validate 24-hour test metrics with SQL queries

**Checkpoint**: All tests pass, load test SLA met, 24-hour metrics within targets

---

## Phase 10: Documentation (MILESTONE I)

**Purpose**: Operational readiness

### MILESTONE I: Phase 2 Documentation

- [ ] T067 [MILESTONE-I] Write production/README.md deployment guide
- [ ] T068 [MILESTONE-I] Complete Phase 2 validation report in specs/phase2-validation-report.md
- [ ] T069 [MILESTONE-I] Create channel setup instructions (Gmail API, Twilio Sandbox)
- [ ] T070 [MILESTONE-I] Write web form embedding instructions

**Checkpoint**: Fresh developer can follow guide to get system running in < 30 minutes

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and handoff

- [ ] T071 Run full test suite (pytest tests/ -v)
- [ ] T072 Run constitution compliance check
- [ ] T073 Create Phase 2 → Phase 3 handoff document
- [ ] T074 Tag release v2.0.0

**Checkpoint**: All tests pass, constitution compliant, release tagged

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (MILESTONE A: Database Foundation)
    ↓
Phase 3 (MILESTONE B: Tool Migration)
    ↓
Phase 4 (MILESTONE C: Agent Definition)
    ↓
Phase 5 (MILESTONE D: Channel Handlers)
    ↓
Phase 6 (MILESTONE E: Kafka Integration)
    ↓
Phase 7 (MILESTONE F: FastAPI Service)
    ↓
Phase 8 (MILESTONE G: Kubernetes Deployment)
    ↓
Phase 9 (MILESTONE H: Integration Testing)
    ↓
Phase 10 (MILESTONE I: Documentation)
    ↓
Phase 11 (Polish & Validation)
```

---

## Parallel Execution Opportunities

**After Phase 2 (Database Foundation):**

- MILESTONE B (T022-T026): Tool migration tasks can run in parallel
- MILESTONE D (T033-T035): Channel handlers can run in parallel
- MILESTONE G (T052-T058): Kubernetes manifests can run in parallel

**Within MILESTONE A:**

- T013-T018: Query implementation can run in parallel (different domains)

---

## Implementation Strategy

**MVP First**: MILESTONE A + MILESTONE B + MILESTONE C

- Database schema (8 tables)
- 5 @function_tool functions
- Production agent definition
- Transition tests passing

**Increment 1**: Add MILESTONE D (Channel Handlers)

- Gmail, WhatsApp, Web Form handlers
- React Web Support Form

**Increment 2**: Add MILESTONE E + F (Kafka + FastAPI)

- Event streaming backbone
- All 9 API endpoints

**Increment 3**: Add MILESTONE G + H (Kubernetes + Testing)

- Kubernetes deployment
- E2E tests, load tests, 24-hour simulation

**Full Delivery**: All milestones complete with documentation

---

## Task Summary

| Milestone | Tasks | Testable Increment |
|-----------|-------|-------------------|
| Phase 1: Setup | 8 | Project structure ready |
| MILESTONE A: Database | 12 | All 8 tables created, queries tested |
| MILESTONE B: Tools | 8 | 5 @function_tool functions working |
| MILESTONE C: Agent | 4 | Agent instantiated, tests passing |
| MILESTONE D: Channels | 7 | All 3 handlers + React form working |
| MILESTONE E: Kafka | 7 | End-to-end Kafka flow |
| MILESTONE F: FastAPI | 5 | All 9 endpoints tested |
| MILESTONE G: K8s | 9 | Pods Running, HPA tested |
| MILESTONE H: Testing | 6 | All tests pass, SLA met |
| MILESTONE I: Docs | 4 | Deployment guide complete |
| Phase 11: Polish | 4 | Release tagged v2.0.0 |

**Total Tasks**: 74
**Total Milestones**: 10 (A-I + Setup + Polish)

---

**Next Step**: Begin implementation with `/sp.implement` command, starting with MILESTONE A (Database Foundation)
