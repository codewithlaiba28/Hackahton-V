---
name: mcp-server
description: Model Context Protocol (MCP) server implementation for customer success agent with tool definitions, async handlers, and protocol compliance.
---

# MCP Server Skill

## Purpose

This skill provides complete guidance for building an MCP (Model Context Protocol) server that exposes customer success agent capabilities as tools. Use this during the incubation phase before transitioning to OpenAI Agents SDK.

## When to Use This Skill

Use this skill when you need to:
- Build a prototype agent during incubation phase
- Expose agent capabilities as MCP tools
- Test tool definitions before production implementation
- Create a bridge between AI agents and external systems
- Rapidly prototype customer support workflows
- Discover requirements through interactive exploration

**Note:** MCP is for **incubation/prototyping**. Transition to OpenAI Agents SDK for production.

---

## MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER ARCHITECTURE                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MCP Server (mcp_server.py)                        │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │    │
│  │  │ search_kb Tool   │  │ create_ticket    │  │ get_history      │   │    │
│  │  │                  │  │ Tool             │  │ Tool             │   │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘   │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │    │
│  │  │ escalate_tool    │  │ send_response    │  │ analyze_sentiment│   │    │
│  │  │                  │  │ Tool             │  │ Tool             │   │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│              ┌───────────────────────────────┐                              │
│              │   MCP Protocol Handler        │                              │
│              │   - Tool registration         │                              │
│              │   - Request routing           │                              │
│              │   - Response formatting       │                              │
│              └───────────────────────────────┘                              │
│                              │                                               │
│         ┌────────────────────┼────────────────────┐                         │
│         ▼                    ▼                    ▼                         │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                 │
│  │  Database   │      │  External   │      │   File      │                 │
│  │  (Postgres) │      │  APIs       │      │   System    │                 │
│  └─────────────┘      └─────────────┘      └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
pip install mcp python-dotenv asyncpg google-api-python-client twilio
```

---

## Basic MCP Server

```python
# mcp_server.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from enum import Enum
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Channel enum for type safety
class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

# Create MCP server instance
server = Server("customer-success-fte")

# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

@server.tool("search_knowledge_base")
async def search_kb(query: str, max_results: int = 5, category: str = None) -> str:
    """Search product documentation for relevant information.
    
    Use this when the customer asks questions about product features,
    how to use something, or needs technical information.
    
    Args:
        query: Search query for product documentation
        max_results: Maximum results to return (default: 5)
        category: Optional category filter (how-to, troubleshooting, feature, faq)
    
    Returns:
        Formatted search results with relevance scores
    """
    try:
        # TODO: Implement actual database search
        # For now, return placeholder
        return f"Search results for '{query}': [Placeholder - implement database search]"
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return "Knowledge base temporarily unavailable. Consider escalating to human support."

@server.tool("create_ticket")
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "medium",
    channel: str = "email"
) -> str:
    """Create a support ticket in the system with channel tracking.
    
    This is the FIRST tool you should call when receiving a customer message.
    All customer interactions must be logged as tickets.
    
    Args:
        customer_id: Unique customer identifier
        issue: Customer issue description
        priority: Ticket priority (low, medium, high, critical)
        channel: Channel the customer used (email, whatsapp, web_form)
    
    Returns:
        The created ticket ID
    """
    try:
        # TODO: Implement actual database insert
        # For now, return placeholder ID
        ticket_id = f"ticket_{customer_id}_{asyncio.get_event_loop().time()}"
        logger.info(f"Created ticket {ticket_id} for customer {customer_id}")
        return ticket_id
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        return f"ticket_error_{customer_id}"

