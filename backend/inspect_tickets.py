import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_columns():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    rows = await conn.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'tickets'
    """)
    for row in rows:
        print(f"{row['column_name']}: {row['data_type']}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_columns())
