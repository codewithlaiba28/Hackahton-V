# Tasks: Phase 1 Incubation

**Input**: Design documents from `specs/phase1-incubation/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/mcp-tools.md (✅)

**Tests**: INCLUDED - Test-driven development is mandatory per constitution

**Organization**: Tasks organized by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- Include exact file paths in descriptions

---

## Phase 1: Setup (Environment & Dossier)

**Purpose**: Project initialization and context dossier creation

- [ ] T001 Create project directory structure per plan.md
  - Create: context/, src/channels/, src/agent/, tests/, specs/
  - Create all __init__.py files in src/ subdirectories
  - Initialize git repository
- [ ] T002 Create .env.example with ANTHROPIC_API_KEY= placeholder
- [ ] T003 Create requirements.txt with Phase 1 dependencies (mcp, anthropic, pydantic, pytest, pytest-asyncio, textblob, rich, python-dotenv)
- [ ] T004 Create and activate virtual environment
- [ ] T005 [P] Create context/company-profile.md (TechCorp SaaS company profile with 3 tiers, product features, support model)
- [ ] T006 [P] Create context/product-docs.md (8 sections: API keys, OAuth, webhooks, rate limits, data export, billing, onboarding, troubleshooting - each ≥200 words)
- [ ] T007 [P] Create context/sample-tickets.json (50+ tickets: 15+ email, 20+ WhatsApp, 15+ web form, 5+ escalation triggers)
- [ ] T008 [P] Create context/escalation-rules.md (category triggers, sentiment triggers, channel triggers, fallback rule)
- [ ] T009 [P] Create context/brand-voice.md (core values, tone per channel, what NOT to say, response patterns)

**Checkpoint**: Environment ready - run `python -c "import mcp, anthropic, pydantic"` without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 [P] Implement Channel enum and ChannelMessage dataclass in src/channels/base.py
  - Channel enum: EMAIL, WHATSAPP, WEB_FORM
  - ChannelMessage dataclass with customer_id property
- [ ] T011 [P] Implement Channel Simulators in src/channels/
  - src/channels/email_simulator.py
  - src/channels/whatsapp_simulator.py
  - src/channels/webform_simulator.py
  - Each converts raw dict → ChannelMessage object
- [ ] T012 [P] Implement ConversationMemory and ConversationTurn dataclasses in src/agent/memory.py
- [ ] T013 [P] Implement ConversationMemoryStore with get_or_create(), add_turn(), get_history_text() in src/agent/memory.py
- [ ] T014 [P] Implement Knowledge Base loader and searcher in src/agent/knowledge_base.py
  - Parse context/product-docs.md on startup
  - Implement search(query, max_results=5) -> str with keyword overlap scoring
- [ ] T015 [P] Implement Sentiment Analyzer in src/agent/sentiment.py
  - analyze(text) -> tuple[float, str] with keyword scoring
  - Thresholds: <0.3 negative, >0.7 positive
- [ ] T016 [P] Implement Escalation Logic in src/agent/escalation.py
  - check_escalation(message, sentiment_score, channel) -> tuple[bool, str]
  - Reason codes: legal_threat, pricing_inquiry, refund_request, human_requested, negative_sentiment

**Checkpoint**: Foundation ready - all user stories can now be implemented in parallel

---

## Phase 3: User Story 1 - Product Question via Web Form (Priority: P1) 🎯 MVP

**Goal**: Customer submits question via web form → FTE searches docs → replies with semi-formal response

**Independent Test**: Submit web form with known product question → verify accurate response + ticket created

### Tests for User Story 1 ⚠️

> **Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Create test for web form submission in tests/test_webform.py
  - Test: submit question → response under 300 words, semi-formal tone
  - Test: ticket created with source_channel = web_form
- [ ] T018 [P] [US1] Create integration test in tests/integration/test_webform_flow.py
  - End-to-end: web form → normalizer → KB search → response → ticket

### Implementation for User Story 1

- [ ] T019 [P] [US1] Implement Message Normalizer in src/agent/normalizer.py
  - normalize(ChannelMessage) -> NormalizedMessage with customer_id, content, channel, intent_hint
- [ ] T020 [US1] Implement Channel Formatter for web_form in src/agent/formatter.py
  - format_response(response, channel="web_form") -> str with semi-formal tone
- [ ] T021 [US1] Implement Core Agent Loop skeleton in src/agent/core_loop.py
  - process_message(ChannelMessage) -> AgentResult with ticket_id, response, channel
- [ ] T022 [US1] Wire Knowledge Base search into core loop
  - search_kb(query) called after ticket creation
  - Return formatted snippets with section titles
- [ ] T023 [US1] Implement ticket creation in core loop
  - create_ticket() called BEFORE any response
  - In-memory ticket store with UUID generation
- [ ] T024 [US1] Add system prompt for web form responses in src/agent/prompts.py
  - SYSTEM_PROMPT with web_form tone instructions

**Checkpoint**: US1 functional - can process web form questions with accurate responses

---

## Phase 4: User Story 2 - Casual WhatsApp Inquiry (Priority: P1)

**Goal**: Customer sends casual WhatsApp message → FTE detects tone → replies <160 chars

**Independent Test**: Send WhatsApp message → verify response <300 chars, conversational tone

### Tests for User Story 2 ⚠️

- [ ] T025 [P] [US2] Create test for WhatsApp response length in tests/test_whatsapp.py
  - Test: response ≤300 chars (preferred 160)
  - Test: conversational tone, no formal greeting
- [ ] T026 [P] [US2] Create integration test in tests/integration/test_whatsapp_flow.py
  - End-to-end: WhatsApp → normalizer → KB search → concise response

### Implementation for User Story 2

- [ ] T027 [P] [US2] Implement Channel Formatter for whatsapp in src/agent/formatter.py
  - format_response(response, channel="whatsapp") -> str truncated to 300 chars
  - Add support prompt: "📱 Type 'human' for live support."
- [ ] T028 [US2] Update Core Agent Loop for WhatsApp channel detection
  - Detect channel from ChannelMessage.channel == Channel.WHATSAPP
  - Apply WhatsApp-specific formatting
- [ ] T029 [US2] Add system prompt section for WhatsApp in src/agent/prompts.py
  - Conversational tone, concise responses, emoji optional

**Checkpoint**: US2 functional - WhatsApp responses are concise and conversational

---

## Phase 5: User Story 3 - Pricing Inquiry Escalation (Priority: P1)

**Goal**: Customer asks about pricing → FTE does NOT answer → escalates immediately

**Independent Test**: Ask pricing question → verify NO pricing info revealed, escalation triggered

### Tests for User Story 3 ⚠️

- [ ] T030 [P] [US3] Create test for pricing escalation in tests/test_escalation.py
  - Test: "What's the price?" → escalate=True, reason="pricing_inquiry"
  - Test: NO pricing info in response
- [ ] T031 [P] [US3] Create integration test in tests/integration/test_pricing_escalation.py
  - End-to-end: pricing question → escalation → customer notified

### Implementation for User Story 3

- [ ] T032 [P] [US3] Add pricing keywords to escalation logic in src/agent/escalation.py
  - PRICING_KEYWORDS = ["price", "cost", "pricing", "how much", "enterprise plan"]
- [ ] T033 [US3] Update Core Agent Loop to check escalation BEFORE generating response
  - check_escalation() called after sentiment analysis
  - If escalate=True, skip KB search, create escalation record
- [ ] T034 [US3] Implement MCP tool: escalate_to_human in src/mcp_server.py
  - Input: ticket_id, reason, context, urgency
  - Output: escalation_id confirmation
- [ ] T035 [US3] Add pricing constraint to system prompt in src/agent/prompts.py
  - "NEVER discuss pricing → escalate immediately with reason pricing_inquiry"

**Checkpoint**: US3 functional - pricing inquiries always escalate, never answered

---

## Phase 6: User Story 4 - Angry Customer Escalation (Priority: P1)

**Goal**: Customer sends angry message (sentiment <0.3) → FTE responds empathetically → escalates

**Independent Test**: Send angry message → verify sentiment <0.3, escalation triggered, empathetic response

### Tests for User Story 4 ⚠️

- [ ] T036 [P] [US4] Create test for negative sentiment escalation in tests/test_sentiment.py
  - Test: "This is BROKEN and useless!" → score <0.3, escalate=True
- [ ] T037 [P] [US4] Create integration test in tests/integration/test_angry_customer.py
  - End-to-end: angry message → empathy → escalation

### Implementation for User Story 4

- [ ] T038 [P] [US4] Add negative keywords to sentiment analyzer in src/agent/sentiment.py
  - NEGATIVE_KEYWORDS with weights: "broken", "useless", "terrible", "frustrated"
- [ ] T039 [US4] Update escalation logic for sentiment threshold in src/agent/escalation.py
  - if sentiment_score < 0.3 → return (True, "negative_sentiment")
- [ ] T040 [US4] Add empathy response template in src/agent/formatter.py
  - Empathetic opening before escalation notice
- [ ] T041 [US4] Update system prompt for angry customers in src/agent/prompts.py
  - "Respond with empathy before escalating"

**Checkpoint**: US4 functional - angry customers detected, responded to with empathy, escalated

---

## Phase 7: User Story 5 - Human Escalation Request (Priority: P1)

**Goal**: Customer types "human" → FTE escalates immediately without AI response

**Independent Test**: Send "I want a human" → verify immediate escalation, no AI response

### Tests for User Story 5 ⚠️

- [ ] T042 [P] [US5] Create test for human request escalation in tests/test_escalation.py
  - Test: "I want to speak to a human" → escalate=True, reason="human_requested"
- [ ] T043 [P] [US5] Create integration test in tests/integration/test_human_request.py
  - End-to-end: human request → immediate escalation

### Implementation for User Story 5

- [ ] T044 [P] [US5] Add human keywords to escalation logic in src/agent/escalation.py
  - HUMAN_KEYWORDS = ["human", "agent", "representative", "real person"]
- [ ] T045 [US5] Update Core Agent Loop to check human request FIRST
  - Check escalation BEFORE KB search, BEFORE response generation
  - Immediate escalation, no AI response

**Checkpoint**: US5 functional - human requests escalate immediately

---

## Phase 8: User Story 6 - Detailed Email Inquiry (Priority: P2)

**Goal**: Customer emails detailed question → FTE responds formally with greeting + signature

**Independent Test**: Send email → verify greeting, signature, detailed response (up to 500 words)

### Tests for User Story 6 ⚠️

- [ ] T046 [P] [US6] Create test for email response format in tests/test_email.py
  - Test: response contains "Dear [Name]" and "Best regards"
  - Test: response up to 500 words, detailed
- [ ] T047 [P] [US6] Create integration test in tests/integration/test_email_flow.py
  - End-to-end: email → formal response with greeting + signature

### Implementation for User Story 6

- [ ] T048 [P] [US6] Implement Channel Formatter for email in src/agent/formatter.py
  - format_response(response, channel="email", customer_name, ticket_id)
  - Add greeting: "Dear [Name]," or "Dear Customer,"
  - Add signature: "Best regards, TechCorp AI Support Team"
- [ ] T049 [US6] Update system prompt for email in src/agent/prompts.py
  - Formal tone, detailed responses, greeting + signature required

**Checkpoint**: US6 functional - email responses are formal with proper greeting and signature

---

## Phase 9: User Story 7 - Follow-Up on Same Topic (Priority: P2)

**Goal**: Customer asks follow-up → FTE retrieves history → references prior context

**Independent Test**: Send follow-up → verify history retrieved, context referenced in response

### Tests for User Story 7 ⚠️

- [ ] T050 [P] [US7] Create test for conversation history in tests/test_memory.py
  - Test: customer with prior history → get_history_text() returns all turns
- [ ] T051 [P] [US7] Create integration test in tests/integration/test_followup.py
  - End-to-end: follow-up question → history retrieved → context acknowledged

### Implementation for User Story 7

- [ ] T052 [P] [US7] Implement cross-channel history lookup in src/agent/memory.py
  - get_history_text() returns turns from ALL channels for same customer_id
- [ ] T053 [US7] Update Core Agent Loop to retrieve history for every message
  - get_customer_history(customer_id) called after ticket creation
  - Pass history to LLM prompt for context
- [ ] T054 [US7] Add follow-up detection to normalizer in src/agent/normalizer.py
  - is_followup = memory.get_or_create(customer_id).turns > 0
- [ ] T055 [US7] Update system prompt for follow-ups in src/agent/prompts.py
  - "Reference prior context when customer asks follow-up questions"

**Checkpoint**: US7 functional - follow-ups reference prior conversation context

---

## Phase 10: MCP Server & Tool Exposure

**Purpose**: Expose all agent capabilities as MCP tools for Claude Code invocation

- [ ] T056 [P] Implement MCP Server skeleton in src/mcp_server.py
  - Use mcp.server.Server
  - Register 6 tool endpoints
- [ ] T057 [P] [P] Implement MCP tool: search_knowledge_base in src/mcp_server.py
  - Input: query, max_results, category
  - Output: formatted search results
- [ ] T058 [P] Implement MCP tool: create_ticket in src/mcp_server.py
  - Input: customer_id, issue, priority, channel
  - Output: ticket_id
- [ ] T059 [P] Implement MCP tool: get_customer_history in src/mcp_server.py
  - Input: customer_id, limit
  - Output: formatted history
- [ ] T060 [P] Implement MCP tool: send_response in src/mcp_server.py
  - Input: ticket_id, message, channel
  - Output: delivery_status
- [ ] T061 [P] Implement MCP tool: analyze_sentiment in src/mcp_server.py
  - Input: message
  - Output: score, label, should_escalate

**Checkpoint**: All 6 MCP tools callable without error

---

## Phase 11: Integration Testing & Discovery

**Purpose**: Run hackathon exercises, document discoveries, validate all scenarios

- [ ] T062 Run Exercise 1.1: Claude Code Exploration (2-3 hours)
  - Launch Claude Code with dossier context
  - Submit exploration prompt from Hackathon.md
  - Document ≥5 discoveries in specs/discovery-log.md
- [ ] T063 Run Exercise 1.2: Prototype Core Loop (4-5 hours)
  - Test with 3 channel scenarios
  - Iterate based on failures
  - Document iterations in discovery-log.md
- [ ] T064 Run Exercise 1.3: Add Memory (3-4 hours)
  - Test follow-up scenarios
  - Verify cross-channel history
- [ ] T065 Run Exercise 1.4: Build MCP Server (3-4 hours)
  - Verify all 6 tools callable
  - Test tool execution order
- [ ] T066 Document Edge Cases (≥10) in specs/discovery-log.md
  - Format: Edge Case | Input | Correct Behavior | Test Added?
- [ ] T067 Write Core Interaction Loop Tests (tests/test_core_loop.py)
  - All 7 user scenarios as passing tests
- [ ] T068 Formalize Agent Skills Manifest in src/skills_manifest.py
  - All 5 skills defined with triggers, inputs, outputs, fallbacks

**Checkpoint**: All exercises complete, ≥10 edge cases documented, all 7 scenarios passing

---

## Phase 12: Phase 1 Exit Gate

**Purpose**: Crystallize specification, complete transition checklist, final validation

- [ ] T069 Write Crystallized Specification in specs/customer-success-fte-spec.md
  - Purpose, Supported Channels table, Scope, Tools table
  - Performance requirements (measured from testing)
  - Guardrails
- [ ] T070 Complete Transition Checklist in specs/transition-checklist.md
  - Discovered Requirements, Working Prompts, Edge Cases, Response Patterns
  - Escalation Rules (finalized), Performance Baseline
- [ ] T071 Final Phase 1 Validation Run
  - Run: pytest tests/ -v --tb=short
  - Run: python src/mcp_server.py --list-tools
  - Run: python -c "from src.skills_manifest import AGENT_SKILLS; print(list(AGENT_SKILLS.keys()))"
  - Verify: All tests pass, 6+ tools listed, 5 skills in manifest

**Checkpoint**: Phase 1 COMPLETE - ready for Phase 2 transition

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundation)
    ↓
Phase 3 (US1: Web Form) → MVP
    ↓
Phase 4 (US2: WhatsApp)
    ↓
Phase 5 (US3: Pricing Escalation)
    ↓
Phase 6 (US4: Angry Customer)
    ↓
Phase 7 (US5: Human Request)
    ↓
Phase 8 (US6: Email)
    ↓
Phase 9 (US7: Follow-Up)
    ↓
Phase 10 (MCP Server)
    ↓
Phase 11 (Integration Testing)
    ↓
Phase 12 (Exit Gate) → Phase 2 Ready
```

