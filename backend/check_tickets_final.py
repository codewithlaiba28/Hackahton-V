import asyncio
import asyncpg

async def check_tickets():
    dsn = "postgresql://neondb_owner:npg_0JgcEZMayS3P@ep-round-sea-amv1w9z4-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    try:
        conn = await asyncpg.connect(dsn)
        rows = await conn.fetch("SELECT count(*) FROM tickets")
        count = rows[0][0]
        print(f"Total tickets in Neon DB: {count}")
        
        if count > 0:
            rows = await conn.fetch("SELECT id, source_channel, status, issue FROM tickets ORDER BY created_at DESC LIMIT 5")
            for r in rows:
                print(f"Ticket: {r['id']} | Channel: {r['source_channel']} | Status: {r['status']} | Issue: {r['issue'][:30]}...")
        
        await conn.close()
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(check_tickets())
