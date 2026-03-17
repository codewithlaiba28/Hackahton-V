# Implementation Plan: Phase 1 Incubation

**Branch**: `phase1-incubation` | **Date**: 2026-03-17 | **Spec**: specs/phase1-incubation/spec.md

**Input**: Feature specification for Customer Success FTE Phase 1 - Incubation

## Summary

Build a working prototype of a Customer Success AI agent that handles support inquiries from three channels (email, WhatsApp, web form) using Claude Code as the Agent Factory. The prototype will use in-memory storage, flat-file knowledge base, and MCP server for tool exposure.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: MCP Server, Anthropic SDK (Claude), Pydantic, pytest, pytest-asyncio
**Storage**: In-memory dictionary (session-scoped)
**Testing**: pytest with async support
**Target Platform**: Local development (Windows/Unix)
**Project Type**: Single Python package
**Performance Goals**: <3 seconds processing time, <30 seconds delivery
**Constraints**: 16-hour development window, simulated channel integrations
**Scale/Scope**: Prototype for 50+ test scenarios, 10+ edge cases documented

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Specification-First Law: This plan is created AFTER spec.md completion
- ✅ Channel-Awareness Mandate: All components are channel-aware (email, whatsapp, web_form)
- ✅ Director-Agent Contract: Developer reviews and approves each exercise before proceeding
- ✅ Documentation-Concurrent: discovery-log.md updated after each exercise
- ✅ Fail-Safe by Default: All tools return human-readable error messages
- ✅ Data Integrity Rules: Email is primary identifier, phone secondary
- ✅ Guardrail Constraints: Pricing, refunds, legal all trigger escalation

## Project Structure

### Documentation (this feature)

```text
specs/phase1-incubation/
├── plan.md                 # This file
├── research.md             # Phase 0 output (technology research)
├── data-model.md           # Phase 1 output (entity definitions)
├── quickstart.md           # Phase 1 output (setup guide)
├── contracts/              # Phase 1 output (API contracts)
│   └── mcp-tools.md        # MCP tool definitions
└── tasks.md                # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
project-root/
├── context/
│   ├── company-profile.md
│   ├── product-docs.md
│   ├── sample-tickets.json
│   ├── escalation-rules.md
│   └── brand-voice.md
├── src/
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── email_simulator.py
│   │   ├── whatsapp_simulator.py
│   │   └── webform_simulator.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── normalizer.py
│   │   ├── knowledge_base.py
│   │   ├── memory.py
│   │   ├── sentiment.py
│   │   ├── escalation.py
│   │   ├── formatter.py
│   │   └── core_loop.py
│   ├── mcp_server.py
│   └── skills_manifest.py
├── tests/
│   ├── test_channels.py
│   ├── test_knowledge_base.py
│   ├── test_memory.py
│   ├── test_escalation.py
│   ├── test_formatter.py
│   └── test_mcp_tools.py
├── specs/
│   ├── discovery-log.md
│   ├── customer-success-fte-spec.md
│   └── transition-checklist.md
├── requirements.txt
└── README.md
```

## Phase 0: Research & Technology Selection

### Research Tasks

1. **MCP Server Framework**
   - Research MCP protocol specification
   - Identify Python MCP server libraries
   - Document tool definition patterns

2. **Anthropic Claude API**
   - Research Claude API integration patterns
   - Document async client usage
   - Identify rate limits and best practices

3. **Sentiment Analysis (Phase 1)**
   - Research simple keyword-based sentiment scoring
   - Evaluate TextBlob for basic sentiment
   - Document threshold strategies

4. **Channel Simulation Patterns**
   - Research message simulator patterns
   - Document dataclass-based message models
   - Identify testing strategies for simulated channels

5. **In-Memory State Management**
   - Research Python dictionary-based state management
   - Document session-scoped storage patterns
   - Identify cleanup/garbage collection strategies

## Phase 1: Design & Contracts

### Data Model (data-model.md)

**Entities:**

1. **ChannelMessage**
   - Fields: channel, content, customer_email, customer_phone, customer_name, subject, thread_id, channel_message_id, received_at, metadata
   - Validation: email format, phone format, channel enum
   - Relationships: linked to Customer via customer_id

2. **CustomerMemory**
   - Fields: customer_id, name, email, phone, turns (list), topics, sentiment_trend, status, escalated
   - Validation: customer_id required, at least one contact method
   - Relationships: contains multiple ConversationTurns

3. **ConversationTurn**
   - Fields: role, content, channel, timestamp, sentiment_score, tool_calls
   - Validation: role enum, content non-empty
   - Relationships: belongs to CustomerMemory

4. **Ticket**
   - Fields: ticket_id, customer_id, source_channel, category, priority, status, created_at, issue
   - Validation: channel enum, priority enum, status enum
   - Relationships: linked to Customer

5. **Escalation**
   - Fields: escalation_id, ticket_id, reason, context, escalated_at, human_agent
   - Validation: reason enum, ticket_id required
   - Relationships: linked to Ticket

### API Contracts (contracts/mcp-tools.md)

