"""
Database access layer for Phase 2.

All queries use asyncpg and are organized by domain.
All functions take a conn parameter (connection from pool).
"""

import asyncpg
import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# =============================================================================
# CONNECTION POOL
# =============================================================================

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> Any:
    """Get or create connection pool (with mock fallback)."""
    global _pool
    if os.getenv("DATABASE_URL") == "mock":
        class MockCursor:
            def __init__(self):
                self.row = {'id': 'mock-customer-id', 'email': 'mock@test.com', 'name': 'Mock User'}
            
            async def fetchrow(self, *args, **kwargs):
                return self.row
            
            async def fetch(self, *args, **kwargs):
                return [self.row]
            
            async def execute(self, *args, **kwargs):
                return 'mock-execution'
        
        class MockConn:
            async def __aenter__(self): 
                self.cursor = MockCursor()
                return self
            async def __aexit__(self, *args): 
                pass
            async def fetchrow(self, *args, **kwargs): 
                return self.cursor.row
            async def fetch(self, *args, **kwargs): 
                return [self.cursor.row]
            async def execute(self, *args, **kwargs):
                return 'mock-execution'

        class MockPool:
            def acquire(self):
                return MockConn()
            async def close(self): 
                pass
        return MockPool()

    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                dsn=os.getenv("DATABASE_URL"),
                min_size=2,
                max_size=20,
                command_timeout=30,
            )
        except Exception as e:
            print(f"FAILED to connect to DB: {e}. Falling back to MOCK mode.")
            os.environ["DATABASE_URL"] = "mock"
            return await get_pool()
    return _pool


async def close_pool():
    """Close connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# =============================================================================
# CUSTOMER QUERIES
# =============================================================================

async def find_customer_by_email(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    """Find customer by email address."""
    row = await conn.fetchrow(
        "SELECT * FROM customers WHERE email = $1",
        email
    )
    return dict(row) if row else None


async def find_customer_by_phone(conn: asyncpg.Connection, phone: str) -> Optional[Dict[str, Any]]:
    """Find customer by phone number."""
    row = await conn.fetchrow(
        "SELECT * FROM customers WHERE phone = $1",
        phone
    )
    return dict(row) if row else None


async def create_customer(
    conn: asyncpg.Connection,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """Create a new customer. Returns UUID as string."""
    row = await conn.fetchrow(
        """
        INSERT INTO customers (email, phone, name)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        email, phone, name
    )
    return str(row['id'])


async def get_customer_with_history(
    conn: asyncpg.Connection,
    customer_id: str
) -> Optional[Dict[str, Any]]:
    """Get customer with basic stats."""
    row = await conn.fetchrow(
        """
        SELECT 
            c.*,
            COUNT(DISTINCT conv.id) as total_conversations,
            COUNT(DISTINCT t.id) as total_tickets
        FROM customers c
        LEFT JOIN conversations conv ON c.id = conv.customer_id
        LEFT JOIN tickets t ON c.id = t.customer_id
        WHERE c.id = $1
        GROUP BY c.id
        """,
        customer_id
    )
    return dict(row) if row else None


async def add_customer_identifier(
    conn: asyncpg.Connection,
    customer_id: str,
    identifier_type: str,
    identifier_value: str
) -> None:
    """Add a customer identifier (for cross-channel mapping)."""
    await conn.execute(
        """
        INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value)
        VALUES ($1, $2, $3)
        ON CONFLICT (identifier_type, identifier_value) DO NOTHING
        """,
        customer_id, identifier_type, identifier_value
    )


async def find_customer_by_identifier(
    conn: asyncpg.Connection,
    identifier_type: str,
    identifier_value: str
) -> Optional[Dict[str, Any]]:
    """Find customer by identifier type and value."""
    row = await conn.fetchrow(
        """
        SELECT c.*
        FROM customers c
        JOIN customer_identifiers ci ON c.id = ci.customer_id
        WHERE ci.identifier_type = $1 AND ci.identifier_value = $2
        """,
        identifier_type, identifier_value
    )
    return dict(row) if row else None


