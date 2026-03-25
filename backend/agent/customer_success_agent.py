import os
from dotenv import load_dotenv

# Load env vars first
load_dotenv('.env')

from agents import Agent, Runner
from agents.models.openai_provider import OpenAIProvider
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)
from agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

# Initialize the provider with forced settings
c_key = os.getenv("CEREBRAS_API_KEY")
c_url = "https://api.cerebras.ai/v1"

print(f"DEBUG: Initializing OpenAIProvider with URL: {c_url}")
print(f"DEBUG: Key provided: {c_key[:5]}...{c_key[-5:] if c_key else 'None'}")

provider = OpenAIProvider(
    use_responses=False,
    api_key=c_key,
    base_url=c_url
)
model_instance = provider.get_model(os.getenv("CEREBRAS_MODEL", "llama3.1-8b"))

# Define the agent
customer_success_agent = Agent(
    name="Customer Success FTE",
    model=model_instance,
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
        customer_success_agent,
        message,
        context=context
    )
    
    return {
        "output": result.final_output,
        "tool_calls": result.tool_calls,
        "usage": result.usage,
    }
