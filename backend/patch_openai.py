import os
import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv
import httpx

# Ensure env vars are loaded
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Force Cerebras settings globally
CEREBRAS_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_URL = "https://api.cerebras.ai/v1"

if CEREBRAS_KEY:
    os.environ["OPENAI_API_KEY"] = CEREBRAS_KEY
    os.environ["OPENAI_BASE_URL"] = CEREBRAS_URL
    openai.api_key = CEREBRAS_KEY
    openai.base_url = CEREBRAS_URL

    # Monkeypatch httpx to redirect ALL OpenAI calls to Cerebras
    original_request = httpx.AsyncClient.request
    async def patched_request(self, method, url, *args, **kwargs):
        url_str = str(url)
        if "api.openai.com" in url_str:
            url_str = url_str.replace("api.openai.com/v1", "api.cerebras.ai/v1")
            # Also ensure the key is the Cerebras one if it's missing or OpenAI
            if 'headers' in kwargs and 'Authorization' in kwargs['headers']:
                auth = kwargs['headers']['Authorization']
                if "Bearer" in auth and ("sk-" in auth or not CEREBRAS_KEY[:10] in auth):
                    kwargs['headers']['Authorization'] = f"Bearer {CEREBRAS_KEY}"
        return await original_request(self, method, url_str, *args, **kwargs)
    
    httpx.AsyncClient.request = patched_request
    
    # Also patch synchronous for good measure
    original_request_sync = httpx.Client.request
    def patched_request_sync(self, method, url, *args, **kwargs):
        url_str = str(url)
        if "api.openai.com" in url_str:
            url_str = url_str.replace("api.openai.com/v1", "api.cerebras.ai/v1")
            if 'headers' in kwargs and 'Authorization' in kwargs['headers']:
                kwargs['headers']['Authorization'] = f"Bearer {CEREBRAS_KEY}"
        return await original_request_sync(self, method, url_str, *args, **kwargs)
    
    httpx.Client.request = patched_request_sync

    print(f"Cerebras Global Redirect Active: {CEREBRAS_URL}")
else:
    print("WARNING: CEREBRAS_API_KEY not found in .env, skipping patch.")
