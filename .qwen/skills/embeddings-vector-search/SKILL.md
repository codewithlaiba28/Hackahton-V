---
name: embeddings-vector-search
description: Vector embeddings generation and semantic search implementation with pgvector, OpenAI embeddings, and similarity search for knowledge base retrieval.
---

# Embeddings & Vector Search Skill

## Purpose

This skill provides complete implementation for generating text embeddings and performing semantic search using PostgreSQL with pgvector extension. Essential for RAG (Retrieval Augmented Generation) patterns in customer success agents.

## When to Use This Skill

Use this skill when you need to:
- Generate embeddings for knowledge base articles
- Perform semantic similarity search
- Implement RAG pattern for AI agents
- Find relevant documentation automatically
- Match customer queries to solutions
- Build vector-based recommendation systems
- Enable natural language search

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VECTOR SEARCH ARCHITECTURE                                 │
│                                                                              │
│  KNOWLEDGE BASE INGESTION                                                    │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│  │   Docs/     │     │  Embedding  │     │  PostgreSQL │                    │
│  │   Articles  │────▶│  Generator  │────▶│  + pgvector │                    │
│  │   (Text)    │     │  (OpenAI)   │     │  (Vectors)  │                    │
│  └─────────────┘     └─────────────┘     └─────────────┘                    │
│                                                                              │
│  QUERY PROCESSING                                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                    │
│  │  Customer   │     │  Embedding  │     │   Vector    │                    │
│  │   Query     │────▶│  Generator  │────▶│  Similarity │                    │
│  │  (Text)     │     │  (OpenAI)   │     │   Search    │                    │
│  └─────────────┘     └─────────────┘     └─────────────┘                    │
│                              │                                               │
│                              ▼                                               │
│                    ┌─────────────────┐                                      │
│                    │  Top-K Results  │                                      │
│                    │  (Sorted by     │                                      │
│                    │   Similarity)   │                                      │
│                    └─────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Setup (pgvector)

```sql
-- database/vector_setup.sql

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Create knowledge base table with vector column
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding VECTOR(1536),  -- OpenAI ada-002 dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create vector similarity index (IVFFlat for better performance)
-- Note: Create index AFTER inserting data for best results
CREATE INDEX idx_knowledge_embedding 
ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Adjust based on data size

-- Alternative: HNSW index (more accurate but slower to build)
-- CREATE INDEX idx_knowledge_embedding_hnsw 
-- ON knowledge_base 
-- USING hnsw (embedding vector_cosine_ops);

-- Create metadata indexes
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_active ON knowledge_base(is_active);
CREATE INDEX idx_knowledge_metadata ON knowledge_base USING GIN (metadata);

-- Function to update embedding when content changes
CREATE OR REPLACE FUNCTION update_knowledge_embedding()
RETURNS TRIGGER AS $$
BEGIN
    -- This trigger would be called from application code
    -- NEW.embedding = await generate_embedding(NEW.content)
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_knowledge_timestamp
    BEFORE UPDATE ON knowledge_base
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_embedding();
```

---

## Embedding Generator

```python
# embeddings/generator.py

from typing import List, Optional, Union
from openai import AsyncOpenAI
import numpy as np
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate text embeddings using OpenAI or other providers."""
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        api_key: str = None,
        batch_size: int = 100
    ):
        """
        Initialize embedding generator.
        
        Args:
            model: OpenAI embedding model name
            dimensions: Output embedding dimensions
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            batch_size: Max batch size for bulk embeddings
        """
        self.model = model
        self.dimensions = dimensions
        self.batch_size = batch_size
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Model dimension mapping
        self.model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
        
        Returns:
            List of floats representing the embedding
        """
        try:
            # Preprocess text (truncate if too long)
            text = self._preprocess_text(text)
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions
            )
            
            embedding = response.data[0].embedding
            
            # Normalize embedding (optional but recommended for cosine similarity)
            embedding = self._normalize_vector(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_batch(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            show_progress: Show progress bar
        
        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            if show_progress:
                logger.info(f"Processing batch {i // self.batch_size + 1}")
            
            try:
                # Preprocess all texts in batch
                batch = [self._preprocess_text(t) for t in batch]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )
                
                # Extract embeddings in order
                batch_embeddings = [
                    self._normalize_vector(item.embedding)
                    for item in sorted(response.data, key=lambda x: x.index)
                ]
                
                embeddings.extend(batch_embeddings)
                
                # Rate limiting (avoid hitting API limits)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Batch {i} failed: {e}")
                # Add None embeddings for failed batch
                embeddings.extend([None] * len(batch))
        
        return embeddings
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate to model max length (OpenAI supports up to 8191 tokens)
        # Conservative character limit
        max_chars = 8000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        return text.strip()
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector to unit length for cosine similarity."""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return (np.array(vector) / norm).tolist()
        return vector
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding optimized for search queries.
        
        Some models support query vs document optimization.
        """
        # For OpenAI, same method works for both
        return await self.generate_embedding(query)


# Global instance
embedding_generator = EmbeddingGenerator()
```

