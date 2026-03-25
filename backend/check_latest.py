import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def check_messages():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT channel, direction, role, delivery_status, content
        FROM messages
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    rows = cur.fetchall()
    for r in rows:
        print(f"[{r[0].upper()}] {r[1]} ({r[2]}) - Status: {r[3]}")
        content = r[4].replace('\n', ' ')
        print(f"Content: {content[:100]}...\n")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_messages()
