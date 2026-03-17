---
name: openai-agents-sdk
description: Build production-grade AI agents using OpenAI Agents SDK with @function_tool decorators, Pydantic input validation, strict tool schemas, and agent orchestration patterns.
---

# OpenAI Agents SDK Skill

## Purpose

This skill provides complete guidance for building Custom Agents using the OpenAI Agents SDK (successor to MCP-based prototypes). Learn to create production-ready agents with proper tool definitions, input validation, error handling, and agent orchestration patterns.

## When to Use This Skill

Use this skill when you need to:
- Transition from MCP server to OpenAI Agents SDK
- Create agents with strongly-typed tool definitions
- Add Pydantic input validation to agent tools
- Implement proper error handling and fallbacks
- Build multi-agent orchestration systems
- Add guardrails and constraints to agent behavior
- Deploy agents to production with monitoring

---

## Key Differences: MCP vs OpenAI Agents SDK

| Aspect | MCP (Incubation) | OpenAI Agents SDK (Production) |
|--------|------------------|-------------------------------|
| **Tool Definition** | `@server.tool()` decorator | `@function_tool` decorator |
| **Input Validation** | Dynamic parameters | Pydantic BaseModel schemas |
| **Type Safety** | Runtime type hints | Compile-time type checking |
| **Error Handling** | Basic try/catch | Structured error types |
| **Agent State** | In-memory | External database |
| **Scaling** | Single-threaded | Async workers |
| **Tool Discovery** | Manual registration | Automatic from decorators |

---

## Installation

```bash
pip install openai-agents openai pydantic pydantic-settings
```

---

## Basic Agent Definition

```python
# agent/customer_success_agent.py

from agents import Agent, Runner
from typing import Any
import asyncio

# Define the agent with instructions
customer_success_agent = Agent(
    name="Customer Success FTE",
    instructions="""You are a Customer Success agent for TechCorp SaaS.

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy.

## Required Workflow
1. FIRST: Call `create_ticket` to log the interaction
2. THEN: Call `get_customer_history` to check for prior context
3. THEN: Call `search_knowledge_base` if product questions arise
4. FINALLY: Call `send_response` to reply

## Hard Constraints
- NEVER discuss pricing → escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds → escalate
- NEVER share internal processes
- Be concise and empathetic
""",
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ],
    model="gpt-4"
)

async def main():
    # Run the agent
    result = await Runner.run(
        customer_success_agent,
        input="How do I reset my password?",
        context={
            "customer_id": "cust_123",
            "channel": "email"
        }
    )
    
    print(f"Agent response: {result.output}")
    print(f"Tool calls: {result.tool_calls}")
    print(f"Usage: {result.usage}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Tool Definitions with Pydantic Validation

```python
# agent/tools.py

from agents import function_tool
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Input Schemas (Pydantic Models)
# =============================================================================

class KnowledgeSearchInput(BaseModel):
    """Input schema for knowledge base search."""
    query: str = Field(
        ...,
        description="Search query for product documentation",
        min_length=1,
        max_length=500
    )
    max_results: int = Field(
        default=5,
        description="Maximum results to return",
        ge=1,
        le=20
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional category filter (how-to, troubleshooting, feature, faq)"
    )
    
    @validator('query')
    def validate_query_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class CreateTicketInput(BaseModel):
    """Input schema for creating support tickets."""
    customer_id: str = Field(..., description="Unique customer identifier")
    issue: str = Field(..., description="Customer issue description", min_length=10)
    priority: Literal["low", "medium", "high", "critical"] = Field(
        default="medium",
        description="Ticket priority level"
    )
    channel: Literal["email", "whatsapp", "web_form"] = Field(
        ...,
        description="Channel the customer used"
    )
    category: Optional[str] = Field(default=None, description="Issue category")

class GetCustomerHistoryInput(BaseModel):
    """Input schema for retrieving customer history."""
    customer_id: str = Field(..., description="Unique customer identifier")
    limit: int = Field(default=10, description="Number of recent interactions to return", ge=1, le=50)

class EscalateToHumanInput(BaseModel):
    """Input schema for escalating to human support."""
    ticket_id: str = Field(..., description="Ticket to escalate")
    reason: Literal[
        "pricing_inquiry",
        "legal_concern",
        "refund_request",
        "negative_sentiment",
        "human_requested",
        "no_information",
        "complex_technical"
    ] = Field(..., description="Reason for escalation")
    context: str = Field(..., description="Summary of the conversation context")
    urgency: Literal["low", "medium", "high"] = Field(default="medium", description="Escalation urgency")

