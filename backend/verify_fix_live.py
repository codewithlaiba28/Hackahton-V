import asyncio
import os
import httpx
import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Ensure we are in backend dir context
os.chdir('c:/Code-journy/Quator-4/Hackahton-V/backend')
load_dotenv('.env')

CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_URL = "https://api.cerebras.ai/v1"

# 1. Patch AsyncOpenAI.__init__ (Direct)
_orig_init = AsyncOpenAI.__init__
def _new_init(self, *args, **kwargs):
    kwargs['api_key'] = CEREBRAS_KEY
    kwargs['base_url'] = CEREBRAS_URL
    if 'http_client' in kwargs: del kwargs['http_client']
    _orig_init(self, *args, **kwargs)
AsyncOpenAI.__init__ = _new_init

# 2. Patch httpx (Ultimate Fallback)
_orig_request = httpx.AsyncClient.request
async def _patched_request(self, method, url, *args, **kwargs):
    u = str(url)
    if "api.openai.com" in u:
        u = u.replace("api.openai.com/v1", "api.cerebras.ai/v1")
        if 'headers' not in kwargs: kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f"Bearer {CEREBRAS_KEY}"
        print(f"DEBUG: Redirecting {method} to {u}")
    return await _orig_request(self, method, u, *args, **kwargs)
httpx.AsyncClient.request = _patched_request

from api.main import process_direct_message

async def test_reply():
    print("Testing WhatsApp reply flow with Cerebras...")
    print(f"Using key: {CEREBRAS_KEY[:10]}...")
    
    try:
        ticket_id, outbound = await process_direct_message(
            channel="whatsapp",
            content="Hello there! Please tell me your purpose and how you can help me.",
            customer_phone="+1234567890",
            customer_name="Test User"
        )
        print(f"SUCCESS!")
        print(f"Ticket ID: {ticket_id}")
        print(f"Agent Response: {outbound}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_reply())
