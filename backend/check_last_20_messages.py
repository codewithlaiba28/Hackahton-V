import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def check_messages():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("\n--- Last 20 Messages ---")
    cur.execute("""
        SELECT id, channel, direction, role, content, created_at, delivery_status
        FROM messages
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    rows = cur.fetchall()
    for r in rows:
        print(f"ID: {r[0]} | Channel: {r[1]} | Dir: {r[2]} | Role: {r[3]} | Status: {r[6]} | Time: {r[5]}")
        print(f"Content: {r[4][:100]}...")
        print("-" * 50)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_messages()
