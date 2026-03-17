"""Knowledge base search for Customer Success FTE."""

import logging
from typing import List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Keyword-based knowledge base searcher for Phase 1.
    
    Loads product documentation and provides keyword search functionality.
    In Phase 2, this will be replaced with pgvector semantic search.
    """
    
    def __init__(self, docs_path: str = "context/product-docs.md"):
        """
        Initialize knowledge base.
        
        Args:
            docs_path: Path to product documentation markdown file
        """
        self.docs_path = Path(docs_path)
        self.sections: List[Tuple[str, str]] = []  # List of (heading, content)
        self._load_documentation()
    
    def _load_documentation(self):
        """Load and parse product documentation into sections."""
        if not self.docs_path.exists():
            logger.warning(f"Documentation not found at {self.docs_path}")
            return
        
        try:
            content = self.docs_path.read_text(encoding='utf-8')
            self.sections = self._parse_sections(content)
            logger.info(f"Loaded {len(self.sections)} sections from knowledge base")
        except Exception as e:
            logger.error(f"Failed to load documentation: {e}")
    
    def _parse_sections(self, content: str) -> List[Tuple[str, str]]:
        """
        Parse markdown content into sections.
        
        Args:
            content: Markdown file content
            
        Returns:
            List of (heading, content) tuples
        """
        sections = []
        current_heading = None
        current_content = []
        
        for line in content.split('\n'):
            # Check for heading (## Section Name)
            if line.startswith('## '):
                # Save previous section
                if current_heading and current_content:
                    sections.append((current_heading, '\n'.join(current_content)))
                
                # Start new section
                current_heading = line[3:].strip()
                current_content = []
            elif current_heading:
                current_content.append(line)
        
        # Save last section
        if current_heading and current_content:
            sections.append((current_heading, '\n'.join(current_content)))
        
        return sections
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Search knowledge base for relevant information.
        
        Args:
            query: Customer's search query
            max_results: Maximum number of results to return
            
        Returns:
            Formatted string of relevant sections, or "No relevant documentation found."
        """
        if not query or not query.strip():
            return "Please describe your question."
        
        if not self.sections:
            logger.warning("Knowledge base is empty")
            return "Knowledge base temporarily unavailable."
        
        # Score sections by keyword overlap
        query_keywords = set(query.lower().split())
        scored_sections = []
        
        for heading, content in self.sections:
            score = self._calculate_overlap_score(query_keywords, heading, content)
            if score > 0:
                scored_sections.append((heading, content, score))
        
        # Sort by score and return top results
        scored_sections.sort(key=lambda x: x[2], reverse=True)
        top_sections = scored_sections[:max_results]
        
        if not top_sections:
            return "No relevant documentation found. Consider escalating to human support."
        
        # Format results
        formatted_results = []
        for heading, content, score in top_sections:
            # Truncate content if too long
            truncated_content = content[:500] + "..." if len(content) > 500 else content
            formatted_results.append(f"**{heading}** (relevance: {score:.2f})\n{truncated_content}")
        
        return "\n\n---\n\n".join(formatted_results)
    
    def _calculate_overlap_score(self, query_keywords: set, heading: str, content: str) -> float:
        """
        Calculate keyword overlap score between query and section.
        
        Args:
            query_keywords: Set of keywords from query
            heading: Section heading
            content: Section content
            
        Returns:
            Overlap score (0.0 to 1.0)
        """
        # Extract keywords from heading and content
        heading_keywords = set(heading.lower().split())
        content_keywords = set(content.lower().split())
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        heading_keywords -= stop_words
        content_keywords -= stop_words
        
        # Calculate overlap
        heading_overlap = len(query_keywords & heading_keywords)
        content_overlap = len(query_keywords & content_keywords)
        
        # Weight heading matches higher
        score = (heading_overlap * 2.0 + content_overlap) / (len(query_keywords) * 2.0 + 1)
        
        return min(1.0, score)
    
    def reload(self):
        """Reload documentation from disk."""
        self.sections = []
        self._load_documentation()
