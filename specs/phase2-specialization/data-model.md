# Data Model: Phase 2 Specialization

**Purpose**: Complete PostgreSQL schema design for Customer Success FTE CRM/ticketing system with pgvector semantic search.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL CRM SCHEMA                         │
│                                                                  │
│  ┌──────────────────┐                                          │
│  │    customers     │                                          │
│  │  ──────────────  │                                          │
│  │  id (UUID) PK    │──┐                                       │
│  │  email UNIQUE    │  │                                       │
│  │  phone           │  │                                       │
│  │  name            │  │                                       │
│  │  created_at      │  │                                       │
│  │  metadata JSONB  │  │                                       │
│  └────────┬─────────┘  │                                       │
│           │            │                                       │
│           │ 1:N        │                                       │
│           ▼            │                                       │
│  ┌──────────────────┐  │                                       │
│  │customer_identifiers│◀┘                                       │
│  │  ────────────────  │                                       │
│  │  id (UUID) PK    │                                          │
│  │  customer_id FK  │                                          │
│  │  identifier_type │                                          │
│  │  identifier_value│ UNIQUE(type, value)                      │
│  │  verified        │                                          │
│  │  created_at      │                                          │
│  └──────────────────┘                                          │
│           │                                                     │
│           │ 1:N                                                 │
│           ▼                                                     │
│  ┌──────────────────┐     ┌──────────────────┐                │
│  │  conversations   │────▶│     messages     │                │
│  │  ──────────────  │ 1:N │  ──────────────  │                │
│  │  id (UUID) PK    │     │  id (UUID) PK    │                │
│  │  customer_id FK  │     │  conversation_id │                │
│  │  initial_channel │     │  channel         │                │
│  │  started_at      │     │  direction       │                │
│  │  ended_at        │     │  role            │                │
│  │  status          │     │  content         │                │
│  │  sentiment_score │     │  created_at      │                │
│  │  resolution_type │     │  latency_ms      │                │
│  │  escalated_to    │     │  delivery_status │                │
│  │  metadata JSONB  │     │  sentiment_score │                │
│  └────────┬─────────┘     │  tool_calls JSONB│                │
│           │ 1:N           │  channel_message_│                │
│           ▼               │  metadata JSONB  │                │
│  ┌──────────────────┐     └──────────────────┘                │
│  │     tickets      │                                          │
│  │  ──────────────  │                                          │
│  │  id (UUID) PK    │                                          │
│  │  conversation_id │                                          │
│  │  customer_id FK  │                                          │
│  │  source_channel  │                                          │
│  │  category        │                                          │
│  │  priority        │                                          │
│  │  status          │                                          │
│  │  created_at      │                                          │
│  │  resolved_at     │                                          │
│  │  resolution_notes│                                          │
│  │  metadata JSONB  │                                          │
│  └──────────────────┘                                          │
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                │
│  │  knowledge_base  │     │  channel_configs │                │
│  │  ──────────────  │     │  ──────────────  │                │
│  │  id (UUID) PK    │     │  id (UUID) PK    │                │
│  │  title           │     │  channel UNIQUE  │                │
│  │  content         │     │  enabled         │                │
│  │  category        │     │  config JSONB    │                │
│  │  embedding VECTOR│     │  response_template                │
│  │  tags TEXT[]     │     │  max_response_length              │
│  │  created_at      │     │  created_at      │                │
│  │  updated_at      │     │  updated_at      │                │
│  │  is_active       │     └──────────────────┘                │
│  │  view_count      │                                          │
│  │  helpful_count   │     ┌──────────────────┐                │
│  └──────────────────┘     │  agent_metrics   │                │
│                           │  ──────────────  │                │
│  INDEX: ivfflat(embedding)│  id (UUID) PK    │                │
│  lists = 100              │  metric_name     │                │
│                           │  metric_value    │                │
│                           │  channel         │                │
│                           │  dimensions JSONB│                │
│                           │  recorded_at     │                │
│                           └──────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Table Definitions

### 1. customers

**Purpose**: Master customer records with unified identity across all channels.

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,  -- Primary identifier
    phone VARCHAR(50),          -- Secondary identifier (WhatsApp)
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_created ON customers(created_at);
```

**Fields**:
- `id` — UUID primary key
- `email` — UNIQUE, primary cross-channel identifier
- `phone` — Secondary identifier (WhatsApp only)
- `name` — Customer display name
- `created_at` — When customer record created
- `metadata` — Additional customer attributes (JSONB)

**Validation**:
- At least one of `email` or `phone` must be present
- `email` must match email format regex
- `phone` must be E.164 format (e.g., +1234567890)

**Relationships**:
- 1:N → customer_identifiers
- 1:N → conversations

---

### 2. customer_identifiers

**Purpose**: Cross-channel identity mapping (email ↔ phone ↔ WhatsApp).

```sql
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,  -- 'email', 'phone', 'whatsapp'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

