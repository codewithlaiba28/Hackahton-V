# Feature Specification: Phase 1 Incubation

**Feature Branch**: `phase1-incubation`
**Created**: 2026-03-17
**Status**: Draft
**Input**: Customer Success FTE Phase 1 - Incubation Phase using Claude Code as Agent Factory

## User Scenarios & Testing

### User Story 1 - Product Question via Web Form (Priority: P1)

A customer submits a product question ("How do I reset my API key?") through the web support form. The FTE searches the product documentation, finds the relevant answer, and replies in a semi-formal tone. A ticket is created before the response is sent.

**Why this priority**: This is the core value proposition - answering customer questions automatically. Without this, there is no product.

**Independent Test**: Can be fully tested by submitting a web form with a known product question and verifying the response is accurate and a ticket is created.

**Acceptance Scenarios**:

1. **Given** a customer submits a question via web form, **When** the FTE processes it, **Then** a ticket is created with source_channel = web_form before any response is sent
2. **Given** a question about API key reset, **When** the knowledge base is searched, **Then** relevant documentation is retrieved
3. **Given** a valid product question, **When** the response is generated, **Then** it is under 300 words and semi-formal in tone
4. **Given** a response is generated, **When** sent to customer, **Then** sentiment score is assessed and stored with the ticket

---

### User Story 2 - Casual WhatsApp Inquiry (Priority: P1)

A customer sends a casual message ("hey can i export my data?") via WhatsApp. The FTE detects the conversational tone, searches documentation, and replies in under 160 characters with a conversational tone.

**Why this priority**: WhatsApp is a primary channel; concise responses are critical for chat-based support.

**Independent Test**: Can be tested by sending WhatsApp messages and verifying response length and tone.

**Acceptance Scenarios**:

1. **Given** a WhatsApp message, **When** processed, **Then** channel is detected as whatsapp
2. **Given** a casual inquiry, **When** response generated, **Then** it is under 300 characters (preferably 160)
3. **Given** a WhatsApp conversation, **When** response sent, **Then** tone is conversational, not formal
4. **Given** any WhatsApp interaction, **When** ticket created, **Then** source_channel = whatsapp

---

### User Story 3 - Detailed Email Inquiry (Priority: P2)

A customer emails asking for a detailed walkthrough of API authentication. The FTE responds with a formal, structured reply including greeting and signature, up to 500 words.

**Why this priority**: Email support requires more detailed responses; customers expect formal communication via email.

**Independent Test**: Can be tested by sending email inquiries and verifying response includes greeting, signature, and appropriate detail level.

**Acceptance Scenarios**:

1. **Given** an email inquiry, **When** processed, **Then** channel is detected as email
2. **Given** an email response, **When** generated, **Then** it includes greeting ("Dear [Name]") and signature
3. **Given** a detailed question, **When** response generated, **Then** it is detailed (up to 500 words)
4. **Given** an email interaction, **When** ticket created, **Then** source_channel = email

---

### User Story 4 - Pricing Inquiry Escalation (Priority: P1)

A customer asks "What's the price of the Enterprise plan?" The FTE does NOT answer; it creates a ticket and escalates immediately to human support.

**Why this priority**: Pricing inquiries must NEVER be answered by AI; this is a critical business guardrail.

**Independent Test**: Can be tested by asking pricing questions and verifying no pricing information is revealed and escalation is triggered.

**Acceptance Scenarios**:

1. **Given** a pricing question, **When** detected, **Then** FTE does NOT reveal or estimate any pricing
2. **Given** a pricing inquiry, **When** ticket created, **Then** category = pricing_inquiry
3. **Given** a pricing inquiry, **When** evaluated, **Then** escalation is triggered with reason pricing_inquiry
4. **Given** an escalation, **When** customer notified, **Then** they are told a human will follow up

---

### User Story 5 - Angry Customer Escalation (Priority: P1)

A customer says "This is BROKEN and your support is USELESS." Sentiment is detected as below 0.3. The FTE responds empathetically and escalates.

**Why this priority**: Negative sentiment must trigger escalation to prevent customer churn and reputation damage.

**Independent Test**: Can be tested by sending messages with negative language and verifying sentiment score and escalation.

**Acceptance Scenarios**:

1. **Given** a negative message, **When** analyzed, **Then** sentiment score is computed and stored (< 0.3 triggers escalation)
2. **Given** an angry customer, **When** FTE responds, **Then** it responds with empathy before or alongside escalation notice
3. **Given** negative sentiment detected, **When** escalation triggered, **Then** reason = negative_sentiment

---

### User Story 6 - Follow-Up on Same Topic (Priority: P2)

A customer who asked about API keys earlier now asks "what about OAuth?" The FTE understands this is a continuation and maintains context.

**Why this priority**: Conversation continuity is essential for good customer experience; customers expect the agent to remember context.

**Independent Test**: Can be tested by having multi-turn conversations and verifying the FTE references prior context.

**Acceptance Scenarios**:

1. **Given** a returning customer, **When** they send a follow-up, **Then** conversation history is retrieved
2. **Given** a follow-up question, **When** response generated, **Then** FTE references prior context
3. **Given** a conversation session, **When** follow-up received, **Then** no duplicate ticket is created
4. **Given** cross-channel history, **When** customer identified, **Then** history lookup works across channels

---

### User Story 7 - Human Escalation Request (Priority: P1)

A WhatsApp customer types "I want to speak to a human agent." The FTE escalates immediately without further AI responses.

