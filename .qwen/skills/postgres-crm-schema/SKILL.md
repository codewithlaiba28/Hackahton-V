---
name: postgres-crm-schema
description: PostgreSQL CRM/ticket management system schema with pgvector for semantic search, customer tracking, conversation history, and multi-channel message storage.
---

# PostgreSQL CRM Schema Skill

## Purpose

This skill provides a complete PostgreSQL database schema for building a CRM/ticket management system that serves as the backend for a Customer Success AI agent. Includes pgvector integration for semantic search and multi-channel support.

## When to Use This Skill

Use this skill when you need to:
- Build a custom CRM/ticket management system
- Track customers across multiple communication channels
- Store conversation history with channel metadata
- Implement semantic search for knowledge base
- Track agent performance metrics
- Support cross-channel customer identification

---

## Database Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL CRM Schema                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────────┐                     │
│  │  customers   │────▶│customer_identifiers│                    │
│  └──────────────┘     └──────────────────┘                     │
│         │                       │                               │
│         ▼                       │                               │
│  ┌──────────────┐               │                               │
│  │conversations │◀──────────────┘                               │
│  └──────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────────┐                     │
│  │   messages   │     │  knowledge_base  │ (pgvector)          │
│  └──────────────┘     └──────────────────┘                     │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────────┐                     │
│  │   tickets    │     │  channel_configs │                     │
│  └──────────────┘     └──────────────────┘                     │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │agent_metrics │                                               │
│  └──────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Schema (schema.sql)

