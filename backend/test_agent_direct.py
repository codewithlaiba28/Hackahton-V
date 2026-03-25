import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

print(f"ROOT ENV CEREBRAS: {os.getenv('CEREBRAS_API_KEY')[:10] if os.getenv('CEREBRAS_API_KEY') else 'None'}")

from agent.customer_success_agent import run_agent, customer_success_agent

async def test():
    print("Running customer success agent test...")
    result = await run_agent(
        message="Hello I need support with my project.",
        context={"customer_id": "test-123", "conversation_id": "conv-123", "channel": "whatsapp"}
    )
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test())