## Parallel Execution Opportunities

**After Phase 2 (Foundation):**

- US1 (T019-T024), US2 (T027-T029), US3 (T032-T035) can run in parallel
- US4 (T038-T041), US5 (T044-T045) can run in parallel
- US6 (T048-T049), US7 (T052-T055) can run in parallel
- MCP Tools (T057-T061) can run in parallel

**Suggested MVP Scope:**

- Phase 1 + Phase 2 + Phase 3 (US1 only)
- Delivers: Web form support with KB search, ticket creation, basic responses
- Independent test: Submit web form → accurate response + ticket created

---

## Implementation Strategy

**MVP First**: Implement US1 (Web Form) completely before moving to other channels

**Incremental Delivery**:
1. MVP: US1 only (web form, basic KB search, ticket creation)
2. Increment 1: US2 + US3 (WhatsApp, pricing escalation)
3. Increment 2: US4 + US5 (angry customer, human request)
4. Increment 3: US6 + US7 (email, follow-up context)
5. Full: All 7 user stories + MCP server

**Cross-Cutting Concerns**:
- Error handling: Added in each story's implementation tasks
- Logging: Added in each story's implementation tasks
- Testing: Tests written FIRST for each story (TDD)

---

**Total Tasks**: 71
**Tasks per Phase**:
- Phase 1: 9 tasks (Setup)
- Phase 2: 6 tasks (Foundation)
- Phase 3: 8 tasks (US1)
- Phase 4: 5 tasks (US2)
- Phase 5: 6 tasks (US3)
- Phase 6: 6 tasks (US4)
- Phase 7: 4 tasks (US5)
- Phase 8: 4 tasks (US6)
- Phase 9: 6 tasks (US7)
- Phase 10: 6 tasks (MCP)
- Phase 11: 7 tasks (Testing)
- Phase 12: 3 tasks (Exit)
