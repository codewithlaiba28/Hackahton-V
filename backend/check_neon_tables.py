import asyncio
import asyncpg

async def check_schema():
    dsn = "postgresql://neondb_owner:npg_0JgcEZMayS3P@ep-round-sea-amv1w9z4-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    try:
        conn = await asyncpg.connect(dsn)
        print("Checking tables in Neon DB...")
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [r['table_name'] for r in rows]
        print(f"Tables found: {tables}")
        await conn.close()
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
