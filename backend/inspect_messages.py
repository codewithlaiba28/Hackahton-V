import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def inspect_columns():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("\n--- Columns in 'messages' ---")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'messages'
    """)
    
    rows = cur.fetchall()
    for r in rows:
        print(f"{r[0]} ({r[1]})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_columns()