-- Indexes
CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer ON customer_identifiers(customer_id);
```

**Fields**:
- `id` — UUID primary key
- `customer_id` — FK to customers
- `identifier_type` — Type of identifier ('email', 'phone', 'whatsapp')
- `identifier_value` — Actual identifier value
- `verified` — Whether identifier has been verified
- `created_at` — When identifier was added

**Validation**:
- UNIQUE constraint on (identifier_type, identifier_value)
- `identifier_type` must be one of: 'email', 'phone', 'whatsapp'

**Relationships**:
- N:1 → customers

**Use Case**: When WhatsApp message arrives from +1234567890, lookup email via this table to retrieve full conversation history.

---

### 3. conversations

**Purpose**: Conversation threads that may span multiple channels.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    initial_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'closed', 'escalated'
    sentiment_score DECIMAL(3,2),  -- -1.0 to 1.0
    resolution_type VARCHAR(50),  -- 'resolved', 'escalated', 'abandoned'
    escalated_to VARCHAR(255),  -- Human agent email/name
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX idx_conversations_started ON conversations(started_at);
```

**Fields**:
- `id` — UUID primary key
- `customer_id` — FK to customers
- `initial_channel` — Channel where conversation started
- `started_at` — When conversation began
- `ended_at` — When conversation closed
- `status` — Current conversation status
- `sentiment_score` — Overall conversation sentiment (-1.0 to 1.0)
- `resolution_type` — How conversation was resolved
- `escalated_to` — Human agent who took over (if escalated)
- `metadata` — Additional conversation attributes (JSONB)

**Validation**:
- `initial_channel` must be one of: 'email', 'whatsapp', 'web_form'
- `status` must be one of: 'active', 'closed', 'escalated'
- `resolution_type` must be one of: 'resolved', 'escalated', 'abandoned'
- `sentiment_score` must be between -1.0 and 1.0

**Relationships**:
- N:1 → customers
- 1:N → messages
- 1:N → tickets

**State Transitions**:
```
active → closed (resolved successfully)
active → escalated (human took over)
active → abandoned (customer stopped responding)
escalated → closed (human resolved)
```

---

### 4. messages

**Purpose**: Individual message records with channel tracking and delivery status.

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(20) NOT NULL,  -- 'inbound', 'outbound'
    role VARCHAR(20) NOT NULL,  -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,  -- Processing latency
    tool_calls JSONB DEFAULT '[]',  -- Tools called by agent
    channel_message_id VARCHAR(255),  -- External ID (Gmail Message-ID, Twilio SID)
    delivery_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'delivered', 'failed'
    sentiment_score DECIMAL(3,2),  -- Message-level sentiment
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_direction ON messages(direction);
```

**Fields**:
- `id` — UUID primary key
- `conversation_id` — FK to conversations
- `channel` — Channel this message arrived/sent on
- `direction` — Inbound (customer) or outbound (agent)
- `role` — Who sent the message (customer, agent, system)
- `content` — Message text
- `created_at` — When message was sent/received
- `tokens_used` — LLM tokens consumed (for agent messages)
- `latency_ms` — Processing latency in milliseconds
- `tool_calls` — List of tools called by agent (JSONB)
- `channel_message_id` — External channel ID (Gmail Message-ID, Twilio SID)
- `delivery_status` — Delivery status for outbound messages
- `sentiment_score` — Sentiment of this specific message
- `metadata` — Additional message attributes (JSONB)

**Validation**:
- `channel` must be one of: 'email', 'whatsapp', 'web_form'
- `direction` must be one of: 'inbound', 'outbound'
- `role` must be one of: 'customer', 'agent', 'system'
- `delivery_status` must be one of: 'pending', 'sent', 'delivered', 'failed'
- `sentiment_score` must be between -1.0 and 1.0

**Relationships**:
- N:1 → conversations

**Critical Notes**:
- `channel_message_id` is crucial for thread preservation (Gmail) and delivery tracking (Twilio)
- `latency_ms` used for performance monitoring and SLA tracking
- `tool_calls` stores which agent tools were invoked (for debugging)

---

### 5. tickets

**Purpose**: Support ticket tracking with lifecycle management.

```sql
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    source_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    category VARCHAR(100),  -- 'technical', 'billing', 'feature_request', etc.
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'open',  -- 'open', 'in_progress', 'waiting', 'resolved', 'closed', 'escalated'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    assigned_to VARCHAR(255),  -- Human agent assigned
    sla_deadline TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(source_channel);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_tickets_priority ON tickets(priority);
