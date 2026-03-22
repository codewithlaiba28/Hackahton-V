import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    dsn = os.getenv('DATABASE_URL')
    try:
        conn = await asyncpg.connect(dsn)
        rows = await conn.fetch('SELECT channel_message_id, direction, role, content FROM messages')
        print(f"Total messages in DB: {len(rows)}")
        for r in rows:
            print(f"- ID: {r['channel_message_id']} | Dir: {r['direction']} | Role: {r['role']} | Content: {r['content'][:100]}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
