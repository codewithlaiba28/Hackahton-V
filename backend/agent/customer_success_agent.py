"""OpenAI Agents SDK agent definition for Phase 2."""

from agents import Agent, Runner
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)
from agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT


import os
customer_success_agent = Agent(
    name="Customer Success FTE",
    model=os.getenv("CEREBRAS_MODEL", "llama3.1-8b"),
    instructions=CUSTOMER_SUCCESS_SYSTEM_PROMPT,
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response,
    ],
)


async def run_agent(message: str, context: dict) -> dict:
    """
    Run the agent with a message and context.
    
    Args:
        message: Customer message
        context: Context dict with customer_id, conversation_id, channel, etc.
    
    Returns:
        Agent result dict with response, tool_calls, etc.
    """
    import os
    from openai import AsyncOpenAI
    
    api_key = os.getenv("CEREBRAS_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") or "https://api.cerebras.ai/v1"
    
    # Custom client for Cerebras compatibility
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    result = await Runner.run(
        customer_success_agent,
        message,
        context=context,
        client=client
    )
    
    return {
        "output": result.final_output,
        "tool_calls": result.tool_calls,
        "usage": result.usage,
    }
