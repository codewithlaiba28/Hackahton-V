import asyncio
import asyncpg

async def check_schema():
    dsn = "postgresql://neondb_owner:npg_0JgcEZMayS3P@ep-round-sea-amv1w9z4-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    try:
        conn = await asyncpg.connect(dsn)
        rows = await conn.fetch("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
        count = rows[0][0]
        print(f"Total tables in Neon DB public schema: {count}")
        
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = [r['table_name'] for r in rows]
        print(f"Tables: {tables}")
        await conn.close()
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