**MCP Tool Definitions:**

1. **search_knowledge_base**
   - Input: query (str), max_results (int, default 5), category (str, optional)
   - Output: str (formatted doc snippets)
   - Errors: KB unavailable, no results found

2. **create_ticket**
   - Input: customer_id (str), issue (str), priority (str), channel (str)
   - Output: str (ticket_id)
   - Errors: Invalid customer_id, missing required fields

3. **get_customer_history**
   - Input: customer_id (str), limit (int, default 10)
   - Output: str (formatted history)
   - Errors: Customer not found

4. **escalate_to_human**
   - Input: ticket_id (str), reason (str), context (str), urgency (str)
   - Output: str (escalation_id)
   - Errors: Invalid ticket_id, missing reason

5. **send_response**
   - Input: ticket_id (str), message (str), channel (str), customer_email (str, optional), customer_phone (str, optional)
   - Output: str (delivery_status)
   - Errors: Invalid channel, delivery failure

6. **analyze_sentiment**
   - Input: message (str)
   - Output: dict (score: float, label: str)
   - Errors: Empty message, analysis failure

### Quick Start Guide (quickstart.md)

**Setup Steps:**

1. Create Python 3.11+ virtual environment
2. Install dependencies from requirements.txt
3. Create context/ directory with 5 required files
4. Run Exercise 1.0 setup verification
5. Start Claude Code integration
6. Begin Exercise 1.1 exploration

**Dependencies:**

```txt
mcp>=0.1.0
anthropic>=0.10.0
pydantic>=2.0
python-dotenv>=1.0
pytest>=7.0
pytest-asyncio>=0.21
textblob>=0.17
```

## Phase 2: Implementation Strategy

### Exercise Execution Order

| Exercise | Duration | Goal | Gate |
|----------|----------|------|------|
| 1.0 Setup | 30 min | Dossier + environment | All 5 context files exist |
| 1.1 Exploration | 2-3 hrs | Claude Code explores | discovery-log.md ≥5 entries |
| 1.2 Core Loop | 4-5 hrs | Prototype interaction | 3 channel scenarios passing |
| 1.3 Memory | 3-4 hrs | Add state tracking | Follow-up scenario working |
| 1.4 MCP Server | 3-4 hrs | Build MCP server | All 5+ tools callable |
| 1.5 Skills | 2-3 hrs | Formalize skills | Skills manifest created |
| Exit | 1 hr | Crystallize spec | All deliverables done |

### Component Implementation Order

1. **src/channels/base.py** - Channel message dataclass
2. **src/agent/memory.py** - In-memory conversation store
3. **src/agent/knowledge_base.py** - Flat-file KB search
4. **src/agent/sentiment.py** - Keyword-based sentiment
5. **src/agent/escalation.py** - Escalation logic
6. **src/agent/formatter.py** - Channel formatter
7. **src/agent/core_loop.py** - Main interaction loop
8. **src/mcp_server.py** - MCP tool exposure
9. **tests/** - Test suite for all components

## Key Design Decisions (ADR Summary)

| Decision | Choice | Reason |
|----------|--------|--------|
| Phase 1 storage | In-memory dict | Speed of iteration; PostgreSQL in Phase 2 |
| Phase 1 search | Keyword overlap | No DB needed; replaced by pgvector in Phase 2 |
| MCP vs direct tools | MCP | Validates tool contract before SDK migration |
| Sentiment | Keyword scoring | No model dependency in prototype phase |
| Channel detection | Message metadata field | Simulated in Phase 1; webhook-driven in Phase 2 |
| Customer ID | Email → phone → uuid | Matches Phase 2 PostgreSQL schema |

## Constitution Check (Post-Design)

*Re-evaluate after design complete:*

- ✅ All components are channel-aware
- ✅ Fail-safe defaults in all error handlers
- ✅ Email as primary identifier enforced
- ✅ Guardrails documented in escalation logic
- ✅ Documentation concurrent with implementation
- ✅ Director-Agent contract maintained

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude API rate limits | High | Implement retry logic, cache responses |
| In-memory state loss | Medium | Accept for Phase 1; document limitation |
| Keyword sentiment accuracy | Medium | Use conservative thresholds, escalate on uncertainty |
| Channel simulation complexity | Low | Use dataclass-based simulators for consistency |
| MCP protocol complexity | Medium | Start with minimal tool set, expand iteratively |

## Success Criteria Validation

**Quantitative:**
- [ ] 100% channel detection on test set
- [ ] >85% KB answer accuracy on 20 queries
- [ ] >95% escalation trigger accuracy on 10 scenarios
- [ ] >80% sentiment analysis accuracy
- [ ] 100% response length compliance
- [ ] 10+ edge cases documented
- [ ] All 5+ MCP tools callable

**Qualitative:**
- [ ] Responses feel natural per channel
- [ ] Escalations handled clearly
- [ ] Context awareness demonstrated
- [ ] Errors degrade gracefully
- [ ] Tone appropriate per channel

---

**Next Step**: Create tasks breakdown with `/sp.tasks` command