@server.tool("get_customer_history")
async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Get customer's interaction history across ALL channels.
    
    Use this to understand the customer's context before responding.
    This helps provide personalized support and avoid asking for information
    the customer has already provided.
    
    Args:
        customer_id: Unique customer identifier
        limit: Number of recent interactions to return (default: 10)
    
    Returns:
        Formatted customer history including past tickets and conversations
    """
    try:
        # TODO: Implement actual database query
        # For now, return placeholder
        return f"Customer history for {customer_id}: [Placeholder - implement database query]"
    except Exception as e:
        logger.error(f"Failed to get customer history: {e}")
        return "Unable to retrieve customer history. Proceed with caution."

@server.tool("escalate_to_human")
async def escalate_to_human(
    ticket_id: str,
    reason: str,
    context: str,
    urgency: str = "medium"
) -> str:
    """Escalate a ticket to human support.
    
    Use this when:
    - Customer asks about pricing or refunds
    - Customer mentions legal action
    - Customer sentiment is very negative
    - Customer explicitly requests a human
    - You cannot find relevant information after 2 search attempts
    
    Args:
        ticket_id: Ticket to escalate
        reason: Reason for escalation (pricing_inquiry, legal_concern, refund_request, etc.)
        context: Summary of the conversation context
        urgency: Escalation urgency (low, medium, high)
    
    Returns:
        Escalation ID and next steps
    """
    try:
        # TODO: Implement actual escalation
        escalation_id = f"escalation_{ticket_id}"
        logger.info(f"Escalated ticket {ticket_id} with reason {reason}")
        
        return (
            f"Escalation created successfully.\n"
            f"Escalation ID: {escalation_id}\n"
            f"Reason: {reason}\n"
            f"Urgency: {urgency}\n"
            f"A human agent will review this within 24 hours."
        )
    except Exception as e:
        logger.error(f"Failed to escalate: {e}")
        return f"Escalation failed: {str(e)}. Please inform the customer a human will contact them."

@server.tool("send_response")
async def send_response(
    ticket_id: str,
    message: str,
    channel: str,
    customer_email: str = None,
    customer_phone: str = None
) -> str:
    """Send response to the customer via the appropriate channel.
    
    This is the FINAL tool you should call after:
    1. Creating a ticket
    2. Getting customer history
    3. Searching knowledge base
    4. Generating your response
    
    NEVER respond to a customer without calling this tool.
    
    Args:
        ticket_id: Ticket ID to respond to
        message: Response message
        channel: Channel to send via (email, whatsapp, web_form)
        customer_email: Customer email (for email channel)
        customer_phone: Customer phone (for WhatsApp)
    
    Returns:
        Delivery status confirmation
    """
    try:
        # TODO: Implement actual channel sending
        logger.info(f"Sending response via {channel} for ticket {ticket_id}")
        
        return f"Response sent successfully via {channel}. Status: delivered"
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
        return f"Failed to send response: {str(e)}. Please try again or escalate."

@server.tool("analyze_sentiment")
async def analyze_sentiment(message: str) -> str:
    """Analyze customer sentiment in a message.
    
    Use this to understand the customer's emotional state and determine
    if escalation is needed due to negative sentiment.
    
    Args:
        message: Customer message to analyze
    
    Returns:
        Sentiment analysis result with score and recommendation
    """
    try:
        # TODO: Implement actual sentiment analysis
        # Simple keyword-based placeholder
        negative_keywords = ["terrible", "awful", "hate", "broken", "useless"]
        positive_keywords = ["great", "awesome", "love", "thanks", "excellent"]
        
        message_lower = message.lower()
        score = 0.5  # Neutral default
        
        for kw in negative_keywords:
            if kw in message_lower:
                score -= 0.15
        
        for kw in positive_keywords:
            if kw in message_lower:
                score += 0.15
        
        score = max(0, min(1, score))
        
        should_escalate = score < 0.3
        
        return (
            f"Sentiment Analysis:\n"
            f"Score: {score:.2f}\n"
            f"Label: {'Negative' if score < 0.3 else 'Positive' if score > 0.7 else 'Neutral'}\n"
            f"Should Escalate: {should_escalate}"
        )
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "Sentiment analysis unavailable. Proceed with caution."

# =============================================================================
# SERVER RUNNER
# =============================================================================

if __name__ == "__main__":
    # Run the MCP server
    import mcp.server.stdio
    
    logger.info("Starting Customer Success FTE MCP Server...")
    logger.info("Available tools: search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response, analyze_sentiment")
    
    mcp.server.stdio.run_server(server)
```

---

## MCP Server with Database Integration

```python
# mcp_server_with_db.py

from mcp.server import Server
import asyncpg
from typing import Optional, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("customer-success-fte-db")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool():
    """Get or create database connection pool."""
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(
            "postgresql://user:password@localhost:5432/customer_success_fte"
        )
    return db_pool

@server.tool("search_knowledge_base")
async def search_kb(
    query: str,
    max_results: int = 5,
    category: Optional[str] = None
) -> str:
    """Search product documentation using vector similarity."""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Generate embedding (use OpenAI or other embedding service)
            from agent.embeddings import generate_embedding
            embedding = await generate_embedding(query)
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            # Query with vector similarity
            if category:
                rows = await conn.fetch(
                    """
                    SELECT title, content, category,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM knowledge_base
                    WHERE category = $2 AND is_active = TRUE
                    ORDER BY embedding <=> $1::vector
                    LIMIT $3
                    """,
                    embedding_str, category, max_results
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT title, content, category,
                           1 - (embedding <=> $1::vector) as similarity
                    FROM knowledge_base
                    WHERE is_active = TRUE
                    ORDER BY embedding <=> $1::vector
                    LIMIT $2
                    """,
                    embedding_str, max_results
                )
            
            if not rows:
                return "No relevant documentation found. Consider escalating to human support."
            
            # Format results
            formatted = []
            for r in rows:
                formatted.append(
                    f"**{r['title']}** (relevance: {r['similarity']:.2f})\n"
                    f"{r['content'][:500]}..."
                )
            
            return "\n\n---\n\n".join(formatted)
            
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}", exc_info=True)
        return "Knowledge base temporarily unavailable. Please try again or escalate."

