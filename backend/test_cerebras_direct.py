import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv("CEREBRAS_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("CEREBRAS_MODEL")

print(f"Testing with: Key={api_key[:10]}..., URL={base_url}, Model={model}")

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "hi"}]
    )
    print("Success! Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Failed: {e}")
