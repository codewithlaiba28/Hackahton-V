# Research Notes: Phase 1 Technology Stack

**Purpose**: Document technology research and decisions for Phase 1 prototype.

---

## Decision: MCP Server Framework

**What was chosen**: MCP (Model Context Protocol) Server

**Rationale**:
- Standardized tool exposure pattern
- Compatible with Claude Code integration
- Validates tool contracts before migration to OpenAI SDK
- Well-documented Python implementation

**Alternatives considered**:
- Direct function calls (rejected: no tool contract validation)
- OpenAI Agents SDK (deferred to Phase 2)
- Custom tool registry (rejected: reinventing the wheel)

---

## Decision: Anthropic Claude API

**What was chosen**: Anthropic SDK (Claude API)

**Rationale**:
- Claude Code is the designated "Agent Factory" per constitution
- Async client support for concurrent requests
- Well-maintained Python SDK
- Good rate limits for prototype phase

**Rate limits** (as of 2026-03-17):
- Standard: 50 requests/minute
- Batch: 10,000 tokens/minute
- Retry with exponential backoff recommended

**Best practices**:
- Use async client for better performance
- Cache responses for repeated queries
- Implement retry logic with backoff
- Log all API calls for debugging

---

## Decision: Keyword-Based Sentiment (Phase 1)

**What was chosen**: Simple keyword scoring with TextBlob fallback

**Rationale**:
- No ML model dependency in prototype
- Fast and interpretable
- Good enough for escalation triggers
- Can be replaced with ML model in Phase 2

**Implementation**:
```python
NEGATIVE_KEYWORDS = ["broken", "useless", "terrible", "frustrated", "angry"]
POSITIVE_KEYWORDS = ["thank", "great", "excellent", "helpful", "love"]
score = (positive - negative * 1.5) / total_words  # clamped to [0, 1]
```

**Alternatives considered**:
- TextBlob sentiment (too slow for Phase 1)
- Hugging Face transformers (overkill for prototype)
- Custom fine-tuned model (Phase 2 consideration)

---

## Decision: In-Memory Storage (Phase 1)

**What was chosen**: Python dictionary with dataclasses

**Rationale**:
- Fastest iteration speed
- No database setup required
- Session-scoped is sufficient for Phase 1
- Maps directly to PostgreSQL schema in Phase 2

**Implementation**:
```python
class ConversationMemoryStore:
    _store: dict[str, CustomerMemory] = {}
    
    def get_or_create(self, customer_id: str) -> CustomerMemory:
        # ...
```

**Limitations**:
- Data lost on restart (acceptable for Phase 1)
- No persistence across sessions
- Not thread-safe (single-threaded in Phase 1)

**Phase 2 migration**: PostgreSQL with SQLAlchemy ORM

---

## Decision: Flat-File Knowledge Base (Phase 1)

**What was chosen**: Markdown file with keyword search

**Rationale**:
- No database required
- Easy to update and maintain
- Keyword search sufficient for prototype
- Replaced by pgvector in Phase 2

**Implementation**:
```python
# Parse sections at startup
sections = parse_markdown("context/product-docs.md")

# Search with keyword overlap
def search(query: str, max_results: int = 5) -> list:
    scores = [(section, keyword_overlap(query, section)) for section in sections]
    return sorted(scores, key=lambda x: x[1], reverse=True)[:max_results]
```

**Alternatives considered**:
- Elasticsearch (overkill for Phase 1)
- pgvector (Phase 2)
- Simple string matching (too naive)

---

## Decision: Channel Simulation (Phase 1)

**What was chosen**: Dataclass-based simulators

**Rationale**:
- Consistent message format across channels
- Easy to test without real API integrations
- Simulates real webhook payloads
- Real integrations in Phase 2

**Implementation**:
```python
@dataclass
class ChannelMessage:
    channel: Channel
    content: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    # ...
```

**Phase 2 migration**:
- Gmail: Real Gmail API + Pub/Sub
- WhatsApp: Real Twilio WhatsApp API
- Web Form: Real FastAPI endpoint

---

## Decision: Pydantic for Data Validation

**What was chosen**: Pydantic v2+

**Rationale**:
- Type-safe data models
- Automatic validation
- Great IDE support
- Industry standard for Python APIs

**Usage**:
```python
from pydantic import BaseModel, Field

class CreateTicketInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    issue: str = Field(..., min_length=10)
    priority: Literal["low", "medium", "high"] = "medium"
```

---

## Decision: pytest for Testing

**What was chosen**: pytest with pytest-asyncio

**Rationale**:
- Industry standard for Python testing
- Async test support
- Great error messages
- Rich plugin ecosystem

**Test structure**:
```python
import pytest

@pytest.mark.asyncio
async def test_something():
    assert True
```

---

## Summary of Technology Choices

| Component | Phase 1 Choice | Phase 2 Migration |
|-----------|---------------|-------------------|
| Agent Framework | MCP Server | OpenAI Agents SDK |
| LLM | Claude API | Claude or GPT-4 |
| Storage | In-memory dict | PostgreSQL + pgvector |
| Knowledge Base | Flat file + keyword | Vector similarity search |
| Sentiment | Keyword scoring | ML-based model |
| Channels | Simulated | Real API integrations |
| Testing | pytest | pytest + integration tests |

---

## Unresolved Questions

None - all NEEDS CLARIFICATION items resolved in Phase 0 research.
