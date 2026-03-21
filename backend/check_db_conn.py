import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    dsn = os.getenv("DATABASE_URL")
    print(f"Checking connection to: {dsn}")
    try:
        conn = await asyncpg.connect(dsn)
        print("SUCCESS: Connected to PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"FAILURE: Could not connect to DB: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
