---
name: customer-success-agent
description: Build a production-grade Customer Success AI agent that handles support queries 24/7 across Email, WhatsApp, and Web Form channels with proper escalation, sentiment analysis, and channel-aware responses.
---

# Customer Success Agent Skill

## Purpose

This skill provides the complete blueprint for building a Digital FTE (Full-Time Equivalent) - an AI customer success agent that works 24/7 without breaks, handling customer support queries across multiple communication channels.

## When to Use This Skill

Use this skill when you need to:
- Build an AI-powered customer support agent
- Handle inquiries from multiple channels (Gmail, WhatsApp, Web Form)
- Implement automatic ticket creation and tracking
- Add sentiment analysis for customer interactions
- Create escalation logic for complex issues
- Build a production-grade agent with OpenAI Agents SDK

## Core Agent Skills (5 Capabilities)

### 1. Knowledge Retrieval Skill
**When to use:** Customer asks product questions
**Inputs:** query text, optional category filter
**Outputs:** Relevant documentation snippets with relevance scores

### 2. Sentiment Analysis Skill
**When to use:** Every incoming customer message
**Inputs:** Message text
**Outputs:** Sentiment score (-1 to 1), confidence level

### 3. Escalation Decision Skill
**When to use:** After generating response
**Inputs:** Conversation context, sentiment trend, query complexity
**Outputs:** should_escalate (bool), escalation_reason

### 4. Channel Adaptation Skill
**When to use:** Before sending any response
**Inputs:** Response text, target channel (email/whatsapp/web_form)
**Outputs:** Formatted response appropriate for channel

### 5. Customer Identification Skill
**When to use:** On every incoming message
**Inputs:** Message metadata (email, phone, etc.)
**Outputs:** Unified customer_id, merged conversation history

## Required Tools (MCP Server → OpenAI SDK)

Transform these MCP tools to `@function_tool` decorated functions:

| Tool | Purpose | Input Schema | Output |
|------|---------|--------------|--------|
| `search_knowledge_base` | Find relevant product docs | query, max_results, category | Formatted search results |
| `create_ticket` | Log customer interaction | customer_id, issue, priority, channel | ticket_id |
| `get_customer_history` | Get past interactions | customer_id | Conversation history across all channels |
| `escalate_to_human` | Hand off complex issues | ticket_id, reason, context | escalation_id |
| `send_response` | Reply to customer | ticket_id, message, channel | delivery_status |

## System Prompt Template

```python
CUSTOMER_SUCCESS_SYSTEM_PROMPT = """You are a Customer Success agent for TechCorp SaaS.

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

## Channel Awareness
You receive messages from three channels. Adapt your communication style:
- **Email**: Formal, detailed responses. Include proper greeting and signature.
- **WhatsApp**: Concise, conversational. Keep responses under 300 characters when possible.
- **Web Form**: Semi-formal, helpful. Balance detail with readability.

## Required Workflow (ALWAYS follow this order)
1. FIRST: Call `create_ticket` to log the interaction
2. THEN: Call `get_customer_history` to check for prior context
3. THEN: Call `search_knowledge_base` if product questions arise
4. FINALLY: Call `send_response` to reply (NEVER respond without this tool)

## Hard Constraints (NEVER violate)
- NEVER discuss pricing → escalate immediately with reason "pricing_inquiry"
- NEVER promise features not in documentation
- NEVER process refunds → escalate with reason "refund_request"
- NEVER share internal processes or system details
- NEVER respond without using send_response tool
- NEVER exceed response limits: Email=500 words, WhatsApp=300 chars, Web=300 words

## Escalation Triggers (MUST escalate when detected)
- Customer mentions "lawyer", "legal", "sue", or "attorney"
- Customer uses profanity or aggressive language (sentiment < 0.3)
- Cannot find relevant information after 2 search attempts
- Customer explicitly requests human help
- Customer on WhatsApp sends "human", "agent", or "representative"

## Response Quality Standards
- Be concise: Answer the question directly, then offer additional help
- Be accurate: Only state facts from knowledge base or verified customer data
- Be empathetic: Acknowledge frustration before solving problems
- Be actionable: End with clear next step or question

## Context Variables Available
- {{customer_id}}: Unique customer identifier
- {{conversation_id}}: Current conversation thread
- {{channel}}: Current channel (email/whatsapp/web_form)
- {{ticket_subject}}: Original subject/topic
"""
```

