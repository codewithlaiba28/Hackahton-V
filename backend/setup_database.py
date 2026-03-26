"""
Database Setup Script

Creates database, user, and schema for Customer Success FTE.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL', 'postgresql://fte_user:password@localhost:5432/fte_db')

# Extract components
# postgresql://user:password@host:port/database
from urllib.parse import urlparse

parsed = urlparse(db_url)
db_name = parsed.path.lstrip('/')
db_user = parsed.username
db_password = parsed.password
db_host = parsed.hostname or 'localhost'
db_port = parsed.port or 5432

print("=" * 70)
print("🗄️  DATABASE SETUP")
print("=" * 70)
print()
print(f"Database: {db_name}")
print(f"User: {db_user}")
print(f"Host: {db_host}:{db_port}")
print()

# Try to connect with default postgres user
print("Attempting to connect to PostgreSQL...")

# First try with postgres user (default superuser)
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Connect to default postgres database
    print("Connecting to PostgreSQL as 'postgres' user...")
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user='postgres',
        password='postgres',  # Default password, change if different
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("✅ Connected to PostgreSQL")
    
    # Create database
    print(f"Creating database '{db_name}'...")
    try:
        cur.execute(f"CREATE DATABASE {db_name};")
        print(f"✅ Database '{db_name}' created")
    except psycopg2.errors.DuplicateDatabase:
        print(f"⚠️  Database '{db_name}' already exists")
    
    # Create user
    print(f"Creating user '{db_user}'...")
    try:
        cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
        print(f"✅ User '{db_user}' created")
    except psycopg2.errors.DuplicateObject:
        print(f"⚠️  User '{db_user}' already exists")
        # Update password
        cur.execute(f"ALTER USER {db_user} WITH PASSWORD '{db_password}';")
        print(f"✅ User '{db_user}' password updated")
    
    # Grant privileges
    print(f"Granting privileges to '{db_user}'...")
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    print("✅ Privileges granted")
    
    cur.close()
    conn.close()
    
    # Now connect to the new database and create schema
    print()
    print(f"Connecting to database '{db_name}'...")
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("✅ Connected to database")
    
    # Create schema
    print("Creating schema...")
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        try:
            cur.execute(schema_sql)
            print("✅ Schema created successfully")
        except Exception as e:
            print(f"⚠️  Schema creation error (may already exist): {e}")
    
    # Verify tables
    print()
    print("Verifying tables...")
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    cur.close()
    conn.close()
    
    print()
    print("=" * 70)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("You can now run the application:")
    print("  python -m uvicorn api.main:app --reload")
    print()
    
except ImportError:
    print("❌ psycopg2 not installed")
    print()
    print("Install with:")
    print("  pip install psycopg2-binary")
    print()
except Exception as e:
    print(f"❌ Setup failed: {e}")
    print()
    print("TROUBLESHOOTING:")
    print("1. Ensure PostgreSQL is running")
    print("2. Check if postgres user password is 'postgres'")
    print("3. Try manual setup:")
    print(f"   psql -U postgres -c \"CREATE DATABASE {db_name};\"")
    print(f"   psql -U postgres -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\"")
    print(f"   psql -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};\"")
    print()