class SendResponseInput(BaseModel):
    """Input schema for sending responses to customers."""
    ticket_id: str = Field(..., description="Ticket ID to respond to")
    message: str = Field(..., description="Response message", min_length=1)
    channel: Literal["email", "whatsapp", "web_form"] = Field(..., description="Channel to send via")
    customer_email: Optional[str] = Field(default=None, description="Customer email (for email channel)")
    customer_phone: Optional[str] = Field(default=None, description="Customer phone (for WhatsApp)")

# =============================================================================
# Tool Implementations
# =============================================================================

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation for relevant information.
    
    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.
    
    Args:
        input: Search parameters including query and optional filters
        
    Returns:
        Formatted search results with relevance scores
    """
    try:
        # Production: Use database with vector search
        from database.queries import DatabaseQueries
        db = DatabaseQueries.get_instance()
        
        # Generate embedding for semantic search
        from agent.embeddings import generate_embedding
        embedding = await generate_embedding(input.query)
        
        # Query with vector similarity
        results = await db.search_knowledge_base(
            query_embedding=embedding,
            max_results=input.max_results,
            category=input.category
        )
        
        if not results:
            return "No relevant documentation found. Consider escalating to human support."
        
        # Format results for the agent
        formatted = []
        for r in results:
            formatted.append(
                f"**{r['title']}** (relevance: {r['similarity']:.2f})\n"
                f"{r['content'][:500]}..."
            )
        
        return "\n\n---\n\n".join(formatted)
        
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return "Knowledge base temporarily unavailable. Please try again or escalate."

@function_tool
async def create_ticket(input: CreateTicketInput) -> str:
    """Create a support ticket in the system with channel tracking.
    
    This is the FIRST tool you should call when receiving a customer message.
    All customer interactions must be logged as tickets.
    
    Args:
        input: Ticket creation parameters
        
    Returns:
        The created ticket ID
    """
    try:
        from database.queries import DatabaseQueries
        db = DatabaseQueries.get_instance()
        
        ticket_id = await db.create_ticket(
            conversation_id=input.conversation_id,
            customer_id=input.customer_id,
            source_channel=input.channel,
            category=input.category,
            priority=input.priority
        )
        
        logger.info(f"Created ticket {ticket_id} for customer {input.customer_id}")
        return ticket_id
        
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        # Return a placeholder ID to continue flow
        return f"ticket_error_{input.customer_id}"

@function_tool
async def get_customer_history(input: GetCustomerHistoryInput) -> str:
    """Get customer's interaction history across ALL channels.
    
    Use this to understand the customer's context before responding.
    This helps provide personalized support and avoid asking for information
    the customer has already provided.
    
    Args:
        input: Customer ID and optional limit
        
    Returns:
        Formatted customer history including past tickets and conversations
    """
    try:
        from database.queries import DatabaseQueries
        db = DatabaseQueries.get_instance()
        
        history = await db.get_customer_history(input.customer_id)
        
        if not history:
            return "This is a new customer with no prior interaction history."
        
        # Format history for the agent
        formatted = [
            f"**Customer: {history.get('name', 'Unknown')}**",
            f"Email: {history.get('email', 'Unknown')}",
            f"Total conversations: {history.get('total_conversations', 0)}",
            f"Total tickets: {history.get('total_tickets', 0)}",
            f"Resolved tickets: {history.get('resolved_tickets', 0)}",
            f"Average sentiment: {history.get('avg_sentiment', 'N/A')}",
            f"Last contact: {history.get('last_contact', 'Never')}"
        ]
        
        return "\n".join(formatted)
        
    except Exception as e:
        logger.error(f"Failed to get customer history: {e}")
        return "Unable to retrieve customer history. Proceed with caution."

@function_tool
async def escalate_to_human(input: EscalateToHumanInput) -> str:
    """Escalate a ticket to human support.
    
    Use this when:
    - Customer asks about pricing or refunds
    - Customer mentions legal action
    - Customer sentiment is very negative
    - Customer explicitly requests a human
    - You cannot find relevant information after 2 search attempts
    - Issue is too complex for automated handling
    
    Args:
        input: Escalation parameters including reason and context
        
    Returns:
        Escalation ID and next steps
    """
    try:
        from database.queries import DatabaseQueries
        db = DatabaseQueries.get_instance()
        
        escalation_id = await db.create_escalation(
            ticket_id=input.ticket_id,
            conversation_id=input.conversation_id,
            reason_code=input.reason,
            reason_detail=input.context
        )
        
        # Update ticket status
        await db.update_ticket_status(input.ticket_id, "escalated")
        
        logger.info(f"Escalated ticket {input.ticket_id} with reason {input.reason}")
        
        return (
            f"Escalation created successfully.\n"
            f"Escalation ID: {escalation_id}\n"
            f"Reason: {input.reason}\n"
            f"Urgency: {input.urgency}\n"
            f"A human agent will review this within 24 hours."
        )
        
    except Exception as e:
        logger.error(f"Failed to escalate: {e}")
        return f"Escalation failed: {str(e)}. Please inform the customer a human will contact them."

@function_tool
async def send_response(input: SendResponseInput) -> str:
    """Send response to the customer via the appropriate channel.
    
    This is the FINAL tool you should call after:
    1. Creating a ticket
    2. Getting customer history
    3. Searching knowledge base
    4. Generating your response
    
    NEVER respond to a customer without calling this tool.
    
    Args:
        input: Response parameters including message and channel
        
    Returns:
        Delivery status confirmation
    """
    try:
        from channels.router import UnifiedChannelRouter
        from enum import Enum
        
        router = UnifiedChannelRouter()
        
        # Determine channel type
        channel_map = {
            "email": ChannelType.EMAIL,
            "whatsapp": ChannelType.WHATSAPP,
            "web_form": ChannelType.WEB_FORM
        }
        
        # Send via appropriate channel
        result = await router.send_response(
            channel=channel_map[input.channel],
            message=input.message,
            customer_email=input.customer_email,
            customer_phone=input.customer_phone,
            ticket_id=input.ticket_id
        )
        
        # Update ticket status
        from database.queries import DatabaseQueries
        db = DatabaseQueries.get_instance()
        await db.update_ticket_status(input.ticket_id, "waiting")
        
        logger.info(f"Response sent via {input.channel}: {result}")
        return f"Response sent successfully via {input.channel}. Status: {result.get('delivery_status')}"
        
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
        return f"Failed to send response: {str(e)}. Please try again or escalate."
```

---

## Agent with Custom Handoffs

```python
# agent/agent_with_handoffs.py

from agents import Agent, Runner, handoff
from typing import Any

# Billing specialist agent
billing_agent = Agent(
    name="Billing Specialist",
    instructions="""You are a billing specialist for TechCorp SaaS.
    