---

## Vector Search Implementation

```python
# embeddings/vector_search.py

from typing import List, Dict, Optional, Tuple
import asyncpg
import logging
from .generator import EmbeddingGenerator

logger = logging.getLogger(__name__)

class VectorSearch:
    """Semantic search using vector similarity."""
    
    def __init__(self, db_connection: str):
        self.db_connection = db_connection
        self.embedding_generator = EmbeddingGenerator()
        self.pool = None
    
    async def create_pool(self):
        """Create database connection pool."""
        self.pool = await asyncpg.create_pool(self.db_connection)
    
    async def close_pool(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        category: str = None,
        min_similarity: float = 0.5,
        filters: Dict = None
    ) -> List[Dict]:
        """
        Search knowledge base using vector similarity.
        
        Args:
            query: Search query text
            max_results: Maximum results to return
            category: Optional category filter
            min_similarity: Minimum similarity threshold
            filters: Additional filters (metadata)
        
        Returns:
            List of results with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embedding(query)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        async with self.pool.acquire() as conn:
            # Build query with optional filters
            where_clauses = ["is_active = TRUE"]
            params = [embedding_str, max_results]
            
            if category:
                where_clauses.append(f"category = ${len(params) + 1}")
                params.append(category)
            
            if filters:
                for key, value in filters.items():
                    where_clauses.append(f"metadata->>'{key}' = ${len(params) + 1}")
                    params.append(str(value))
            
            where_clause = " AND ".join(where_clauses)
            
            # Vector similarity search
            results = await conn.fetch(f"""
                SELECT 
                    id,
                    title,
                    content,
                    category,
                    metadata,
                    1 - (embedding <=> $1::vector) as similarity
                FROM knowledge_base
                WHERE {where_clause}
                AND 1 - (embedding <=> $1::vector) >= ${len(params) + 1}
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, *params, min_similarity)
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'content': row['content'],
                    'category': row['category'],
                    'metadata': dict(row['metadata']),
                    'similarity': float(row['similarity']),
                    'relevance': self._calculate_relevance(row['similarity'])
                })
            
            return formatted_results
    
    async def search_hybrid(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Hybrid search combining vector and keyword search.
        
        Uses both semantic similarity and text matching.
        """
        # Vector search
        vector_results = await self.search(query, max_results=max_results * 2)
        
        # Keyword search (full-text search)
        async with self.pool.acquire() as conn:
            keyword_results = await conn.fetch("""
                SELECT 
                    id,
                    title,
                    content,
                    category,
                    ts_rank(to_tsvector('english', title || ' ' || content), query) as keyword_score
                FROM knowledge_base,
                     plainto_tsquery('english', $1) query
                WHERE to_tsvector('english', title || ' ' || content) @@ query
                AND is_active = TRUE
                ORDER BY keyword_score DESC
                LIMIT $2
            """, query, max_results * 2)
        
        # Merge results (reciprocal rank fusion)
        merged = self._merge_results(vector_results, keyword_results)
        
        return merged[:max_results]
    
    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict]
    ) -> List[Dict]:
        """Merge vector and keyword results using reciprocal rank fusion."""
        # Create rank maps
        vector_ranks = {r['id']: i + 1 for i, r in enumerate(vector_results)}
        keyword_ranks = {r['id']: i + 1 for i, r in enumerate(keyword_results)}
        
        # Get all unique IDs
        all_ids = set(vector_ranks.keys()) | set(keyword_ranks.keys())
        
        # Calculate fusion scores
        scored = []
        for id in all_ids:
            vector_rank = vector_ranks.get(id, len(vector_results) + 1)
            keyword_rank = keyword_ranks.get(id, len(keyword_results) + 1)
            
            # Reciprocal rank fusion with k=60
            score = (1 / (60 + vector_rank)) + (1 / (60 + keyword_rank))
            
            # Get result data (prefer vector result)
            result = next(
                (r for r in vector_results if r['id'] == id),
                next((r for r in keyword_results if r['id'] == id))
            )
            result['fusion_score'] = score
            scored.append(result)
        
        # Sort by fusion score
        return sorted(scored, key=lambda x: x['fusion_score'], reverse=True)
    
    def _calculate_relevance(self, similarity: float) -> str:
        """Convert similarity score to relevance label."""
        if similarity >= 0.9:
            return "highly_relevant"
        elif similarity >= 0.7:
            return "relevant"
        elif similarity >= 0.5:
            return "somewhat_relevant"
        else:
            return "low_relevance"
    
    async def find_similar(
        self,
        document_id: str,
        max_results: int = 5
    ) -> List[Dict]:
        """Find documents similar to a given document."""
        async with self.pool.acquire() as conn:
            # Get document embedding
            doc = await conn.fetchrow(
                "SELECT embedding, category FROM knowledge_base WHERE id = $1",
                document_id
            )
            
            if not doc:
                return []
            
            embedding_str = '[' + ','.join(map(str, doc['embedding'])) + ']'
            
            # Find similar documents (excluding the original)
            results = await conn.fetch(f"""
                SELECT 
                    id,
                    title,
                    content,
                    category,
                    1 - (embedding <=> $1::vector) as similarity
                FROM knowledge_base
                WHERE id != $2
                AND is_active = TRUE
                AND category = $3  -- Same category
                ORDER BY embedding <=> $1::vector
                LIMIT $4
            """, embedding_str, document_id, doc['category'], max_results)
            
            return [
                {
                    'id': str(row['id']),
                    'title': row['title'],
                    'similarity': float(row['similarity'])
                }
                for row in results
            ]
    
    async def index_document(
        self,
        title: str,
        content: str,
        category: str = None,
        metadata: Dict = None
    ) -> str:
        """
        Index a new document with embedding.
        
        Args:
            title: Document title
            content: Document content
            category: Document category
            metadata: Additional metadata
        
        Returns:
            Document ID
        """
        # Generate embedding
        # Combine title and content for better context
        full_text = f"{title}: {content}"
        embedding = await self.embedding_generator.generate_embedding(full_text)
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO knowledge_base (title, content, category, embedding, metadata)
                VALUES ($1, $2, $3, $4::vector, $5)
                RETURNING id
            """, title, content, category, embedding_str, metadata)
            
            return str(result['id'])
    
    async def bulk_index(
        self,
        documents: List[Dict],
        batch_size: int = 50
    ) -> int:
        """
        Index multiple documents in batches.
        
        Args:
            documents: List of documents with title, content, category, metadata
            batch_size: Batch size for processing
        
        Returns:
            Number of documents indexed
        """
        indexed = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Generate embeddings for batch
            texts = [f"{d['title']}: {d['content']}" for d in batch]
            embeddings = await self.embedding_generator.generate_batch(texts)
            
            # Insert into database
            async with self.pool.acquire() as conn:
                for doc, embedding in zip(batch, embeddings):
                    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                    
                    await conn.execute("""
                        INSERT INTO knowledge_base (title, content, category, embedding, metadata)
                        VALUES ($1, $2, $3, $4::vector, $5)
                    """, doc['title'], doc['content'], doc.get('category'), 
                       embedding_str, doc.get('metadata', {}))
                    
                    indexed += 1
            
            logger.info(f"Indexed batch {i // batch_size + 1}")
        
        return indexed
```

