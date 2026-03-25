import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

# Intercept HTTPX requests
_orig_send = httpx.AsyncClient.send

async def intercepted_send(self, request: httpx.Request, *args, **kwargs):
    print(f"\n[INTERCEPT] {request.method} {request.url}")
    print(f"[INTERCEPT] Headers:")
    for k, v in request.headers.items():
        if k.lower() == 'authorization':
            print(f"  {k}: {v[:15]}...{v[-5:]}")
        else:
            print(f"  {k}: {v}")
    
    body = request.content.decode() if hasattr(request, 'content') and request.content else ""
    print(f"[INTERCEPT] Body: {body[:100]}...")
    
    response = await _orig_send(self, request, *args, **kwargs)
    print(f"[INTERCEPT] Response: {response.status_code}")
    print(f"[INTERCEPT] Response Text: {response.text[:200]}...")
    return response

httpx.AsyncClient.send = intercepted_send

from agent.customer_success_agent import run_agent

async def test():
    print("Running customer success agent test...")
    try:
        result = await run_agent(
            message="Hello I need support with my project.",
            context={"customer_id": "test-123", "conversation_id": "conv-123", "channel": "whatsapp"}
        )
        print("Result:", result)
    except Exception as e:
        print("Exception:", str(e))

if __name__ == "__main__":
    asyncio.run(test())
