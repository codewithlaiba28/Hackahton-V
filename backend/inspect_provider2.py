import asyncio
from agent.customer_success_agent import provider, model_instance

print("Provider DIRS:", [d for d in dir(provider) if not d.startswith('__')])
print("Model DIRS:", [d for d in dir(model_instance) if not d.startswith('__')])

if hasattr(model_instance, 'client'):
    print("Model API Key:", model_instance.client.api_key[:5] if model_instance.client.api_key else None)
    print("Model Base URL:", model_instance.client.base_url)
    
    # Let's try to override it directly and run test:
    model_instance.client.base_url = "https://api.cerebras.ai/v1/"
    print("Re-assigned Base URL to:", model_instance.client.base_url)
