import asyncio
from agent.customer_success_agent import provider, c_key, c_url

print("Provider API Key:", provider.client.api_key[:5] if provider.client.api_key else None)
print("Provider Base URL:", provider.client.base_url)