@server.tool("create_ticket")
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "medium",
    channel: str = "email"
) -> str:
    """Create a support ticket in PostgreSQL."""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Create ticket
            result = await conn.fetchrow(
                """
                INSERT INTO tickets (customer_id, source_channel, category, priority)
                VALUES ($1, $2, NULL, $3)
                RETURNING id
                """,
                customer_id, channel, priority
            )
            
            ticket_id = str(result['id'])
            logger.info(f"Created ticket {ticket_id} for customer {customer_id}")
            
            return ticket_id
            
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        return f"ticket_error_{customer_id}"

@server.tool("get_customer_history")
async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Get customer's complete interaction history."""
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            # Get customer info
            customer = await conn.fetchrow(
                "SELECT * FROM customers WHERE id = $1",
                customer_id
            )
            
            if not customer:
                return "Customer not found."
            
            # Get conversation history
            conversations = await conn.fetch(
                """
                SELECT id, initial_channel, started_at, status, sentiment_score
                FROM conversations
                WHERE customer_id = $1
                ORDER BY started_at DESC
                LIMIT $2
                """,
                customer_id, limit
            )
            
            # Format history
            formatted = [
                f"**Customer: {customer.get('name', 'Unknown')}**",
                f"Email: {customer.get('email', 'Unknown')}",
                f"Total conversations: {len(conversations)}",
                ""
            ]
            
            for conv in conversations:
                formatted.append(
                    f"- {conv['started_at'].strftime('%Y-%m-%d %H:%M')}: "
                    f"{conv['initial_channel']} - {conv['status']} "
                    f"(sentiment: {conv['sentiment_score'] or 'N/A'})"
                )
            
            return "\n".join(formatted)
            
    except Exception as e:
        logger.error(f"Failed to get customer history: {e}", exc_info=True)
        return "Unable to retrieve customer history. Proceed with caution."

# Run server
if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(server)
```

---

## Testing MCP Tools

```python
# tests/test_mcp_tools.py

import pytest
import asyncio
from mcp_server import (
    search_kb,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
    analyze_sentiment
)

