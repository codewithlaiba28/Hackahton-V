import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    dsn = os.getenv('DATABASE_URL')
    if not dsn:
        print("DATABASE_URL not found in .env")
        return
    try:
        conn = await asyncpg.connect(dsn)
        tables = ['customers', 'conversations', 'messages', 'tickets']
        for t in tables:
            count = await conn.fetchval(f"SELECT count(*) FROM {t}")
            print(f"Table {t}: {count} rows")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
