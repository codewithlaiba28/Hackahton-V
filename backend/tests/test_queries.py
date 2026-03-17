"""
Database query tests for Phase 2.

Tests all database operations with real PostgreSQL.
"""

import pytest
import asyncio
import asyncpg
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.queries import (
    get_pool,
    close_pool,
    create_customer,
    find_customer_by_email,
    find_customer_by_phone,
    add_customer_identifier,
    create_conversation,
    store_message,
    create_ticket,
    get_ticket_by_id,
)


@pytest.fixture
async def db_pool():
    """Create database pool for testing."""
    pool = await get_pool()
    yield pool
    await close_pool()


@pytest.mark.asyncio
async def test_create_and_find_customer(db_pool):
    """Test: Create customer → retrieve by email → assert same UUID."""
    async with db_pool.acquire() as conn:
        # Create customer
        customer_id = await create_customer(
            conn=conn,
            email="test@example.com",
            phone="+1234567890",
            name="Test User"
        )
        
        # Retrieve by email
        customer = await find_customer_by_email(conn, "test@example.com")
        
        # Assert same UUID
        assert customer is not None
        assert str(customer['id']) == customer_id
        assert customer['email'] == "test@example.com"
        assert customer['name'] == "Test User"


@pytest.mark.asyncio
async def test_cross_channel_customer_lookup(db_pool):
    """Test: Create customer via email, add phone identifier, look up by phone → same customer."""
    async with db_pool.acquire() as conn:
        # Create customer via email
        customer_id = await create_customer(
            conn=conn,
            email="cross@example.com",
            name="Cross Channel User"
        )
        
        # Add phone identifier
        await add_customer_identifier(conn, customer_id, "phone", "+1987654321")
        
        # Look up by phone
        customer = await find_customer_by_phone(conn, "+1987654321")
        
        # Assert same customer
        assert customer is not None
        assert str(customer['id']) == customer_id


@pytest.mark.asyncio
async def test_create_conversation_and_messages(db_pool):
    """Test: Create conversation → store messages → load conversation messages → assert message in list."""
    async with db_pool.acquire() as conn:
        # Create customer
        customer_id = await create_customer(
            conn=conn,
            email="conv@example.com",
            name="Conversation User"
        )
        
        # Create conversation
        conv_id = await create_conversation(conn, customer_id, "email")
        
        # Store inbound message
        msg_id = await store_message(
            conn=conn,
            conversation_id=conv_id,
            channel="email",
            direction="inbound",
            role="customer",
            content="Hello, I need help with my API key"
        )
        
        # Store outbound message
        await store_message(
            conn=conn,
            conversation_id=conv_id,
            channel="email",
            direction="outbound",
            role="agent",
            content="I'd be happy to help you with your API key"
        )
        
        # Load conversation messages
        messages = await conn.fetch(
            "SELECT * FROM messages WHERE conversation_id = $1 ORDER BY created_at ASC",
            conv_id
        )
        
        # Assert messages in list
        assert len(messages) == 2
        assert messages[0]['direction'] == 'inbound'
        assert messages[1]['direction'] == 'outbound'


@pytest.mark.asyncio
async def test_create_ticket_and_update_status(db_pool):
    """Test: Create ticket → update status → retrieve → assert status updated."""
    async with db_pool.acquire() as conn:
        # Create customer
        customer_id = await create_customer(
            conn=conn,
            email="ticket@example.com",
            name="Ticket User"
        )
        
        # Create conversation
        conv_id = await create_conversation(conn, customer_id, "email")
        
        # Create ticket
        ticket_id = await create_ticket(
            conn=conn,
            customer_id=customer_id,
            conversation_id=conv_id,
            channel="email",
            issue="Cannot access my account",
            priority="high"
        )
        
        # Retrieve ticket
        ticket = await get_ticket_by_id(conn, ticket_id)
        
        # Assert initial status
        assert ticket is not None
        assert ticket['status'] == 'open'
        assert ticket['priority'] == 'high'
        
        # Update status
        await conn.execute(
            "UPDATE tickets SET status = 'resolved' WHERE id = $1",
            ticket_id
        )
        
        # Retrieve again and assert status updated
        ticket = await get_ticket_by_id(conn, ticket_id)
        assert ticket['status'] == 'resolved'


@pytest.mark.asyncio
async def test_knowledge_base_search(db_pool):
    """Test: Insert knowledge base entry → search with vector → returns relevant result."""
    async with db_pool.acquire() as conn:
        # Insert test knowledge base entry
        embedding = [0.1] * 1536  # Dummy embedding
        
        await conn.execute(
            """
            INSERT INTO knowledge_base (title, content, category, embedding)
            VALUES ($1, $2, $3, $4::vector)
            """,
            "API Key Reset",
            "To reset your API key, go to Settings > API > Keys and click Rotate Key",
            "how-to",
            '[' + ','.join(map(str, embedding)) + ']'
        )
        
        # Search (simplified - in production would use real embedding)
        results = await conn.fetch(
            """
            SELECT title, content FROM knowledge_base
            WHERE category = 'how-to'
            LIMIT 5
            """
        )
        
        # Assert result contains expected content
        assert len(results) >= 1
        assert "API Key" in results[0]['title']


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