Handle billing-related inquiries:
- Invoice questions
- Payment issues
- Subscription changes
- Upgrade/downgrade requests

ESCALATE to human for:
- Refund requests
- Pricing negotiations
- Payment disputes
""",
    tools=[
        search_knowledge_base,
        get_customer_history,
        send_response
    ]
)

# Technical specialist agent
technical_agent = Agent(
    name="Technical Specialist",
    instructions="""You are a technical support specialist for TechCorp SaaS.
    
Handle technical inquiries:
- API integration questions
- Bug reports
- Feature troubleshooting
- Configuration help

ESCALATE to human for:
- Complex technical issues beyond documentation
- Enterprise customer issues
""",
    tools=[
        search_knowledge_base,
        get_customer_history,
        send_response,
        create_ticket
    ]
)

# General customer success agent with handoffs
customer_success_agent = Agent(
    name="Customer Success FTE",
    instructions="""You are the first point of contact for customer support.
    
Triage incoming requests:
- General questions → Handle yourself
- Billing questions → Transfer to billing_agent
- Technical issues → Transfer to technical_agent
- Pricing/refunds → Escalate to human
""",
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ],
    handoffs=[
        handoff(billing_agent, name="billing_specialist", description="For billing inquiries"),
        handoff(technical_agent, name="technical_specialist", description="For technical support")
    ]
)
```

---

## Agent with Response Guardrails

```python
# agent/guardrails.py

from agents import Agent, Runner
from pydantic import BaseModel

class ResponseValidation(BaseModel):
    """Validate agent responses before sending."""
    is_appropriate: bool
    contains_pricing: bool
    contains_promises: bool
    sentiment: str
    word_count: int
    channel_appropriate: bool

def validate_response(response: str, channel: str) -> ResponseValidation:
    """Validate response before sending."""
    
    # Check for pricing discussions
    pricing_keywords = ["price", "cost", "pricing", "expensive", "cheap", "discount"]
    contains_pricing = any(kw in response.lower() for kw in pricing_keywords)
    
    # Check for promises
    promise_keywords = ["will add", "we'll build", "coming soon", "next release"]
    contains_promises = any(kw in response.lower() for kw in promise_keywords)
    
    # Check word count
    word_count = len(response.split())
    max_words = {"email": 500, "whatsapp": 50, "web_form": 300}
    
    return ResponseValidation(
        is_appropriate=not contains_pricing and not contains_promises,
        contains_pricing=contains_pricing,
        contains_promises=contains_promises,
        sentiment="neutral",  # Add sentiment analysis
        word_count=word_count,
        channel_appropriate=word_count <= max_words.get(channel, 300)
    )

# Agent with guardrail checking
guarded_agent = Agent(
    name="Guarded Customer Success Agent",
    instructions="""You are a Customer Success agent with strict guardrails.
    
