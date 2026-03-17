# Data Model: Phase 1 Incubation

**Purpose**: Define all data entities, relationships, and validation rules for Phase 1 prototype.

## Core Entities

### 1. Channel Enum

```python
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"
```

**Validation**: Must be one of the three defined channels.

---

### 2. ChannelMessage

**Purpose**: Represents a customer message from any channel with channel-specific metadata.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class ChannelMessage:
    # Required fields
    channel: Channel                    # Source channel
    content: str                        # Message content
    received_at: datetime               # When message was received
    
    # Customer identification (at least one required)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    
    # Channel-specific metadata
    subject: Optional[str] = None       # Email only
    thread_id: Optional[str] = None     # Email only
    channel_message_id: Optional[str] = None  # External channel ID
    
    # Additional metadata
    metadata: dict = field(default_factory=dict)
    
    @property
    def customer_id(self) -> str:
        """Primary customer identifier (email preferred, phone fallback)."""
        return self.customer_email or self.customer_phone or "unknown"
```

**Validation Rules**:
- `content` must be non-empty
- At least one of `customer_email` or `customer_phone` should be present
- If `channel == EMAIL`, `thread_id` is optional but recommended
- `customer_email` must match email format (validated at ingestion)
- `customer_phone` must match E.164 format (validated at ingestion)

**Relationships**:
- Linked to `CustomerMemory` via `customer_id`
- Becomes a `ConversationTurn` when added to memory

---

### 3. ConversationTurn

**Purpose**: Represents a single turn in a conversation (customer or agent message).

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ConversationTurn:
    role: str                           # "customer" | "agent"
    content: str                        # Message content
    channel: str                        # Channel name
    timestamp: str                      # ISO format timestamp
    sentiment_score: Optional[float] = None  # 0.0 to 1.0
    tool_calls: List[dict] = field(default_factory=list)
```

**Validation Rules**:
- `role` must be "customer" or "agent"
- `content` must be non-empty
- `sentiment_score` must be in range [0.0, 1.0] if present
- `tool_calls` is a list of dicts with keys: `tool`, `args`, `result`

**Relationships**:
- Belongs to a `CustomerMemory`
- Multiple turns form a conversation thread

---

### 4. CustomerMemory

**Purpose**: In-memory representation of a customer's state and conversation history.

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class CustomerMemory:
    customer_id: str                    # Primary key
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    turns: List[ConversationTurn] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    sentiment_trend: List[float] = field(default_factory=list)
    status: str = "active"              # "active" | "escalated" | "resolved"
    escalated: bool = False
```

**Validation Rules**:
- `customer_id` must be non-empty
- At least one of `email` or `phone` must be present
- `status` must be one of: "active", "escalated", "resolved"
- `sentiment_trend` contains last N sentiment scores (default: 10)

**Relationships**:
- Contains multiple `ConversationTurn` objects
- Linked to multiple `Ticket` objects
- Identified by `customer_id`

---

### 5. Ticket

**Purpose**: Represents a support ticket created for each customer interaction.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"

@dataclass
class Ticket:
    ticket_id: str                      # Unique identifier
    customer_id: str                    # Foreign key
    source_channel: Channel             # Original channel
    category: Optional[str] = None      # Issue category
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    issue: str = ""                     # Issue description
    resolution_notes: Optional[str] = None
```

**Validation Rules**:
- `ticket_id` must be unique
- `customer_id` must reference a valid customer
- `source_channel` must be valid Channel enum
- `priority` must be valid TicketPriority enum
- `status` must be valid TicketStatus enum
- `resolved_at` must be set when status becomes "resolved" or "closed"

**Relationships**:
- Linked to `CustomerMemory` via `customer_id`
- May be linked to an `Escalation`
- Created before any response is sent

---

### 6. Escalation

**Purpose**: Represents a handoff to human support with reason and context.

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EscalationReason(str, Enum):
    PRICING_INQUIRY = "pricing_inquiry"
    REFUND_REQUEST = "refund_request"
    LEGAL_THREAT = "legal_threat"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    HUMAN_REQUESTED = "human_requested"
    NO_INFORMATION = "no_information"
    COMPLEX_TECHNICAL = "complex_technical"
    COMPETITOR_INQUIRY = "competitor_inquiry"

class EscalationUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Escalation:
    escalation_id: str                  # Unique identifier
    ticket_id: str                      # Foreign key
    reason: EscalationReason            # Why escalated
    context: str                        # Conversation summary
    urgency: EscalationUrgency = EscalationUrgency.MEDIUM
    escalated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    human_agent: Optional[str] = None   # Assigned human agent