```sql
-- =============================================================================
-- CUSTOMER SUCCESS FTE - CRM/TICKET MANAGEMENT SYSTEM
-- =============================================================================
-- This PostgreSQL schema serves as your complete CRM system for tracking:
-- - Customers (unified across all channels)
-- - Conversations and message history
-- - Support tickets and their lifecycle
-- - Knowledge base for AI responses
-- - Performance metrics and reporting
-- =============================================================================

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- CUSTOMERS TABLE (unified across channels)
-- =============================================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index for customer lookup
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_created ON customers(created_at);

-- =============================================================================
-- CUSTOMER IDENTIFIERS (for cross-channel matching)
-- =============================================================================
CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL,  -- 'email', 'phone', 'whatsapp'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

-- Index for identifier lookup
CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_customer_identifiers_customer ON customer_identifiers(customer_id);

-- =============================================================================
-- CONVERSATIONS TABLE
-- =============================================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Indexes for conversation queries
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX idx_conversations_started ON conversations(started_at);

-- =============================================================================
-- MESSAGES TABLE (with channel tracking)
-- =============================================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(20) NOT NULL,  -- 'inbound', 'outbound'
    role VARCHAR(20) NOT NULL,  -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,
    tool_calls JSONB DEFAULT '[]',  -- List of tool calls made by agent
    channel_message_id VARCHAR(255),  -- External ID (Gmail message ID, Twilio SID)
    delivery_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'delivered', 'failed'
    sentiment_score DECIMAL(3,2),  -- Message-level sentiment
    metadata JSONB DEFAULT '{}'
);

-- Indexes for message queries
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_direction ON messages(direction);

-- =============================================================================
-- TICKETS TABLE
-- =============================================================================
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    source_channel VARCHAR(50) NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    category VARCHAR(100),  -- 'technical', 'billing', 'feature_request', etc.
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'open',  -- 'open', 'in_progress', 'waiting', 'resolved', 'closed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    assigned_to VARCHAR(255),  -- Human agent assigned
    sla_deadline TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Indexes for ticket queries
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(source_channel);
CREATE INDEX idx_tickets_customer ON tickets(customer_id);
CREATE INDEX idx_tickets_created ON tickets(created_at);
CREATE INDEX idx_tickets_priority ON tickets(priority);

-- =============================================================================
-- KNOWLEDGE BASE TABLE (with pgvector for semantic search)
-- =============================================================================
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),  -- 'feature', 'how-to', 'troubleshooting', 'faq'
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    tags TEXT[],  -- Array of tags for filtering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0
);

-- Vector similarity index for semantic search
CREATE INDEX idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Regular indexes
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_tags ON knowledge_base USING GIN (tags);
CREATE INDEX idx_knowledge_active ON knowledge_base(is_active);

-- =============================================================================
-- CHANNEL CONFIGS TABLE
-- =============================================================================
CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) UNIQUE NOT NULL,  -- 'email', 'whatsapp', 'web_form'
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL,  -- API keys, webhook URLs, etc.
    response_template TEXT,
    max_response_length INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- AGENT METRICS TABLE
-- =============================================================================
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- =============================================================================
-- ESCALATIONS TABLE
-- =============================================================================
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    reason_code VARCHAR(50) NOT NULL,  -- 'pricing_inquiry', 'legal_concern', 'negative_sentiment', etc.
    reason_detail TEXT,
    escalated_to VARCHAR(255),  -- Human agent email/name
    escalated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'accepted', 'resolved'
    metadata JSONB DEFAULT '{}'
);

-- Indexes for escalation queries
CREATE INDEX idx_escalations_ticket ON escalations(ticket_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_reason ON escalations(reason_code);

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at
    BEFORE UPDATE ON channel_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to generate embedding for knowledge base entries
CREATE OR REPLACE FUNCTION generate_knowledge_embedding()
RETURNS TRIGGER AS $$
BEGIN
    -- This would be called from application code with actual embedding
    -- NEW.embedding = await generate_embedding(NEW.title || ' ' || NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View: Active conversations with customer info
CREATE VIEW active_conversations_view AS
SELECT 
    c.id AS conversation_id,
    c.customer_id,
    cust.email AS customer_email,
    cust.name AS customer_name,
    c.initial_channel,
    c.started_at,
    c.status,
    c.sentiment_score,
    COUNT(m.id) AS message_count,
    (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) AS last_message
FROM conversations c
LEFT JOIN customers cust ON c.customer_id = cust.id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE c.status = 'active'
GROUP BY c.id, cust.email, cust.name;

-- View: Ticket summary by status and channel
CREATE VIEW ticket_summary_view AS
SELECT 
    source_channel,
    status,
    priority,
    COUNT(*) AS ticket_count,
    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/3600) AS avg_resolution_hours
FROM tickets
WHERE resolved_at IS NOT NULL
GROUP BY source_channel, status, priority;

-- View: Customer interaction history
CREATE VIEW customer_history_view AS
SELECT 
    cust.id AS customer_id,
    cust.email,
    cust.name,
    COUNT(DISTINCT conv.id) AS total_conversations,
    COUNT(DISTINCT tick.id) AS total_tickets,
    COUNT(DISTINCT CASE WHEN tick.status = 'resolved' THEN tick.id END) AS resolved_tickets,
    AVG(conv.sentiment_score) AS avg_sentiment,
    MAX(conv.started_at) AS last_contact
FROM customers cust
LEFT JOIN conversations conv ON cust.id = conv.customer_id
LEFT JOIN tickets tick ON cust.id = tick.customer_id
GROUP BY cust.id, cust.email, cust.name;

-- =============================================================================
-- SEED DATA
-- =============================================================================

-- Insert channel configurations
INSERT INTO channel_configs (channel, enabled, config, max_response_length) VALUES
('email', TRUE, '{"smtp_host": "smtp.gmail.com", "smtp_port": 587}', 500),
('whatsapp', TRUE, '{"twilio_enabled": true}', 300),
('web_form', TRUE, '{"confirmation_email": true}', 300);

-- =============================================================================
-- PERMISSIONS (adjust as needed)
-- =============================================================================

-- Create role for the application
-- CREATE ROLE app_user WITH LOGIN PASSWORD 'your_secure_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

---

## Database Access Functions (queries.py)

```python
# database/queries.py