```

**Fields**:
- `id` — UUID primary key (shown to customer as ticket ID)
- `conversation_id` — FK to conversations
- `customer_id` — FK to customers
- `source_channel` — Channel where ticket originated
- `category` — Ticket category for routing/reporting
- `priority` — Ticket priority level
- `status` — Current ticket status
- `created_at` — When ticket was created
- `resolved_at` — When ticket was resolved
- `resolution_notes` — Human-readable resolution summary
- `assigned_to` — Human agent email/name (if assigned)
- `sla_deadline` — SLA deadline for resolution
- `metadata` — Additional ticket attributes (JSONB)

**Validation**:
- `source_channel` must be one of: 'email', 'whatsapp', 'web_form'
- `priority` must be one of: 'low', 'medium', 'high', 'critical'
- `status` must be one of: 'open', 'in_progress', 'waiting', 'resolved', 'closed', 'escalated'

**Relationships**:
- N:1 → conversations
- N:1 → customers

**State Transitions**:
```
open → in_progress (agent started working)
in_progress → waiting (waiting for customer response)
in_progress → resolved (issue resolved)
open → escalated (escalated to human)
escalated → resolved (human resolved)
resolved → closed (customer confirmed resolution)
```

---

### 6. knowledge_base

**Purpose**: Product documentation with vector embeddings for semantic search.

```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),  -- 'feature', 'how-to', 'troubleshooting', 'faq'
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small dimension
    tags TEXT[],  -- Array of tags for filtering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0
);

-- Vector similarity index (IVFFlat for performance)
CREATE INDEX idx_knowledge_embedding 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Regular indexes
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_tags ON knowledge_base USING GIN (tags);
CREATE INDEX idx_knowledge_active ON knowledge_base(is_active);
```

**Fields**:
- `id` — UUID primary key
- `title` — Document title
- `content` — Document content
- `category` — Document category for filtering
- `embedding` — Vector embedding (1536 dimensions for OpenAI)
- `tags` — Array of tags for additional filtering
- `created_at` — When document was added
- `updated_at` — When document was last updated
- `is_active` — Whether document is active (soft delete)
- `view_count` — How many times document was retrieved
- `helpful_count` — How many times marked helpful

**Validation**:
- `embedding` must be VECTOR(1536) for OpenAI compatibility
- `category` must be one of: 'feature', 'how-to', 'troubleshooting', 'faq'

**Indexes**:
- **IVFFlat index** — For approximate nearest neighbor search (semantic search)
- `lists = 100` — Balance between speed and accuracy (tune based on data size)

**Usage**:
```sql
-- Semantic search example
SELECT title, content, category,
       1 - (embedding <=> $1::vector) as similarity
FROM knowledge_base
WHERE is_active = TRUE
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

---

### 7. channel_configs

**Purpose**: Per-channel configuration (API keys, templates, limits).

```sql
CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel VARCHAR(50) UNIQUE NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,  -- API keys, webhook URLs, etc.
    response_template TEXT,
    max_response_length INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Fields**:
- `id` — UUID primary key
- `channel` — Channel name (UNIQUE)
- `enabled` — Whether channel is enabled
- `config` — Channel-specific configuration (JSONB)
- `response_template` — Default response template for channel
- `max_response_length` — Maximum response length (words for email/web, chars for WhatsApp)
- `created_at` — When config was created
- `updated_at` — When config was last updated

**Validation**:
- `channel` must be one of: 'email', 'whatsapp', 'web_form'

**Example Config (JSONB)**:
```json
{
  "email": {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "gmail_api_credentials": "..."
  },
  "whatsapp": {
    "twilio_account_sid": "...",
    "twilio_auth_token": "...",
    "whatsapp_number": "whatsapp:+14155238886"
  },
  "web_form": {
    "confirmation_email_enabled": true,
    "notification_email": "support@techcorp.com"
  }
}
```

---

### 8. agent_metrics

**Purpose**: Time-series metrics for performance monitoring and reporting.

```sql
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    channel VARCHAR(50),  -- Optional: channel-specific metrics
    dimensions JSONB DEFAULT '{}',  -- Additional dimensions (date, hour, etc.)
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for metrics queries
CREATE INDEX idx_metrics_name ON agent_metrics(metric_name);
CREATE INDEX idx_metrics_recorded ON agent_metrics(recorded_at);
CREATE INDEX idx_metrics_channel ON agent_metrics(channel);
```

**Fields**:
- `id` — UUID primary key
- `metric_name` — Metric name (e.g., 'processing_latency', 'escalation_rate')
- `metric_value` — Metric value (decimal for precision)
- `channel` — Optional channel filter
- `dimensions` — Additional dimensions for slicing (JSONB)
- `recorded_at` — When metric was recorded

**Example Metrics**:
- `processing_latency` — Agent processing time in seconds
- `escalation_rate` — Percentage of tickets escalated
- `sentiment_score` — Average sentiment score
- `token_usage` — LLM tokens consumed
- `kafka_lag` — Kafka consumer lag in messages

**Usage**:
```sql
-- Get channel metrics for last 24 hours
SELECT 
    channel,
    COUNT(*) as total_conversations,
    AVG(metric_value) as avg_sentiment,
    COUNT(CASE WHEN metric_name = 'escalation' THEN 1 END) as escalations
