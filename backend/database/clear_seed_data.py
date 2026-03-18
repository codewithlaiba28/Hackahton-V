"""
Clear Seed Data Script for Customer Success FTE.

This script removes all mock/demo customer data (tickets, messages, conversations, metrics)
to prepare the database for real production use, while keeping the Knowledge Base intact.

Usage:
    python database/clear_seed_data.py
"""

import asyncio
import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fte_user:password@localhost:5432/fte_db")

async def clear_data():
    """Clear all customer-related seed data."""
    print("=" * 60)
    print("WARNING: Customer Data Clearance")
    print("=" * 60)
    print("This will delete all Tickets, Messages, Conversations, Customers, and Metrics.")
    print("The Knowledge Base will NOT be deleted.")
    
    response = input("\nAre you sure you want to proceed? Type 'YES' to confirm: ")
    
    if response != 'YES':
        print("Aborted.")
        return

    print(f"\nConnecting to database: {DATABASE_URL}")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        async with conn.transaction():
            print("Deleting metrics...")
            await conn.execute("TRUNCATE TABLE agent_metrics CASCADE")
            
            print("Deleting tickets...")
            await conn.execute("TRUNCATE TABLE tickets CASCADE")
            
            print("Deleting messages...")
            await conn.execute("TRUNCATE TABLE messages CASCADE")
            
            print("Deleting conversations...")
            await conn.execute("TRUNCATE TABLE conversations CASCADE")
            
            print("Deleting customers and identifiers...")
            await conn.execute("TRUNCATE TABLE customer_identifiers CASCADE")
            await conn.execute("TRUNCATE TABLE customers CASCADE")
            
        print("\n[SUCCESS] All mock customer data has been cleared.")
        print("Your FTE is now ready for real production traffic.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to clear data: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(clear_data())