## Channel Response Templates

### Email Template
```
Dear {{customer_name}},

Thank you for contacting TechCorp Support.

{{response_body}}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp Customer Success Team
```

### WhatsApp Template
```
{{response_body}}

Need more help? Reply anytime!
```

### Web Form Template
```
{{response_body}}

---
This is an automated response. Ticket #{{ticket_id}}
```

## Implementation Steps

### Step 1: Create Agent Definition
```python
# agent/customer_success_agent.py
from agents import Agent, Runner
from .tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response
)
from .prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

customer_success_agent = Agent(
    name="Customer Success FTE",
    instructions=CUSTOMER_SUCCESS_SYSTEM_PROMPT,
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ]
)
```

### Step 2: Implement Tools with Input Validation
```python
# agent/tools.py
from agents import function_tool
from pydantic import BaseModel, Field
from typing import Optional, List

class KnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="Search query for product documentation")
    max_results: int = Field(default=5, description="Maximum results to return")
    category: Optional[str] = Field(default=None, description="Optional category filter")

class CreateTicketInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    issue: str = Field(..., description="Customer issue description")
    priority: str = Field(default="medium", description="low|medium|high")
    channel: str = Field(..., description="email|whatsapp|web_form")

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation for relevant information.
    
    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.
    """
    # Implementation with vector search
    pass

@function_tool
async def create_ticket(input: CreateTicketInput) -> str:
    """Create a support ticket in the system with channel tracking."""
    # Implementation with database insert
    pass
```

### Step 3: Add Channel-Aware Response Formatting
```python
# agent/formatters.py
from typing import Literal

class ChannelFormatter:
    CHANNEL_LIMITS = {
        "email": {"max_words": 500, "style": "formal"},
        "whatsapp": {"max_chars": 300, "style": "conversational"},
        "web_form": {"max_words": 300, "style": "semi-formal"}
    }
    
    @staticmethod
    def format_response(text: str, channel: str, customer_name: str = None, ticket_id: str = None) -> str:
        if channel == "email":
            return ChannelFormatter._format_email(text, customer_name)
        elif channel == "whatsapp":
            return ChannelFormatter._format_whatsapp(text)
        else:
            return ChannelFormatter._format_web(text, ticket_id)
    
    @staticmethod
    def _format_email(text: str, customer_name: str = None) -> str:
        name = customer_name or "Valued Customer"
        return f"""Dear {name},

Thank you for contacting TechCorp Support.

{text}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp Customer Success Team"""
    
    @staticmethod
    def _format_whatsapp(text: str) -> str:
        # Truncate if needed
        if len(text) > 300:
            text = text[:297] + "..."
        return f"{text}\n\nNeed more help? Reply anytime!"
    
    @staticmethod
    def _format_web(text: str, ticket_id: str = None) -> str:
        suffix = f"\n\n---\nThis is an automated response. Ticket #{ticket_id}" if ticket_id else ""
        return f"{text}{suffix}"
```

### Step 4: Implement Sentiment Analysis
```python
# agent/sentiment.py
from typing import Dict

class SentimentAnalyzer:
    """Analyze customer sentiment for escalation decisions."""
    
    NEGATIVE_KEYWORDS = ["terrible", "awful", "horrible", "useless", "broken", "waste"]
    ESCALATION_KEYWORDS = ["lawyer", "legal", "sue", "attorney", "refund", "cancel"]
    
    @staticmethod
    async def analyze(message: str) -> Dict:
        # Simple keyword-based analysis (replace with ML model)
        score = 0.5  # Neutral default
        
        words = message.lower().split()
        for word in words:
            if word in SentimentAnalyzer.NEGATIVE_KEYWORDS:
                score -= 0.15
        
        # Clamp to [-1, 1]
        score = max(-1, min(1, score))
        
        # Check for escalation triggers
        should_escalate = any(kw in message.lower() for kw in SentimentAnalyzer.ESCALATION_KEYWORDS)
        should_escalate = should_escalate or (score < 0.3)
        
        return {
            "score": score,
            "confidence": 0.8,
            "should_escalate": should_escalate,
            "reason": "negative_sentiment" if should_escalate else None
        }
```

