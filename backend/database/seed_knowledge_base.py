"""
Seed knowledge base from product-docs.md.

Usage:
    python database/seed_knowledge_base.py
"""

import asyncio
import asyncpg
import os
import re
from pathlib import Path
from typing import List, Tuple

# OpenAI for embeddings (you can use any embedding service)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fte_user:password@localhost:5432/fte_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def parse_markdown_sections(content: str) -> List[Tuple[str, str]]:
    """Parse markdown content into sections by ## headings."""
    sections = []
    current_heading = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_heading and current_content:
                sections.append((current_heading, '\n'.join(current_content).strip()))
            
            # Start new section
            current_heading = line[3:].strip()
            current_content = []
        elif current_heading:
            current_content.append(line)
    
    # Save last section
    if current_heading and current_content:
        sections.append((current_heading, '\n'.join(current_content).strip()))
    
    return sections


async def get_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI."""
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        # Return dummy embedding for testing
        print("WARN: OpenAI not available, using dummy embedding")
        return [0.1] * 1536
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


async def seed_knowledge_base():
    """Seed knowledge base from product-docs.md."""
    print("=" * 60)
    print("Knowledge Base Seeder")
    print("=" * 60)
    
    # Read product docs
    docs_path = Path(__file__).parent.parent.parent / "context" / "product-docs.md"
    
    if not docs_path.exists():
        print(f"WARN: Product docs not found at {docs_path}")
        return
    
    print(f"\nREAD: Reading: {docs_path}")
    content = docs_path.read_text(encoding='utf-8')
    
    # Parse sections
    sections = parse_markdown_sections(content)
    print(f"INFO: Found {len(sections)} sections")
    
    # Connect to database
    print(f"\nCONN: Connecting to database: {DATABASE_URL}")
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Check if already seeded
        count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")
        if count > 0:
            print(f"WARN: Knowledge base already has {count} entries")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Aborted")
                return
        
        # Insert sections
        print("\nINSERT: Inserting sections...")
        inserted = 0
        
        for title, content in sections:
            # Skip very short sections
            if len(content) < 50:
                print(f"⊘ Skipping short section: {title}")
                continue
            
            # Generate embedding
            print(f"  STEP: Generating embedding for: {title}")
            embedding = await get_embedding(f"{title}: {content}")
            
            # Determine category
            category = "how-to"
            if "troubleshoot" in title.lower() or "error" in title.lower():
                category = "troubleshooting"
            elif "faq" in title.lower():
                category = "faq"
            elif "feature" in title.lower():
                category = "feature"
            
            # Insert
            await insert_knowledge_entry(
                conn=conn,
                title=title,
                content=content,
                category=category,
                embedding=embedding
            )
            inserted += 1
        
        print(f"\n[DONE] Inserted {inserted} knowledge base entries")
        
        # Verify
        final_count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")
        print(f"STATS: Total entries: {final_count}")
        
        # Test search
        print("\nSEARCH: Testing search...")
        test_query = "API key"
        embedding = await get_embedding(test_query)
        results = await search_knowledge_base(conn, embedding, test_query, max_results=3)
        
        if results:
            print(f"[PASS] Search returned {len(results)} results")
            print(f"  Top result: {results[0]['title']} (similarity: {results[0]['similarity']:.2f})")
        else:
            print("[FAIL] Search returned no results")
        
    finally:
        await conn.close()


async def insert_knowledge_entry(
    conn,
    title: str,
    content: str,
    category: str,
    embedding: List[float],
    tags: List[str] = None
):
    """Insert a knowledge base entry."""
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    
    await conn.execute(
        """
        INSERT INTO knowledge_base (title, content, category, embedding, tags)
        VALUES ($1, $2, $3, $4::vector, $5)
        """,
        title, content, category, embedding_str, tags
    )


async def search_knowledge_base(conn, embedding: List[float], query: str, max_results: int = 3):
    """Search knowledge base."""
    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
    
    rows = await conn.fetch(
        """
        SELECT title, content,
               1 - (embedding <=> $1::vector) as similarity
        FROM knowledge_base
        WHERE is_active = TRUE
        ORDER BY embedding <=> $1::vector
        LIMIT $2
        """,
        embedding_str, max_results
    )
    
    return [dict(row) for row in rows]


async def main():
    """Main entry point."""
    await seed_knowledge_base()


if __name__ == "__main__":
    asyncio.run(main())
