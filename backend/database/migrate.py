"""
Database migration runner for Phase 2.

Usage:
    python database/migrate.py
"""

import asyncio
import asyncpg
import os
from pathlib import Path
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fte_user:password@localhost:5432/fte_db")


async def create_migrations_table(conn):
    """Create migrations tracking table."""
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    print("✓ Created _migrations table")


async def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    rows = await conn.fetch("SELECT migration_name FROM _migrations ORDER BY id")
    return {row['migration_name'] for row in rows}


async def apply_migration(conn, migration_name: str, sql: str):
    """Apply a single migration."""
    async with conn.transaction():
        await conn.execute(sql)
        await conn.execute(
            "INSERT INTO _migrations (migration_name) VALUES ($1)",
            migration_name
        )
    print(f"✓ Applied migration: {migration_name}")


async def run_migrations():
    """Run all pending migrations."""
    print(f"Connecting to database: {DATABASE_URL}")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await create_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        
        # Find all migration files
        migrations_dir = Path(__file__).parent / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))
        
        if not migration_files:
            print("⚠ No migration files found in database/migrations/")
            return
        
        # Apply pending migrations
        for migration_file in migration_files:
            migration_name = migration_file.stem
            
            if migration_name in applied:
                print(f"⊘ Skipping already applied: {migration_name}")
                continue
            
            print(f"\nApplying migration: {migration_name}")
            sql = migration_file.read_text()
            await apply_migration(conn, migration_name, sql)
        
        print("\n✅ All migrations applied successfully")
        
    finally:
        await conn.close()


async def verify_schema():
    """Verify all tables were created."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        table_names = [row['table_name'] for row in tables]
        expected_tables = {
            'customers',
            'customer_identifiers',
            'conversations',
            'messages',
            'tickets',
            'knowledge_base',
            'channel_configs',
            'agent_metrics',
            '_migrations'
        }
        
        print(f"\n📊 Database Tables ({len(table_names)}):")
        for table in sorted(table_names):
            status = "✓" if table in expected_tables or table == '_migrations' else "⚠"
            print(f"  {status} {table}")
        
        missing = expected_tables - set(table_names)
        if missing:
            print(f"\n⚠ Missing tables: {missing}")
        else:
            print("\n✅ All expected tables present")
        
    finally:
        await conn.close()


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Phase 2 Database Migration Runner")
    print("=" * 60)
    
    await run_migrations()
    await verify_schema()


if __name__ == "__main__":
    asyncio.run(main())
