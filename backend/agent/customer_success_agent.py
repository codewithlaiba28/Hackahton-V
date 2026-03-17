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


# Define production agent
customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
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
    result = await Runner.run(
        agent=customer_success_agent,
        input=message,
        context=context,
    )
    
    return {
        "output": result.output,
        "tool_calls": result.tool_calls,
        "usage": result.usage,
    }