class TestMCPTools:
    """Test MCP tool implementations."""
    
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self):
        """Test knowledge base search."""
        result = await search_kb(
            query="How to reset password",
            max_results=5,
            category="how-to"
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_create_ticket(self):
        """Test ticket creation."""
        result = await create_ticket(
            customer_id="cust_123",
            issue="Cannot login to my account",
            priority="high",
            channel="email"
        )
        
        assert result is not None
        assert result.startswith("ticket_")
    
    @pytest.mark.asyncio
    async def test_get_customer_history(self):
        """Test customer history retrieval."""
        result = await get_customer_history(
            customer_id="cust_123",
            limit=10
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_escalate_to_human(self):
        """Test escalation."""
        result = await escalate_to_human(
            ticket_id="ticket_123",
            reason="pricing_inquiry",
            context="Customer asked about enterprise pricing",
            urgency="medium"
        )
        
        assert "Escalation created" in result
        assert "escalation_" in result
    
    @pytest.mark.asyncio
    async def test_send_response(self):
        """Test response sending."""
        result = await send_response(
            ticket_id="ticket_123",
            message="Here's how to reset your password...",
            channel="email",
            customer_email="test@example.com"
        )
        
        assert "sent successfully" in result
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_positive(self):
        """Test positive sentiment analysis."""
        result = await analyze_sentiment(
            "Thank you so much! Your product is amazing!"
        )
        
        assert "Score:" in result
        assert "Should Escalate:" in result
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_negative(self):
        """Test negative sentiment analysis."""
        result = await analyze_sentiment(
            "This is terrible! Your product is broken and useless!"
        )
        
        assert "Score:" in result
        # Should recommend escalation for negative sentiment
```

---

## Running the MCP Server

```bash
# Run the MCP server
python mcp_server.py

# Or with database integration
python mcp_server_with_db.py
```

---

## MCP Client Example (Claude Code)

```python
# Example of how Claude Code would use MCP tools

"""
When connected to the MCP server, Claude Code can:

1. List available tools:
   - search_knowledge_base
   - create_ticket
   - get_customer_history
   - escalate_to_human
   - send_response
   - analyze_sentiment

2. Call tools:
   - search_knowledge_base(query="password reset", max_results=5)
   - create_ticket(customer_id="cust_123", issue="...", priority="high")
   - get_customer_history(customer_id="cust_123")
   - escalate_to_human(ticket_id="ticket_123", reason="pricing_inquiry", context="...")
   - send_response(ticket_id="ticket_123", message="...", channel="email")
   - analyze_sentiment(message="I'm frustrated with this product")

3. Receive structured responses:
   - Tool results returned as text
   - Errors handled gracefully
   - Logging for debugging
"""
```

---

## Transition Guide: MCP → OpenAI Agents SDK

```python
# Migration example: MCP tool to @function_tool

# BEFORE (MCP):
@server.tool("search_knowledge_base")
async def search_kb(query: str, max_results: int = 5) -> str:
    """Search product documentation."""
    # Implementation...

# AFTER (OpenAI Agents SDK):
from agents import function_tool
from pydantic import BaseModel, Field

class KnowledgeSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(default=5, description="Max results")

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation for relevant information."""
    # Implementation with input validation...
```

---

## Acceptance Criteria

- [ ] MCP server starts without errors
- [ ] All 6 tools are registered and callable
- [ ] Tools return properly formatted responses
- [ ] Error handling exists in all tools
- [ ] Logging is configured properly
- [ ] Database integration works (if implemented)
- [ ] All tests pass
- [ ] Tools can be called by MCP client (Claude Code)
- [ ] Transition path to Agents SDK is documented

## Related Skills

- `openai-agents-sdk` - Production successor to MCP
- `customer-success-agent` - Uses tools for agent logic
- `postgres-crm-schema` - Database for tool implementations
- `sentiment-analysis` - Sentiment tool implementation

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenAI Agents SDK Migration](https://github.com/openai/openai-agents-python)
