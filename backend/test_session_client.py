from agents import Session
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv("CEREBRAS_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

client = AsyncOpenAI(api_key=api_key, base_url=base_url)

try:
    with Session(client=client) as session:
        print("Session created with client!")
except Exception as e:
    print(f"Session with client failed: {e}")
