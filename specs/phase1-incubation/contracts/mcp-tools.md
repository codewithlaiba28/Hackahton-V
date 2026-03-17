# MCP Tool Contracts: Customer Success FTE

**Purpose**: Define all MCP tools exposed by the prototype for Claude Code invocation.

## Server Definition

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("customer-success-fte")
```

---

## Tool 1: search_knowledge_base

**Purpose**: Search product documentation for relevant information.

**When to use**: Customer asks product questions, how-to guidance, or technical information.

### Input Schema

```python
class SearchKnowledgeBaseInput(BaseModel):
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
```

### Output

```python
str  # Formatted search results with relevance scores
```

### Example Output

```
**API Key Management** (relevance: 0.92)
To reset your API key, navigate to Settings > API > Keys and click "Rotate Key"...

**Authentication Overview** (relevance: 0.78)
Our API uses OAuth 2.0 for authentication. You can find your credentials in...
```

### Error Handling

- If KB unavailable: "Knowledge base temporarily unavailable. Consider escalating."
- If no results: "No relevant documentation found. Consider escalating to human support."

---

## Tool 2: create_ticket

**Purpose**: Create a support ticket in the system with channel tracking.

**When to use**: FIRST tool called when receiving any customer message.

### Input Schema

```python
class CreateTicketInput(BaseModel):
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
```

### Output

```python
str  # The created ticket ID (e.g., "ticket_12345")
```

### Example Output

```
ticket_cust123_1711234567
```

### Error Handling

- If invalid customer_id: Return "ticket_error_{customer_id}"
- Log error but continue flow (never block ticket creation)

---

## Tool 3: get_customer_history

**Purpose**: Get customer's interaction history across ALL channels.

**When to use**: After creating ticket, before generating response.

### Input Schema

```python
class GetCustomerHistoryInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    limit: int = Field(
        default=10,
        description="Number of recent interactions to return",
        ge=1,
        le=50
    )
```

### Output

```python
str  # Formatted customer history
```

### Example Output

```
**Customer: John Doe**
Email: john@example.com
Total conversations: 3
Total tickets: 5
Resolved tickets: 4
Average sentiment: 0.72
Last contact: 2024-03-15 10:30 AM

Recent interactions:
[EMAIL] customer: How do I reset my API key?
[AGENT]: To reset your API key...
[WHATSAPP] customer: Thanks!
```

### Error Handling

- If customer not found: "This is a new customer with no prior interaction history."

---

## Tool 4: escalate_to_human

**Purpose**: Escalate a ticket to human support.

**When to use**: Pricing questions, legal threats, negative sentiment, explicit human requests.

### Input Schema

```python
class EscalateToHumanInput(BaseModel):
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
    urgency: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Escalation urgency"
    )
```

### Output

```python
str  # Escalation ID and next steps
```

### Example Output

```
Escalation created successfully.
Escalation ID: esc_ticket123_1711234567
Reason: pricing_inquiry
Urgency: medium
A human agent will review this within 24 hours.
```

### Error Handling

- If escalation fails: "Escalation failed: {error}. Please inform the customer a human will contact them."

---

## Tool 5: send_response

**Purpose**: Send response to the customer via the appropriate channel.

**When to use**: FINAL tool called after generating the response.

### Input Schema

```python
class SendResponseInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID to respond to")
    message: str = Field(..., description="Response message", min_length=1)
    channel: Literal["email", "whatsapp", "web_form"] = Field(
        ...,
        description="Channel to send via"
    )
    customer_email: Optional[str] = Field(
        default=None,
        description="Customer email (for email channel)"
    )
    customer_phone: Optional[str] = Field(
        default=None,
        description="Customer phone (for WhatsApp)"
    )
```

### Output

```python
str  # Delivery status confirmation
```

### Example Output

```
Response sent successfully via email. Status: delivered
```

### Error Handling

- If delivery fails: "Failed to send response: {error}. Please try again or escalate."

---

## Tool 6: analyze_sentiment

**Purpose**: Analyze customer sentiment in a message.

**When to use**: Every incoming customer message.

### Input Schema

```python
class AnalyzeSentimentInput(BaseModel):
    message: str = Field(..., description="Customer message to analyze")
```

### Output

```python
dict  # Sentiment analysis result
{
    "score": float,      # 0.0 to 1.0
    "label": str,        # "positive", "neutral", "negative"
    "should_escalate": bool,
    "reason": str        # Escalation reason if applicable
}
```

### Example Output

```python
{
    "score": 0.15,
    "label": "negative",
    "should_escalate": True,
    "reason": "negative_sentiment"
}
```

### Error Handling

- If analysis fails: Return neutral score (0.5) with warning log

---

## Tool Usage Order

**Required workflow order** (enforced by constitution):

```
1. create_ticket          (FIRST - before any response)
2. get_customer_history   (Understand context)
3. search_knowledge_base  (If product question)
4. analyze_sentiment      (Evaluate emotional state)
5. escalate_to_human      (If escalation triggers detected)
6. send_response          (FINAL - deliver response)
```

**Violation**: Responding without calling `create_ticket` first is a constitution violation.

---

## MCP Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("customer-success-fte")

@server.tool("search_knowledge_base")
async def search_kb(query: str, max_results: int = 5, category: str = None) -> str:
    """Search product documentation for relevant information."""
    # Implementation from knowledge_base.py
    pass

@server.tool("create_ticket")
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "medium",
    channel: str = "email"
) -> str:
    """Create a support ticket in the system with channel tracking."""
    # Implementation
    pass

@server.tool("get_customer_history")
async def get_history(customer_id: str, limit: int = 10) -> str:
    """Get customer's interaction history across ALL channels."""
    # Implementation
    pass

@server.tool("escalate_to_human")
async def escalate(
    ticket_id: str,
    reason: str,
    context: str,
    urgency: str = "medium"
) -> str:
    """Escalate a ticket to human support."""
    # Implementation
    pass

@server.tool("send_response")
async def send_response(
    ticket_id: str,
    message: str,
    channel: str,
    customer_email: str = None,
    customer_phone: str = None
) -> str:
    """Send response to the customer via the appropriate channel."""
    # Implementation
    pass

@server.tool("analyze_sentiment")
async def analyze_sentiment(message: str) -> str:
    """Analyze customer sentiment in a message."""
    # Implementation
    pass

if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(server)
```

---

## Testing MCP Tools

```python
# tests/test_mcp_tools.py
import pytest

class TestMCPTools:
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self):
        result = await search_kb("API key reset")
        assert result is not None
        assert "API" in result or "key" in result
    
    @pytest.mark.asyncio
    async def test_create_ticket(self):
        result = await create_ticket(
            customer_id="test_123",
            issue="Test issue for ticket creation",
            priority="medium",
            channel="email"
        )
        assert result.startswith("ticket_")
    
    @pytest.mark.asyncio
    async def test_get_customer_history(self):
        result = await get_history("test_123")
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_escalate_to_human(self):
        result = await escalate(
            ticket_id="ticket_123",
            reason="pricing_inquiry",
            context="Customer asked about enterprise pricing"
        )
        assert "Escalation created" in result
    
    @pytest.mark.asyncio
    async def test_send_response(self):
        result = await send_response(
            ticket_id="ticket_123",
            message="Test response",
            channel="email",
            customer_email="test@example.com"
        )
        assert "sent successfully" in result
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self):
        result = await analyze_sentiment("This is terrible and broken!")
        assert "score" in result
        assert result["should_escalate"] == True
```
