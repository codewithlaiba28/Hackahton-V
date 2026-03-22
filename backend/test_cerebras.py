import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print("KEY LEN:", len(api_key) if api_key else 0)

async def main():
    client = AsyncOpenAI(api_key=api_key, base_url=os.getenv('OPENAI_BASE_URL', 'https://api.cerebras.ai/v1'))
    try:
        r = await client.models.list()
        for m in r.data:
            print("MODEL:", m.id)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