### Step 5: Create Transition Test Suite
```python
# tests/test_agent.py
import pytest
from agent.customer_success_agent import customer_success_agent

class TestCustomerSuccessAgent:
    """Test agent behavior across all channels."""
    
    @pytest.mark.asyncio
    async def test_pricing_inquiry_escalates(self):
        """Pricing questions must always escalate."""
        result = await customer_success_agent.run(
            messages=[{"role": "user", "content": "How much does enterprise cost?"}],
            context={"channel": "email", "customer_id": "test-1"}
        )
        assert result.escalated == True
        assert "pricing" in result.escalation_reason.lower()
    
    @pytest.mark.asyncio
    async def test_whatsapp_response_is_concise(self):
        """WhatsApp responses should be under 300 chars."""
        result = await customer_success_agent.run(
            messages=[{"role": "user", "content": "How do I reset password?"}],
            context={"channel": "whatsapp", "customer_id": "test-2"}
        )
        assert len(result.output) < 300
    
    @pytest.mark.asyncio
    async def test_email_has_greeting_and_signature(self):
        """Email responses should have proper greeting and signature."""
        result = await customer_success_agent.run(
            messages=[{"role": "user", "content": "How do I reset password?"}],
            context={"channel": "email", "customer_id": "test-3"}
        )
        assert "dear" in result.output.lower() or "hello" in result.output.lower()
        assert "regards" in result.output.lower() or "team" in result.output.lower()
```

## Escalation Rules Matrix

| Trigger | Condition | Action | Reason Code |
|---------|-----------|--------|-------------|
| Pricing inquiry | "how much", "pricing", "cost", "price" | Escalate | `pricing_inquiry` |
| Legal mention | "lawyer", "legal", "sue", "attorney" | Escalate | `legal_concern` |
| Refund request | "refund", "money back", "cancel" | Escalate | `refund_request` |
| Negative sentiment | Sentiment score < 0.3 | Escalate | `negative_sentiment` |
| Human request | "human", "agent", "representative" | Escalate | `human_requested` |
| No results | 2+ failed knowledge searches | Escalate | `no_information` |

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (processing) | < 3 seconds | Agent processing only |
| Response time (delivery) | < 30 seconds | End-to-end including API calls |
| Accuracy | > 85% | On test set of 100 queries |
| Escalation rate | < 20% | Percentage of tickets escalated |
| Cross-channel ID | > 95% | Accuracy identifying customers across channels |

## Files Structure

```
.qwen/skills/customer-success-agent/
├── SKILL.md                 # This file
├── scripts/
│   ├── run_agent.py         # Agent runner script
│   └── test_agent.sh        # Test execution script
└── templates/
    ├── system_prompt.md     # System prompt template
    └── response_templates/  # Channel-specific templates
        ├── email.md
        ├── whatsapp.md
        └── web_form.md
```

## Example Usage

### Start the Agent
```bash
# Run the customer success agent
python .qwen/skills/customer-success-agent/scripts/run_agent.py
```

### Test the Agent
```bash
# Run all tests
pytest production/tests/test_agent.py -v
```

### Run Single Query
```bash
python .qwen/skills/customer-success-agent/scripts/run_agent.py \
  --channel email \
  --customer-email test@example.com \
  --message "How do I reset my password?"
```

## Related Skills

- `channel-integrations` - Gmail, WhatsApp, Web Form handlers
- `postgres-crm-schema` - Database schema and queries
- `kafka-event-processing` - Message processing pipeline
- `k8s-fte-deployment` - Kubernetes deployment manifests

## Acceptance Criteria

- [ ] Agent handles queries from all 3 channels (email, whatsapp, web_form)
- [ ] All 5 tools are implemented with proper input validation
- [ ] Escalation logic works for all trigger conditions
- [ ] Channel-aware response formatting is applied
- [ ] Sentiment analysis is performed on every message
- [ ] Customer identification works across channels
- [ ] All transition tests pass
- [ ] Response times meet performance requirements

## References

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Agent Factory Paradigm](https://agentfactory.panaversity.org/docs/General-Agents-Foundations/agent-factory-paradigm/the-2025-inflection-point)