import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class DatabaseQueries:
    """PostgreSQL database access functions for CRM system."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def create_pool(self):
        """Create connection pool."""
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def close_pool(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
    
    # =========================================================================
    # CUSTOMER QUERIES
    # =========================================================================
    
    async def get_or_create_customer(self, email: str = None, phone: str = None) -> Dict:
        """Get existing customer or create new one."""
        async with self.pool.acquire() as conn:
            # Try to find by email
            if email:
                customer = await conn.fetchrow(
                    "SELECT * FROM customers WHERE email = $1", email
                )
                if customer:
                    return dict(customer)
            
            # Try to find by phone
            if phone:
                customer = await conn.fetchrow(
                    "SELECT * FROM customers WHERE phone = $1", phone
                )
                if customer:
                    return dict(customer)
            
            # Create new customer
            customer_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO customers (id, email, phone)
                VALUES ($1, $2, $3)
                """,
                customer_id, email, phone
            )
            
            return {
                'id': str(customer_id),
                'email': email,
                'phone': phone,
                'name': None,
                'created_at': datetime.utcnow()
            }
    
    async def add_customer_identifier(self, customer_id: str, identifier_type: str, identifier_value: str):
        """Add a new identifier for a customer (for cross-channel matching)."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
                VALUES ($1, $2, $3)
                ON CONFLICT (identifier_type, identifier_value) DO NOTHING
                """,
                customer_id, identifier_type, identifier_value
            )
    
    async def get_customer_history(self, customer_id: str) -> Dict:
        """Get customer's complete interaction history."""
        async with self.pool.acquire() as conn:
            history = await conn.fetchrow(
                "SELECT * FROM customer_history_view WHERE customer_id = $1",
                customer_id
            )
            return dict(history) if history else None
    
    # =========================================================================
    # CONVERSATION QUERIES
    # =========================================================================
    
    async def create_conversation(self, customer_id: str, initial_channel: str) -> str:
        """Create a new conversation."""
        async with self.pool.acquire() as conn:
            conversation_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO conversations (id, customer_id, initial_channel)
                VALUES ($1, $2, $3)
                """,
                conversation_id, customer_id, initial_channel
            )
            return str(conversation_id)
    
    async def get_active_conversation(self, customer_id: str, channel: str) -> Optional[str]:
        """Get active conversation for a customer on a specific channel."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id FROM conversations
                WHERE customer_id = $1 AND initial_channel = $2 AND status = 'active'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                customer_id, channel
            )
            return str(row['id']) if row else None
    
    async def update_conversation_sentiment(self, conversation_id: str, sentiment_score: float):
        """Update conversation sentiment score."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE conversations
                SET sentiment_score = $1
                WHERE id = $2
                """,
                sentiment_score, conversation_id
            )
    
    async def close_conversation(self, conversation_id: str, resolution_type: str):
        """Close a conversation."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE conversations
                SET status = 'closed', ended_at = NOW(), resolution_type = $1
                WHERE id = $2
                """,
                resolution_type, conversation_id
            )
    
    # =========================================================================
    # MESSAGE QUERIES
    # =========================================================================
    
    async def create_message(
        self,
        conversation_id: str,
        channel: str,
        direction: str,
        role: str,
        content: str,
        channel_message_id: str = None,
        metadata: Dict = None
    ) -> str:
        """Create a new message."""
        async with self.pool.acquire() as conn:
            message_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO messages (
                    id, conversation_id, channel, direction, role, content,
                    channel_message_id, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                message_id, conversation_id, channel, direction, role,
                content, channel_message_id, metadata
            )
            return str(message_id)
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a conversation."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                conversation_id, limit
            )
            return [dict(row) for row in rows]
    
    # =========================================================================
    # TICKET QUERIES
    # =========================================================================
    
    async def create_ticket(
        self,
        conversation_id: str,
        customer_id: str,
        source_channel: str,
        category: str = None,
        priority: str = 'medium'
    ) -> str:
        """Create a new support ticket."""
        async with self.pool.acquire() as conn:
            ticket_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO tickets (
                    id, conversation_id, customer_id, source_channel,
                    category, priority
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                ticket_id, conversation_id, customer_id, source_channel,
                category, priority
            )
            return str(ticket_id)
    
    async def update_ticket_status(self, ticket_id: str, status: str):
        """Update ticket status."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE tickets SET status = $1 WHERE id = $2",
                status, ticket_id
            )
    
    async def resolve_ticket(self, ticket_id: str, resolution_notes: str = None):
        """Mark ticket as resolved."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets
                SET status = 'resolved', resolved_at = NOW(), resolution_notes = $1
                WHERE id = $2
                """,
                resolution_notes, ticket_id
            )
    
    # =========================================================================
    # KNOWLEDGE BASE QUERIES (with vector search)
    # =========================================================================
    
    async def search_knowledge_base(
        self,
        query_embedding: List[float],
        max_results: int = 5,
        category: str = None
    ) -> List[Dict]:
        """Search knowledge base using vector similarity."""
        async with self.pool.acquire() as conn:
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
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
            
            return [dict(row) for row in rows]
    
    async def add_knowledge_entry(
        self,
        title: str,
        content: str,
        category: str,
        embedding: List[float],
        tags: List[str] = None
    ):
        """Add a new knowledge base entry."""
        async with self.pool.acquire() as conn:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            await conn.execute(
                """
                INSERT INTO knowledge_base (title, content, category, embedding, tags)
                VALUES ($1, $2, $3, $4::vector, $5)
                """,
                title, content, category, embedding_str, tags
            )
    
    # =========================================================================
    # ESCALATION QUERIES
    # =========================================================================
    
    async def create_escalation(
        self,
        ticket_id: str,
        conversation_id: str,
        reason_code: str,
        reason_detail: str = None
    ) -> str:
        """Create an escalation record."""
        async with self.pool.acquire() as conn:
            escalation_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO escalations (
                    id, ticket_id, conversation_id, reason_code, reason_detail
                )
                VALUES ($1, $2, $3, $4, $5)
                """,
                escalation_id, ticket_id, conversation_id, reason_code, reason_detail
            )
            return str(escalation_id)
    
    # =========================================================================
    # METRICS QUERIES
    # =========================================================================
    
    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        channel: str = None,
        dimensions: Dict = None
    ):
        """Record an agent metric."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO agent_metrics (metric_name, metric_value, channel, dimensions)
                VALUES ($1, $2, $3, $4)
                """,
                metric_name, metric_value, channel, dimensions
            )
    
    async def get_metrics(
        self,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
        channel: str = None
    ) -> List[Dict]:
        """Get metrics for a time period."""
        async with self.pool.acquire() as conn:
            if channel:
                rows = await conn.fetch(
                    """
                    SELECT * FROM agent_metrics
                    WHERE metric_name = $1 AND channel = $2
                    AND recorded_at BETWEEN $3 AND $4
                    ORDER BY recorded_at
                    """,
                    metric_name, channel, start_date, end_date
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM agent_metrics
                    WHERE metric_name = $1
                    AND recorded_at BETWEEN $2 AND $3
                    ORDER BY recorded_at
                    """,
                    metric_name, start_date, end_date
                )
            
            return [dict(row) for row in rows]
```

---

## Environment Variables

```bash
# .env

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/customer_success_fte
DB_HOST=localhost
DB_PORT=5432
DB_NAME=customer_success_fte
DB_USER=app_user
DB_PASSWORD=your_secure_password

# Connection Pool Settings
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30
```

---

## Docker Compose for Local Development

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: crm_postgres
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: customer_success_fte
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d customer_success_fte"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    container_name: crm_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@techcorp.com
      PGADMIN_DEFAULT_PASSWORD: admin_password
    ports:
      - "8080:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

---

## Testing

```python
# tests/test_database.py

import pytest
import asyncio
from database.queries import DatabaseQueries

@pytest.fixture
async def db():
    """Create test database connection."""
    db = DatabaseQueries("postgresql://app_user:password@localhost:5432/customer_success_fte_test")
    await db.create_pool()
    yield db
    await db.close_pool()

class TestCustomerQueries:
    @pytest.mark.asyncio
    async def test_get_or_create_customer(self, db):
        customer = await db.get_or_create_customer(email="test@example.com")
        
        assert customer['email'] == "test@example.com"
        assert 'id' in customer
        
        # Should return same customer on second call
        customer2 = await db.get_or_create_customer(email="test@example.com")
        assert customer2['id'] == customer['id']
    
    @pytest.mark.asyncio
    async def test_add_customer_identifier(self, db):
        customer = await db.get_or_create_customer(email="test@example.com")
        
        await db.add_customer_identifier(
            customer['id'],
            'phone',
            '+1234567890'
        )
        
        # Verify identifier was added
        # (Add query to verify)

class TestConversationQueries:
    @pytest.mark.asyncio
    async def test_create_conversation(self, db):
        customer = await db.get_or_create_customer(email="test@example.com")
        
        conversation_id = await db.create_conversation(
            customer['id'],
            'email'
        )
        
        assert conversation_id is not None
    
    @pytest.mark.asyncio
    async def test_get_conversation_messages(self, db):
        customer = await db.get_or_create_customer(email="test@example.com")
        conversation_id = await db.create_conversation(customer['id'], 'email')
        
        # Add messages
        await db.create_message(
            conversation_id,
            'email',
            'inbound',
            'customer',
            "Hello, I need help"
        )
        
        messages = await db.get_conversation_messages(conversation_id)
        assert len(messages) >= 1

class TestKnowledgeBaseQueries:
    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, db):
        # Add test entry
        embedding = [0.1] * 1536  # Mock embedding
        await db.add_knowledge_entry(
            title="How to reset password",
            content="To reset your password, go to settings...",
            category="how-to",
            embedding=embedding
        )
        
        # Search
        results = await db.search_knowledge_base(
            query_embedding=embedding,
            max_results=5,
            category="how-to"
        )
        
        assert len(results) >= 1
        assert 'similarity' in results[0]
```

---

## Acceptance Criteria

- [ ] All tables created with proper constraints
- [ ] pgvector extension enabled and working
- [ ] Customer lookup works across channels
- [ ] Conversation tracking with messages
- [ ] Ticket lifecycle management
- [ ] Vector similarity search returns relevant results
- [ ] Indexes created for performance
- [ ] Database functions tested
- [ ] Connection pooling configured
- [ ] Migrations supported

## Related Skills

- `customer-success-agent` - Uses database for state management
- `kafka-event-processing` - Events from database changes
- `channel-integrations` - Stores messages in database
- `sentiment-analysis` - Stores sentiment scores

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)
