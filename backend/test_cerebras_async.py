import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def main():
    load_dotenv('backend/.env')
    api_key = os.getenv("CEREBRAS_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("CEREBRAS_MODEL")

    print(f"Testing Async with: Key={api_key[:10]}..., URL={base_url}, Model={model}")

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "hi"}]
        )
        print("Async Success! Response:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Async Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
