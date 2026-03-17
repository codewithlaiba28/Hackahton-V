<!-- 
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0 (Initial constitution)
Added sections:
  - Project Identity
  - 7 Immutable Principles
  - Technology Constraints (Phase 1)
  - Quality Standards (Code, Testing, Documentation)
  - Phase Gate Requirements
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (pending verification)
  - ✅ .specify/templates/spec-template.md (pending verification)
  - ✅ .specify/templates/tasks-template.md (pending verification)
Follow-up TODOs:
  - TODO(CONSTITUTION_VERSION): Increment per semantic versioning as principles evolve
  - TODO(RATIFICATION_DATE): Confirm official project start date
-->

# Customer Success FTE Constitution

## Core Principles

### I. Specification-First Law
Every feature starts with a specification entry in `specs/` before any code is written. No exceptions.

**Non-negotiable rules:**
- Every feature, tool, and workflow MUST be described in `specs/` before implementation
- The spec is the source of truth; code is the last-mile artifact
- "I'll document it later" is a constitution violation
- Discovery logs are written concurrently with code

**Rationale**: Prevents scope creep, ensures intentional design, creates audit trail for decisions.

### II. Channel-Awareness Mandate
Every function, response, and workflow is channel-aware. Three channels exist: `email`, `whatsapp`, `web_form`.

**Non-negotiable rules:**
- No code may ignore the channel context
- Response formatting, length, and tone MUST differ by channel
- Channel metadata MUST be tracked in all customer interactions
- Cross-channel continuity MUST be maintained (customers can switch channels mid-conversation)

**Channel specifications:**
| Channel | Style | Max Length | Identifier |
|---------|-------|------------|------------|
| Email | Formal, detailed | 500 words | Email address |
| WhatsApp | Conversational, concise | 300 chars | Phone number |
| Web Form | Semi-formal | 300 words | Email address |

**Rationale**: Customers expect channel-appropriate communication; one-size-fits-all fails.

### III. Director-Agent Contract
The developer (human) acts as **Director**: provides intent, reviews output, approves phases. Claude Code acts as **Agent**: explores, prototypes, discovers requirements, generates code.

**Non-negotiable rules:**
- The agent does NOT proceed to the next phase without explicit human approval
- The Director provides strategic intent; the Agent executes tactically
- All phase gates require explicit Director sign-off
- The Agent asks clarifying questions when intent is ambiguous

**Rationale**: Human oversight prevents costly mistakes; AI speed accelerates discovery.

### IV. Documentation-Concurrent Principle
Discovery logs, edge case records, and spec documents are written at the same time as code.

**Non-negotiable rules:**
- `specs/discovery-log.md` updated after every exercise
- Edge cases documented immediately upon discovery
- `specs/customer-success-fte-spec.md` finalized at end of Phase 1
- `specs/transition-checklist.md` completed before Phase 2 begins

**Rationale**: Retrospective documentation is always incomplete; real-time capture preserves context.

### V. Fail-Safe by Default
Every tool and agent response must degrade gracefully. No exception may propagate to the end user without a human-readable fallback.

**Non-negotiable rules:**
- All exceptions MUST be caught and handled with user-friendly messages
- Escalation is always preferable to a bad AI response
- Fallback responses MUST be helpful, not alarming
- Error logs capture full stack traces for debugging

**Rationale**: Customer trust is fragile; graceful failures preserve confidence.

### VI. Data Integrity Rules
Customer email is the primary cross-channel identifier. Phone number is secondary (WhatsApp only).

**Non-negotiable rules:**
- A customer record MUST be created or resolved before any ticket is opened
- Email address is the primary key for customer identification
- Phone number used for WhatsApp-only customers
- Cross-channel matching MUST merge customer histories

**Rationale**: Consistent customer identification enables personalized support across channels.

### VII. Guardrail Constraints (Hard — Never Violate)
| Constraint | Rule | Escalation Reason Code |
|------------|------|------------------------|
| **Pricing** | NEVER answer pricing questions | `pricing_inquiry` |
| **Refunds** | NEVER process refunds | `refund_request` |
| **Competitor products** | NEVER discuss or compare | `competitor_inquiry` |
| **Legal threats** | NEVER engage; flag immediately | `legal_threat` |
| **Feature promises** | NEVER promise undocumented features | `feature_request` |
| **Response without ticket** | NEVER respond without creating ticket first | `protocol_violation` |

**Rationale**: These constraints protect the business from liability, over-promising, and compliance risks.

## Technology Constraints (Phase 1)

| Layer | Technology | Notes |
|-------|------------|-------|
| **Language** | Python 3.11+ | Async-first (asyncio) |
| **Agent Framework** | MCP Server | Phase 1 prototype; transitions to OpenAI Agents SDK in Phase 2 |
| **Storage** | In-memory / local JSON | Transitions to PostgreSQL in Phase 2 |
| **Knowledge Base** | Flat file search | Transitions to pgvector in Phase 2 |
| **LLM** | Claude via Anthropic API | Configured through Claude Code |
| **Package Manager** | uv preferred; pip acceptable | Consistent dependency management |

**Phase 1 Duration**: Hours 1–16 of a 48–72 hour hackathon

**Rationale**: Phase 1 focuses on rapid prototyping and requirement discovery; production technologies introduced in Phase 2.

## Quality Standards

### Code Quality
- All functions MUST have type annotations
- All async functions MUST handle `asyncio.TimeoutError`
- No `print()` statements in logic code — use Python `logging`
- All tools return `str` (as required by MCP protocol)
- Functions MUST be testable in isolation

### Testing Requirements
- Every exercise produces at least 3 test cases before moving on
- Edge cases discovered during incubation MUST be documented in `specs/discovery-log.md`
- Minimum 10 edge cases must be documented before Phase 1→2 transition
- Tests MUST cover: happy path, edge cases, error handling

### Documentation Requirements
| Document | When | Owner |
|----------|------|-------|
| `specs/discovery-log.md` | After every exercise | Agent |
| `specs/customer-success-fte-spec.md` | End of Phase 1 | Agent + Director |
| `specs/transition-checklist.md` | Before Phase 2 | Agent |
| `specs/edge-cases.md` | Concurrent with discovery | Agent |

## Phase Gate: Constitution → Specification

Before proceeding to `/sp.specify`, confirm ALL of the following:

- [x] This constitution has been reviewed and accepted by the developer
- [ ] The `/context/` dossier folder exists with all 5 required files:
  - `company-profile.md`
  - `product-docs.md`
  - `sample-tickets.json` (50+ multi-channel samples)
  - `escalation-rules.md`
  - `brand-voice.md`
- [ ] The development environment is set up (Python, venv, dependencies)
- [ ] Claude Code is configured and accessible
- [ ] `specs/` directory created
- [ ] `specs/discovery-log.md` initialized

**If any box is unchecked, do NOT proceed. Address the gap first.**

## Governance

This constitution supersedes all other practices and guidelines for the Customer Success FTE project.

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

**Version**: 1.0.0 | **Ratified**: 2026-03-17 | **Last Amended**: 2026-03-17