Before responding, ensure:
1. You are NOT discussing pricing (escalate instead)
2. You are NOT promising features not in docs
3. Your response length matches the channel
4. You are being empathetic and helpful
""",
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ]
)

async def run_with_guardrails(agent, input, context):
    """Run agent and validate response before sending."""
    
    result = await Runner.run(agent, input, context)
    
    # Validate response
    validation = validate_response(
        result.output,
        context.get("channel", "email")
    )
    
    if not validation.is_appropriate:
        # Auto-escalate if guardrails violated
        return await escalate_to_human(EscalateToHumanInput(
            ticket_id=context.get("ticket_id"),
            reason="guardrail_violation",
            context=f"Response violated guardrails: pricing={validation.contains_pricing}, promises={validation.contains_promises}"
        ))
    
    return result
```

---

## Agent Runner with Streaming

```python
# agent/streaming_runner.py

from agents import Agent, Runner
from typing import AsyncIterator

async def stream_agent_response(
    agent: Agent,
    input: str,
    context: dict = None
) -> AsyncIterator[str]:
    """Stream agent response token by token."""
    
    stream = Runner.run_streamed(
        agent,
        input=input,
        context=context
    )
    
    async for chunk in stream:
        if chunk.type == "content":
            yield chunk.content

# Usage example
async def main():
    agent = customer_success_agent
    
    async for token in stream_agent_response(
        agent,
        input="How do I integrate your API?",
        context={"customer_id": "cust_123", "channel": "email"}
    ):
        print(token, end="", flush=True)
```

---

## Testing Agent Tools

```python
# tests/test_agent_tools.py

import pytest
from pydantic import ValidationError
from agent.tools import (
    KnowledgeSearchInput,
    CreateTicketInput,
    search_knowledge_base,
    create_ticket
)

class TestInputValidation:
    """Test Pydantic input validation."""
    
    def test_knowledge_search_valid_input(self):
        """Valid input should pass validation."""
        input = KnowledgeSearchInput(
            query="How to reset password",
            max_results=5,
            category="how-to"
        )
        assert input.query == "How to reset password"
        assert input.max_results == 5
    
    def test_knowledge_search_empty_query(self):
        """Empty query should fail validation."""
        with pytest.raises(ValidationError):
            KnowledgeSearchInput(query="")
    
    def test_knowledge_search_max_results_limit(self):
        """Max results above 20 should fail."""
        with pytest.raises(ValidationError):
            KnowledgeSearchInput(query="test", max_results=25)
    
    def test_create_ticket_valid_input(self):
        """Valid ticket input should pass."""
        input = CreateTicketInput(
            customer_id="cust_123",
            issue="Cannot login to my account",
            priority="high",
            channel="email"
        )
        assert input.priority == "high"
        assert input.channel == "email"
    
    def test_create_ticket_invalid_priority(self):
        """Invalid priority should fail."""
        with pytest.raises(ValidationError):
            CreateTicketInput(
                customer_id="cust_123",
                issue="Test issue",
                priority="urgent"  # Not a valid option
            )

class TestToolExecution:
    """Test tool execution with mocked dependencies."""
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, mock_db):
        """Knowledge search should return formatted results."""
        input = KnowledgeSearchInput(query="password reset")
        result = await search_knowledge_base(input)
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_create_ticket(self, mock_db):
        """Ticket creation should return ticket ID."""
        input = CreateTicketInput(
            customer_id="cust_123",
            issue="Test issue",
            channel="email"
        )
        result = await create_ticket(input)
        
        assert result.startswith("ticket_")
```

---

## Environment Configuration

```bash
# .env

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1024
OPENAI_TEMPERATURE=0.7

# Agent Configuration
AGENT_NAME="Customer Success FTE"
AGENT_INSTRUCTIONS_FILE=agent/prompts/system.md

# Tool Configuration
KNOWLEDGE_BASE_MAX_RESULTS=5
TICKET_DEFAULT_PRIORITY=medium
ESCALATION_URGENCY_DEFAULT=medium
```

---

## Acceptance Criteria

- [ ] All tools have Pydantic input schemas
- [ ] Input validation catches invalid data
- [ ] Error handling exists in all tools
- [ ] Agent follows required workflow order
- [ ] Guardrails prevent prohibited responses
- [ ] Handoffs work to specialist agents
- [ ] Streaming responses work
- [ ] All tests pass
- [ ] Tool execution is logged
- [ ] Context is passed correctly to tools

## Related Skills

- `customer-success-agent` - Main agent using SDK
- `postgres-crm-schema` - Tools query database
- `sentiment-analysis` - Used in guardrails
- `mcp-server` - Predecessor to Agents SDK

## References

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Function Tools Guide](https://openai.github.io/openai-agents-python/function-tools/)
