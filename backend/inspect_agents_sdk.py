import os
from dotenv import load_dotenv
load_dotenv('c:/Code-journy/Quator-4/Hackahton-V/backend/.env')

from agents.models.openai_provider import OpenAIProvider
import inspect

def inspect_provider():
    provider = OpenAIProvider(
        use_responses=False,
        base_url="https://api.cerebras.ai/v1"
    )
    model = provider.get_model("llama3.1-8b")
    print("Model attributes:")
    for attr in dir(model):
        if not attr.startswith('__'):
            try:
                val = getattr(model, attr)
                print(f"  {attr}: {val}")
            except Exception:
                print(f"  {attr}: [Error accessing]")

if __name__ == "__main__":
    inspect_provider()
