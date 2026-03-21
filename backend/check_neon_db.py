import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    # Try Neon DB from frontend if available
    dsn = "postgresql://neondb_owner:npg_0JgcEZMayS3P@ep-round-sea-amv1w9z4-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    print(f"Checking connection to Neon DB: {dsn}")
    try:
        conn = await asyncpg.connect(dsn)
        print("SUCCESS: Connected to Neon PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"FAILURE: Could not connect to Neon DB: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