---

## RAG Integration with Agent

```python
# embeddings/rag_agent.py

from typing import List, Dict
from .vector_search import VectorSearch
import logging

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Retriever for RAG (Retrieval Augmented Generation) pattern."""
    
    def __init__(self, vector_search: VectorSearch):
        self.vector_search = vector_search
    
    async def retrieve_context(
        self,
        query: str,
        max_results: int = 5,
        min_similarity: float = 0.6
    ) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            max_results: Maximum documents to retrieve
            min_similarity: Minimum similarity threshold
        
        Returns:
            Formatted context string for LLM
        """
        results = await self.vector_search.search(
            query=query,
            max_results=max_results,
            min_similarity=min_similarity
        )
        
        if not results:
            return "No relevant documentation found."
        
        # Format context for LLM
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}] {result['title']}\n"
                f"Relevance: {result['relevance']} ({result['similarity']:.2f})\n"
                f"Content: {result['content'][:500]}..."
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def create_rag_prompt(self, query: str, context: str) -> str:
        """
        Create RAG prompt for LLM.
        
        Args:
            query: User query
            context: Retrieved context
        
        Returns:
            Formatted prompt for LLM
        """
        return f"""You are a helpful customer support agent. Use the following context to answer the question.

## Context from Knowledge Base:
{context}

## Instructions:
- Answer based on the provided context
- If the context doesn't contain the answer, say so
- Be concise and helpful
- Cite sources when possible

## Customer Question:
{query}

## Your Response:
"""
```

