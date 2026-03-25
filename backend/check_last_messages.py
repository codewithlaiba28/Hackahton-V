import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def check_messages():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("\n--- Last 10 Messages ---")
    cur.execute("""
        SELECT m.id, c.channel, m.direction, m.role, m.content, m.created_at 
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        ORDER BY m.created_at DESC
        LIMIT 10
    """)
    
    rows = cur.fetchall()
    for r in rows:
        print(f"ID: {r[0]} | Channel: {r[1]} | Dir: {r[2]} | Role: {r[3]} | Time: {r[5]}")
        print(f"Content: {r[4][:100]}...")
        print("-" * 50)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_messages()