```

**Validation Rules**:
- `escalation_id` must be unique
- `ticket_id` must reference a valid ticket
- `reason` must be valid EscalationReason enum
- `urgency` must be valid EscalationUrgency enum
- `context` must be non-empty and summarize the conversation

**Relationships**:
- Linked to `Ticket` via `ticket_id`
- Created when escalation triggers are detected

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  CustomerMemory │
│  ─────────────  │
│  customer_id    │
│  email          │
│  phone          │
│  status         │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐       1:N       ┌─────────────────┐
│ ConversationTurn│                 │     Ticket      │
│ ─────────────── │                 │ ─────────────── │
│ role            │                 │ ticket_id       │
│ content         │                 │ customer_id     │
│ channel         │                 │ source_channel  │
│ sentiment_score │                 │ status          │
└─────────────────┘                 └────────┬────────┘
                                             │
                                             │ 1:0..1
                                             │
                                             ▼
                                      ┌─────────────────┐
                                      │   Escalation    │
                                      │ ─────────────── │
                                      │ escalation_id   │
                                      │ ticket_id       │
                                      │ reason          │
                                      │ urgency         │
                                      └─────────────────┘
```

---

## State Transitions

### Ticket Lifecycle

```
OPEN → IN_PROGRESS → WAITING → RESOLVED → CLOSED
              ↓
         ESCALATED → (human resolves) → RESOLVED → CLOSED
```

### Customer Memory Lifecycle

```
active → escalated → resolved
   ↓         ↓           ↓
active   (human)    (closed)
```

---

## Validation Functions

```python
def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate E.164 phone format."""
    import re
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def validate_sentiment_score(score: float) -> bool:
    """Validate sentiment score range."""
    return 0.0 <= score <= 1.0

def validate_channel(channel: str) -> bool:
    """Validate channel enum."""
    return channel in ["email", "whatsapp", "web_form"]
```

---

## In-Memory Store Implementation

```python
class ConversationMemoryStore:
    """In-memory store for customer conversations, keyed by customer_id."""
    
    def __init__(self):
        self._store: dict[str, CustomerMemory] = {}
    
    def get_or_create(
        self,
        customer_id: str,
        email: str = None,
        phone: str = None,
        name: str = None
    ) -> CustomerMemory:
        """Get existing customer memory or create new one."""
        if customer_id not in self._store:
            self._store[customer_id] = CustomerMemory(
                customer_id=customer_id,
                email=email,
                phone=phone,
                name=name
            )
        return self._store[customer_id]
    
    def add_turn(self, customer_id: str, turn: ConversationTurn):
        """Add a conversation turn to customer memory."""
        memory = self.get_or_create(customer_id)
        memory.turns.append(turn)
        if turn.sentiment_score is not None:
            memory.sentiment_trend.append(turn.sentiment_score)
            # Keep only last 10 scores
            memory.sentiment_trend = memory.sentiment_trend[-10:]
    
    def get_history_text(self, customer_id: str, limit: int = 10) -> str:
        """Get formatted conversation history for a customer."""
        memory = self._store.get(customer_id)
        if not memory or not memory.turns:
            return "No prior interaction history."
        
        lines = []
        for turn in memory.turns[-limit:]:
            lines.append(f"[{turn.channel.upper()}] {turn.role}: {turn.content}")
        
        return "\n".join(lines)
    
    def mark_escalated(self, customer_id: str):
        """Mark customer conversation as escalated."""
        memory = self.get_or_create(customer_id)
        memory.status = "escalated"
        memory.escalated = True
    
    def mark_resolved(self, customer_id: str):
        """Mark customer conversation as resolved."""
        memory = self.get_or_create(customer_id)
        memory.status = "resolved"
        memory.escalated = False
```

---

## Phase 1 Limitations

**Important**: This data model is for Phase 1 prototype only. Phase 2 will replace:

| Phase 1 Component | Phase 2 Replacement |
|-------------------|---------------------|
| In-memory dict | PostgreSQL database |
| Session-scoped storage | Persistent storage with pgvector |
| Python dataclasses | SQLAlchemy ORM models |
| Keyword sentiment | ML-based sentiment model |
| Flat-file knowledge base | Vector similarity search |

**Migration Path**: The dataclass structure is designed to map directly to PostgreSQL tables in Phase 2.