---

## Testing

```python
# tests/test_embeddings.py

import pytest
from embeddings.generator import EmbeddingGenerator
from embeddings.vector_search import VectorSearch

@pytest.fixture
def embedding_generator():
    return EmbeddingGenerator()

@pytest.fixture
def vector_search():
    vs = VectorSearch("postgresql://user:pass@localhost:5432/test_db")
    return vs

class TestEmbeddingGenerator:
    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_generator):
        """Test single embedding generation."""
        embedding = await embedding_generator.generate_embedding(
            "How do I reset my password?"
        )
        
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_generate_batch(self, embedding_generator):
        """Test batch embedding generation."""
        texts = [
            "How do I reset my password?",
            "Where can I find my invoices?",
            "How to update my profile?"
        ]
        
        embeddings = await embedding_generator.generate_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)

class TestVectorSearch:
    @pytest.mark.asyncio
    async def test_search(self, vector_search):
        """Test vector similarity search."""
        results = await vector_search.search(
            query="password reset",
            max_results=5
        )
        
        assert isinstance(results, list)
        if results:
            assert 'title' in results[0]
            assert 'similarity' in results[0]
    
    @pytest.mark.asyncio
    async def test_search_with_category(self, vector_search):
        """Test search with category filter."""
        results = await vector_search.search(
            query="billing",
            max_results=5,
            category="billing"
        )
        
        # All results should match the category
        for result in results:
            assert result['category'] == 'billing'
    
    @pytest.mark.asyncio
    async def test_index_document(self, vector_search):
        """Test document indexing."""
        doc_id = await vector_search.index_document(
            title="How to Reset Password",
            content="To reset your password, go to settings...",
            category="how-to"
        )
        
        assert doc_id is not None
```

---

## Acceptance Criteria

- [ ] pgvector extension installed and configured
- [ ] Embedding generator works with OpenAI
- [ ] Vector similarity search returns relevant results
- [ ] Hybrid search combines vector + keyword
- [ ] Batch embedding generation works
- [ ] RAG retriever formats context correctly
- [ ] Document indexing creates embeddings
- [ ] All tests pass
- [ ] Performance is acceptable (<100ms for search)

## Related Skills

- `postgres-crm-schema` - Database with pgvector
- `customer-success-agent` - Uses RAG for knowledge
- `observability-metrics` - Search metrics

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [RAG Pattern](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/)
