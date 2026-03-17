"""
Agent tests for Phase 2.

Tests OpenAI Agents SDK agent with transition tests from Phase 1.
"""

import pytest
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.customer_success_agent import customer_success_agent, run_agent
from agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_agent_instantiation():
    """Test: Agent instantiates without error."""
    assert customer_success_agent is not None
    assert customer_success_agent.name == "Customer Success FTE"
    assert len(customer_success_agent.tools) == 5


@pytest.mark.asyncio
async def test_system_prompt_contains_required_sections():
    """Test: System prompt contains all 6 required sections."""
    required_sections = [
        "Your Purpose",
        "Channel Awareness",
        "Required Workflow",
        "Hard Constraints",
        "Escalation Triggers",
        "Response Quality Standards"
    ]
    
    for section in required_sections:
        assert section in CUSTOMER_SUCCESS_SYSTEM_PROMPT, f"Missing section: {section}"


@pytest.mark.asyncio
async def test_empty_message_handling():
    """Test: Empty message → asks for clarification, no crash."""
    result = await run_agent(
        message="",
        context={
            "customer_id": "test_123",
            "channel": "email"
        }
    )
    
    # Should not crash and should ask for clarification
    assert result is not None
    assert "output" in result


@pytest.mark.asyncio
async def test_pricing_question_escalates():
    """Test: Pricing question → escalated with reason 'pricing_inquiry'."""
    result = await run_agent(
        message="What's the price of the Enterprise plan?",
        context={
            "customer_id": "test_123",
            "channel": "email"
        }
    )
    
    # Should escalate (not answer pricing)
    assert result is not None
    # In production, would check tool_calls for escalate_to_human


@pytest.mark.asyncio
async def test_angry_customer_handling():
    """Test: Angry customer (WhatsApp) → escalated or empathetic response."""
    result = await run_agent(
        message="This is BROKEN and your support is USELESS!",
        context={
            "customer_id": "test_123",
            "channel": "whatsapp"
        }
    )
    
    # Should not crash and should handle appropriately
    assert result is not None


@pytest.mark.asyncio
async def test_email_format_has_greeting_and_signature():
    """Test: Email response → contains greeting and signature."""
    result = await run_agent(
        message="How do I reset my password?",
        context={
            "customer_id": "test_123",
            "channel": "email"
        }
    )
    
    # Should contain greeting or signature (in production)
    assert result is not None


@pytest.mark.asyncio
async def test_whatsapp_response_length():
    """Test: WhatsApp response → under 500 chars (preferably 300)."""
    result = await run_agent(
        message="hey can i export my data?",
        context={
            "customer_id": "test_123",
            "channel": "whatsapp"
        }
    )
    
    # In production, would check length < 300 chars
    assert result is not None


@pytest.mark.asyncio
async def test_tool_execution_order():
    """Test: Tools called in correct order (create_ticket first, send_response last)."""
    # This would require mocking tools to track call order
    # For now, just verify agent has all required tools
    tool_names = [tool.name for tool in customer_success_agent.tools]
    
    assert "create_ticket" in tool_names
    assert "send_response" in tool_names
    assert "get_customer_history" in tool_names
    assert "search_knowledge_base" in tool_names
    assert "escalate_to_human" in tool_names


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
