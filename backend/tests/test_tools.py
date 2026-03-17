"""
Agent tool tests for Phase 2.

Tests all 5 @function_tool functions.
"""

import pytest
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
    KnowledgeSearchInput,
    TicketInput,
    CustomerHistoryInput,
    EscalationInput,
    ResponseInput,
    Channel,
)


@pytest.mark.asyncio
async def test_search_knowledge_base_valid_query():
    """Test: search_knowledge_base with valid query → returns results."""
    input = KnowledgeSearchInput(query="API key reset", max_results=5)
    result = await search_knowledge_base(input)
    
    # Should return formatted results or "not found" message
    assert result is not None
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_search_knowledge_base_empty_query():
    """Test: search_knowledge_base with empty query → raises ValidationError."""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        KnowledgeSearchInput(query="", max_results=5)


@pytest.mark.asyncio
async def test_create_ticket_valid_input():
    """Test: create_ticket with valid input → returns ticket ID."""
    input = TicketInput(
        customer_id="test_customer_123",
        issue="Cannot access my account - need help urgently",
        priority="high",
        category="technical",
        channel=Channel.EMAIL
    )
    result = await create_ticket(input)
    
    # Should return confirmation string with ticket ID
    assert result is not None
    assert isinstance(result, str)
    assert "Ticket" in result


@pytest.mark.asyncio
async def test_get_customer_history_new_customer():
    """Test: get_customer_history for new customer → returns 'no history' message."""
    input = CustomerHistoryInput(customer_id="new_customer_xyz", limit=10)
    result = await get_customer_history(input)
    
    # Should return "no history" message
    assert result is not None
    assert "new customer" in result.lower() or "no prior" in result.lower()


@pytest.mark.asyncio
async def test_escalate_to_human_valid():
    """Test: escalate_to_human with valid input → returns escalation confirmation."""
    input = EscalationInput(
        ticket_id="ticket_test_123",
        reason="pricing_inquiry",
        urgency="normal",
        context="Customer asked about enterprise pricing"
    )
    result = await escalate_to_human(input)
    
    # Should return escalation confirmation
    assert result is not None
    assert isinstance(result, str)
    assert "Escalation" in result


@pytest.mark.asyncio
async def test_send_response_valid():
    """Test: send_response with valid input → returns delivery confirmation."""
    input = ResponseInput(
        ticket_id="ticket_test_456",
        message="Thank you for contacting support. Here's how to reset your API key...",
        channel=Channel.EMAIL,
        customer_email="test@example.com"
    )
    result = await send_response(input)
    
    # Should return delivery confirmation
    assert result is not None
    assert isinstance(result, str)
    assert "sent" in result.lower() or "delivered" in result.lower()


@pytest.mark.asyncio
async def test_channel_enum_values():
    """Test: Channel enum has all required values."""
    assert Channel.EMAIL.value == "email"
    assert Channel.WHATSAPP.value == "whatsapp"
    assert Channel.WEB_FORM.value == "web_form"


@pytest.mark.asyncio
async def test_ticket_input_validation():
    """Test: TicketInput validates required fields."""
    from pydantic import ValidationError
    
    # Should fail with short issue
    with pytest.raises(ValidationError):
        TicketInput(
            customer_id="test",
            issue="Short",  # Too short (< 10 chars)
            channel=Channel.EMAIL
        )
    
    # Should pass with valid input
    input = TicketInput(
        customer_id="test",
        issue="This is a valid issue description",
        channel=Channel.EMAIL
    )
    assert input is not None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