**Why this priority**: When customers explicitly request humans, the AI must comply immediately to avoid frustration.

**Independent Test**: Can be tested by sending messages with escalation keywords and verifying immediate escalation.

**Acceptance Scenarios**:

1. **Given** a message with "human", "agent", "representative", or "person", **When** detected, **Then** escalation is triggered immediately
2. **Given** an escalation request, **When** acknowledged, **Then** customer is notified via same channel
3. **Given** a human request, **When** detected, **Then** no further AI-generated responses are sent

---

### Edge Cases

- What happens when a customer submits an empty message?
- How does the system handle messages with multiple intents (e.g., "I need help with billing AND technical issue")?
- What happens when knowledge base search returns no results?
- How does the system handle non-English messages?
- What happens when the same customer contacts via multiple channels simultaneously?
- How are attachments (images, files) in messages handled?
- What happens when sentiment is exactly 0.3 (boundary condition)?
- How does the system handle very long messages (>1000 words)?
- What happens when a customer uses profanity but isn't angry (e.g., casual usage)?
- How are links and formatted text in messages handled?

## Requirements

### Functional Requirements

- **FR-001**: System MUST accept customer messages from three channels: email, whatsapp, and web_form
- **FR-002**: System MUST create a ticket before responding to any customer message
- **FR-003**: System MUST search knowledge base for relevant information before generating responses
- **FR-004**: System MUST generate channel-appropriate responses (tone, length, format)
- **FR-005**: System MUST compute sentiment score for every incoming customer message
- **FR-006**: System MUST escalate immediately when pricing questions are detected
- **FR-007**: System MUST escalate when sentiment score is below 0.3
- **FR-008**: System MUST escalate when customer explicitly requests human support
- **FR-009**: System MUST maintain conversation history per customer within a session
- **FR-010**: System MUST identify customers across channels using email as primary identifier
- **FR-011**: System MUST expose all capabilities as MCP tools for Claude Code invocation
- **FR-012**: System MUST track channel metadata in all customer interactions
- **FR-013**: System MUST NEVER discuss pricing, process refunds, or promise undocumented features
- **FR-014**: System MUST degrade gracefully with human-readable fallback messages on errors

### Key Entities

- **Customer**: Person submitting support requests; identified by email (primary) or phone (WhatsApp)
- **Ticket**: Record of a customer interaction; includes channel, issue, priority, status
- **Conversation**: Thread of messages between customer and FTE; may span multiple sessions
- **Message**: Individual communication unit; has direction (inbound/outbound), content, channel
- **Knowledge Base**: Product documentation used to answer questions
- **Escalation**: Handoff to human support with reason code and context

## Success Criteria

### Quantitative Metrics

1. **Channel Detection Accuracy**: 100% correct channel identification on test set
2. **Knowledge Base Accuracy**: >85% correct answers on 20 test queries
3. **Escalation Trigger Accuracy**: >95% accuracy on 10 escalation scenarios
4. **Sentiment Analysis Accuracy**: >80% accuracy on labeled test set
5. **Response Length Compliance**: 100% of responses within channel limits
6. **Edge Cases Documented**: Minimum 10 edge cases documented before Phase 2
7. **MCP Tools Working**: All 5+ tools callable without error

### Qualitative Measures

1. **Customer Experience**: Responses feel natural and appropriate for each channel
2. **Escalation Handling**: Customers are notified clearly when escalated
3. **Context Awareness**: FTE demonstrates understanding of conversation history
4. **Error Handling**: Graceful degradation with helpful messages on failures
5. **Tone Appropriateness**: Formal for email, conversational for WhatsApp, balanced for web

## Assumptions

1. Knowledge base is provided as a flat file (product-docs.md) during Phase 1
2. Email address is available for all customers (primary identifier)
3. Phone number is available for WhatsApp customers
4. Session-scoped memory is sufficient for Phase 1 (persistence not required)
5. Keyword-based search is acceptable for Phase 1 (vector search in Phase 2)
6. Simulated channel integrations are acceptable for Phase 1 testing
7. Claude Code is available and configured for the Developer (Director)

## Out of Scope (Phase 1)

- Real Gmail webhook integration (simulated in Phase 1)
- Real WhatsApp/Twilio integration (simulated in Phase 1)
- PostgreSQL persistence (in-memory in Phase 1)
- Kubernetes deployment (Phase 2 only)
- Kafka event streaming (Phase 2 only)
- Vector similarity search with pgvector (Phase 2 only)
- Daily report generation (Phase 2 only)
- Cross-session conversation persistence (Phase 2 only)

## Dependencies

1. **Claude Code**: Must be configured and accessible for the Developer
2. **Product Documentation**: Must be provided in /context/product-docs.md
3. **Sample Tickets**: Test data must be provided in /context/sample-tickets.json
4. **Escalation Rules**: Must be defined in /context/escalation-rules.md
5. **Brand Voice**: Must be defined in /context/brand-voice.md
6. **Company Profile**: Must be provided in /context/company-profile.md

## Constraints

- **Duration**: Hours 1-16 of a 48-72 hour hackathon
- **Language**: Python 3.11+ with async-first approach
- **Agent Framework**: MCP Server (transitions to OpenAI Agents SDK in Phase 2)
- **Storage**: In-memory / local JSON (transitions to PostgreSQL in Phase 2)
- **LLM**: Claude via Anthropic API (configured through Claude Code)
- **Response Time**: <3 seconds processing, <30 seconds delivery (target)