# =============================================================================
# CONVERSATION QUERIES
# =============================================================================

async def get_active_conversation(
    conn: asyncpg.Connection,
    customer_id: str,
    channel: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get active conversation for a customer."""
    if channel:
        row = await conn.fetchrow(
            """
            SELECT * FROM conversations
            WHERE customer_id = $1 
              AND initial_channel = $2
              AND status = 'active'
            ORDER BY started_at DESC
            LIMIT 1
            """,
            customer_id, channel
        )
    else:
        row = await conn.fetchrow(
            """
            SELECT * FROM conversations
            WHERE customer_id = $1 
              AND status = 'active'
            ORDER BY started_at DESC
            LIMIT 1
            """,
            customer_id
        )
    return dict(row) if row else None


async def create_conversation(
    conn: asyncpg.Connection,
    customer_id: str,
    channel: str
) -> str:
    """Create a new conversation."""
    row = await conn.fetchrow(
        """
        INSERT INTO conversations (customer_id, initial_channel)
        VALUES ($1, $2)
        RETURNING id
        """,
        customer_id, channel
    )
    return str(row['id'])


async def close_conversation(
    conn: asyncpg.Connection,
    conversation_id: str,
    resolution_type: str
) -> None:
    """Close a conversation."""
    await conn.execute(
        """
        UPDATE conversations
        SET status = 'closed',
            ended_at = NOW(),
            resolution_type = $2
        WHERE id = $1
        """,
        conversation_id, resolution_type
    )


async def update_conversation_sentiment(
    conn: asyncpg.Connection,
    conversation_id: str,
    score: float
) -> None:
    """Update conversation sentiment score."""
    await conn.execute(
        """
        UPDATE conversations
        SET sentiment_score = $2
        WHERE id = $1
        """,
        conversation_id, score
    )


# =============================================================================
# MESSAGE QUERIES
# =============================================================================

async def get_real_customers(
    conn: asyncpg.Connection,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get list of real customers with their stats."""
    rows = await conn.fetch(
        """
        SELECT 
            c.id, 
            c.name, 
            c.email, 
            c.phone, 
            COUNT(t.id) as total_tickets,
            MAX(t.created_at) as last_contact,
            AVG(conv.sentiment_score) as avg_sentiment
        FROM customers c
        LEFT JOIN tickets t ON c.id = t.customer_id
        LEFT JOIN conversations conv ON c.id = conv.customer_id
        GROUP BY c.id
        ORDER BY MAX(t.created_at) DESC NULLS LAST
        LIMIT $1
        """,
        limit
    )
    return [dict(row) for row in rows]

async def store_message(
    conn: asyncpg.Connection,
    conversation_id: str,
    channel: str,
    direction: str,
    role: str,
    content: str,
    channel_message_id: Optional[str] = None,
    tokens_used: Optional[int] = None,
    latency_ms: Optional[int] = None,
    tool_calls: Optional[List[Dict]] = None,
    sentiment_score: Optional[float] = None
) -> str:
    """Store a message in the database."""
    row = await conn.fetchrow(
        """
        INSERT INTO messages (
            conversation_id, channel, direction, role, content,
            channel_message_id, tokens_used, latency_ms, tool_calls,
            sentiment_score
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
        """,
        conversation_id, channel, direction, role, content,
        channel_message_id, tokens_used, latency_ms,
        str(tool_calls) if tool_calls else None,
        sentiment_score
    )
    return str(row['id'])


async def load_conversation_messages(
    conn: asyncpg.Connection,
    conversation_id: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Load messages for a conversation."""
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


# =============================================================================
# TICKET QUERIES
# =============================================================================

async def create_ticket(
    conn: asyncpg.Connection,
    customer_id: str,
    conversation_id: str,
    channel: str,
    issue: str,
    priority: str = "medium",
    category: Optional[str] = None
) -> str:
    """Create a support ticket."""
    import json
    metadata = json.dumps({"issue": issue})
    row = await conn.fetchrow(
        """
        INSERT INTO tickets (
            customer_id, conversation_id, source_channel,
            priority, category, metadata
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
        """,
        customer_id, conversation_id, channel, priority, category, metadata
    )
    return str(row['id'])


async def update_ticket_status(
    conn: asyncpg.Connection,
    ticket_id: str,
    status: str,
    notes: Optional[str] = None
) -> None:
    """Update ticket status."""
    if notes:
        await conn.execute(
            """
            UPDATE tickets
            SET status = $2,
                resolution_notes = $3,
                resolved_at = CASE WHEN $2 IN ('resolved', 'closed') THEN NOW() ELSE NULL END
            WHERE id = $1
            """,
            ticket_id, status, notes
        )
    else:
        await conn.execute(
            """
            UPDATE tickets
            SET status = $2,
                resolved_at = CASE WHEN $2 IN ('resolved', 'closed') THEN NOW() ELSE NULL END
            WHERE id = $1
            """,
            ticket_id, status
        )


async def get_ticket_by_id(
    conn: asyncpg.Connection,
    ticket_id: str
) -> Optional[Dict[str, Any]]:
    """Get ticket by ID."""
    row = await conn.fetchrow(
        "SELECT * FROM tickets WHERE id = $1",
        ticket_id
    )
    return dict(row) if row else None


async def get_ticket_with_messages(
    conn: asyncpg.Connection,
    ticket_id: str
) -> Optional[Dict[str, Any]]:
    """Get ticket with its messages."""
    ticket_row = await conn.fetchrow(
        "SELECT * FROM tickets WHERE id = $1",
        ticket_id
    )
    
    if not ticket_row:
        return None
    
    ticket = dict(ticket_row)
    
    # Get conversation messages
    messages = await conn.fetch(
        """
        SELECT m.* FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        WHERE c.id = (SELECT conversation_id FROM tickets WHERE id = $1)
        ORDER BY m.created_at ASC
        """,
        ticket_id
    )
    
    ticket['messages'] = [dict(m) for m in messages]
    return ticket


async def get_recent_tickets(
    conn: asyncpg.Connection,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get recent tickets."""
    rows = await conn.fetch(
        """
        SELECT 
            t.id, 
            t.source_channel as channel, 
            COALESCE(t.metadata->>'issue', 'No subject') as subject, 
            t.priority, 
            t.status, 
            t.created_at as time,
            c.email as customer,
            conv.sentiment_score as sentiment
        FROM tickets t
        LEFT JOIN customers c ON t.customer_id = c.id
        LEFT JOIN conversations conv ON t.conversation_id = conv.id
        ORDER BY t.created_at DESC
        LIMIT $1
        """,
        limit
    )
    return [dict(row) for row in rows]


# =============================================================================
# KNOWLEDGE BASE QUERIES
# =============================================================================

async def search_knowledge_base(
    conn: asyncpg.Connection,
    embedding: List[float],
    query: str,
    max_results: int = 5,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search knowledge base with vector similarity."""
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    
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


async def insert_knowledge_entry(
    conn: asyncpg.Connection,
    title: str,
    content: str,
    category: str,
    embedding: List[float],
    tags: Optional[List[str]] = None
) -> str:
    """Insert a knowledge base entry."""
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    
    row = await conn.fetchrow(
        """
        INSERT INTO knowledge_base (title, content, category, embedding, tags)
        VALUES ($1, $2, $3, $4::vector, $5)
        RETURNING id
        """,
        title, content, category, embedding_str, tags
    )
    return str(row['id'])


# =============================================================================
# METRICS QUERIES
# =============================================================================

async def record_metric(
    conn: asyncpg.Connection,
    metric_name: str,
    metric_value: float,
    channel: Optional[str] = None,
    dimensions: Optional[Dict[str, Any]] = None
) -> None:
    """Record a metric."""
    await conn.execute(
        """
        INSERT INTO agent_metrics (metric_name, metric_value, channel, dimensions)
        VALUES ($1, $2, $3, $4)
        """,
        metric_name, metric_value, channel, str(dimensions) if dimensions else None
    )


async def get_channel_metrics_last_24h(
    conn: asyncpg.Connection
) -> List[Dict[str, Any]]:
    """Get channel metrics for last 24 hours."""
    rows = await conn.fetch(
        """
        SELECT 
            channel,
            COUNT(*) as total_conversations,
            AVG(metric_value) FILTER (WHERE metric_name = 'sentiment_score') as avg_sentiment,
            COUNT(*) FILTER (WHERE metric_name = 'escalation') as escalations,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY metric_value) FILTER (WHERE metric_name = 'latency_ms') as p95_latency
        FROM agent_metrics
        WHERE recorded_at > NOW() - INTERVAL '24 hours'
        GROUP BY channel
        """,
    )
    return [dict(row) for row in rows]


async def get_advanced_metrics(
    conn: asyncpg.Connection
) -> Dict[str, Any]:
    """Get advanced metrics for analytics dashboard (weekly, categories, trends)."""
    # 1. Weekly Ticket Volume (last 7 days grouped by day name)
    weekly_rows = await conn.fetch(
        """
        SELECT 
            to_char(created_at, 'Dy') as day,
            COUNT(*) as tickets,
            COUNT(*) FILTER (WHERE status IN ('resolved', 'closed')) as resolved,
            COUNT(*) FILTER (WHERE status = 'escalated') as escalated
        FROM tickets
        WHERE created_at > NOW() - INTERVAL '7 days'
        GROUP BY to_char(created_at, 'Dy'), EXTRACT(ISODOW FROM created_at)
        ORDER BY EXTRACT(ISODOW FROM created_at)
        """
    )
    
    # 2. Top Categories
    category_rows = await conn.fetch(
        """
        SELECT 
            COALESCE(category, 'Uncategorized') as category,
            COUNT(*) as count
        FROM tickets
        GROUP BY COALESCE(category, 'Uncategorized')
        ORDER BY count DESC
        LIMIT 6
        """
    )
    
    total_tickets = sum(row['count'] for row in category_rows) if category_rows else 1
    categories_data = [
        {
            "category": row["category"],
            "count": row["count"],
            "pct": int((row["count"] / total_tickets) * 100)
        }
        for row in category_rows
    ]
    
    # 3. Sentiment Trend (last 4 weeks)
    # Simplified sentiment logic for real responses
    trend_rows = await conn.fetch(
        """
        SELECT 
            'Week ' || CEIL((EXTRACT(EPOCH FROM (NOW() - recorded_at)) / 604800)) as period,
            COUNT(*) FILTER (WHERE metric_value >= 0.6) * 100 / GREATEST(COUNT(*), 1) as positive,
            COUNT(*) FILTER (WHERE metric_value >= 0.3 AND metric_value < 0.6) * 100 / GREATEST(COUNT(*), 1) as neutral,
            COUNT(*) FILTER (WHERE metric_value < 0.3) * 100 / GREATEST(COUNT(*), 1) as negative
        FROM agent_metrics
        WHERE metric_name = 'sentiment_score' AND recorded_at > NOW() - INTERVAL '28 days'
        GROUP BY CEIL((EXTRACT(EPOCH FROM (NOW() - recorded_at)) / 604800))
        ORDER BY CEIL((EXTRACT(EPOCH FROM (NOW() - recorded_at)) / 604800)) DESC
        """
    )
    
    return {
        "weeklyData": [dict(r) for r in weekly_rows],
        "topCategories": categories_data,
        "sentimentTrend": [dict(r) for r in trend_rows]
    }

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def verify_schema() -> List[str]:
    """Verify all expected tables exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        return [row['table_name'] for row in rows]