FROM agent_metrics
WHERE recorded_at > NOW() - INTERVAL '24 hours'
GROUP BY channel;
```

---

## pgvector Setup

**Prerequisites**:

```sql
-- Enable pgvector extension (must be done before schema creation)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

**IVFFlat Index Configuration**:

```sql
-- Create IVFFlat index for approximate nearest neighbor search
CREATE INDEX idx_knowledge_embedding 
ON knowledge_base USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Index Tuning**:
- `lists` parameter controls speed/accuracy tradeoff
- Rule of thumb: `lists = rows / 1000` (for < 1M rows)
- For larger datasets: `lists = rows / 100`
- Test with your data size to find optimal value

**Semantic Search Query**:

```sql
-- Search knowledge base with vector similarity
SELECT 
    title,
    content,
    category,
    1 - (embedding <=> $1::vector) as similarity
FROM knowledge_base
WHERE is_active = TRUE
  AND ($2::text IS NULL OR category = $2)
ORDER BY embedding <=> $1::vector
LIMIT $3;
```

**Parameters**:
- `$1` — Query embedding (VECTOR(1536))
- `$2` — Optional category filter (TEXT)
- `$3` — Max results to return (INTEGER)

---

## Database Access Layer (queries.py)

**Query Organization**:

```python
# database/queries.py

# Customer queries
async def find_customer_by_email(conn, email: str) -> Optional[dict]
async def find_customer_by_phone(conn, phone: str) -> Optional[dict]
async def create_customer(conn, email: str, phone: str, name: str) -> str  # returns UUID
async def get_customer_with_history(conn, customer_id: str) -> dict

# Conversation queries
async def get_active_conversation(conn, customer_id: str) -> Optional[dict]
async def create_conversation(conn, customer_id: str, channel: str) -> str
async def close_conversation(conn, conversation_id: str, resolution_type: str) -> None
async def update_conversation_sentiment(conn, conversation_id: str, score: float) -> None

# Message queries
async def store_message(conn, **fields) -> str
async def load_conversation_messages(conn, conversation_id: str, limit: int = 20) -> list

# Ticket queries
async def create_ticket(conn, customer_id: str, conversation_id: str, channel: str, **fields) -> str
async def update_ticket_status(conn, ticket_id: str, status: str, notes: str = None) -> None
async def get_ticket_by_id(conn, ticket_id: str) -> Optional[dict]
async def get_ticket_with_messages(conn, ticket_id: str) -> dict

# Knowledge base queries
async def search_knowledge_base(conn, embedding: list[float], limit: int = 5) -> list[dict]
async def insert_knowledge_entry(conn, title: str, content: str, category: str, embedding: list[float]) -> str

# Metrics queries
async def record_metric(conn, name: str, value: float, channel: str = None, dimensions: dict = None) -> None
async def get_channel_metrics_last_24h(conn) -> list[dict]
```

---

## Connection Pool Strategy

```python
# database/queries.py

import asyncpg
import os
from typing import Optional

_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """Get or create connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=20,
            command_timeout=30,
        )
    return _pool

async def close_pool():
    """Close connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

**Configuration**:
- `min_size=2` — Minimum idle connections
- `max_size=20` — Maximum connections (per pod)
- `command_timeout=30` — Query timeout in seconds

**Scaling**:
- 3 API pods × 20 connections = 60 max connections
- 3 Worker pods × 20 connections = 60 max connections
- Total: 120 connections (configure PostgreSQL `max_connections` accordingly)

---

## Migration Strategy

**Initial Migration (001_initial_schema.sql)**:

```sql
-- Migration 001: Initial schema
-- Created: 2026-03-17
-- Description: Create all 8 tables with indexes

BEGIN;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (in dependency order)
CREATE TABLE customers (...);
CREATE TABLE customer_identifiers (...);
CREATE TABLE conversations (...);
CREATE TABLE messages (...);
CREATE TABLE tickets (...);
CREATE TABLE knowledge_base (...);
CREATE TABLE channel_configs (...);
CREATE TABLE agent_metrics (...);

-- Create indexes
-- (all indexes from table definitions above)

COMMIT;
```

**Future Migrations**:
- `002_add_sla_columns.sql` — Add SLA tracking columns
- `003_add_audit_logging.sql` — Add audit logging tables
- `004_add_user_roles.sql` — Add user roles and permissions

---

**Next Step**: Create API contracts in `contracts/openapi.yaml` and `contracts/kafka-topics.yaml`
