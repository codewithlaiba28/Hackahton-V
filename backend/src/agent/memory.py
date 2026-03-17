"""In-memory conversation memory for Customer Success FTE."""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """
    Represents a single turn in a conversation.
    
    Attributes:
        role: "customer" or "agent"
        content: Message content
        channel: Source channel
        timestamp: When message was sent
        sentiment_score: Optional sentiment score
        tool_calls: List of tool calls made
    """
    role: str  # "customer" or "agent"
    content: str
    channel: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    sentiment_score: Optional[float] = None
    tool_calls: List[Dict] = field(default_factory=list)


@dataclass
class CustomerMemory:
    """
    In-memory representation of a customer's state and history.
    
    Attributes:
        customer_id: Primary identifier
        name: Customer name
        email: Customer email
        phone: Customer phone
        turns: List of conversation turns
        topics: List of discussed topics
        sentiment_trend: List of recent sentiment scores
        status: Conversation status (active, escalated, resolved)
        escalated: Whether conversation is escalated
    """
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    turns: List[ConversationTurn] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    sentiment_trend: List[float] = field(default_factory=list)
    status: str = "active"  # "active", "escalated", "resolved"
    escalated: bool = False


class ConversationMemoryStore:
    """
    In-memory store for customer conversations.
    
    Thread-safe dictionary-based store for Phase 1.
    In Phase 2, this will be replaced with PostgreSQL persistence.
    """
    
    def __init__(self):
        """Initialize conversation memory store."""
        self._store: Dict[str, CustomerMemory] = {}
    
    def get_or_create(
        self,
        customer_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None
    ) -> CustomerMemory:
        """
        Get existing customer memory or create new one.
        
        Args:
            customer_id: Primary customer identifier
            email: Optional email address
            phone: Optional phone number
            name: Optional customer name
            
        Returns:
            CustomerMemory object
        """
        if customer_id not in self._store:
            self._store[customer_id] = CustomerMemory(
                customer_id=customer_id,
                email=email,
                phone=phone,
                name=name
            )
            logger.debug(f"Created new customer memory for {customer_id}")
        
        return self._store[customer_id]
    
    def add_turn(self, customer_id: str, turn: ConversationTurn):
        """
        Add a conversation turn to customer memory.
        
        Args:
            customer_id: Customer identifier
            turn: Conversation turn to add
        """
        memory = self.get_or_create(customer_id)
        memory.turns.append(turn)
        
        # Update sentiment trend
        if turn.sentiment_score is not None:
            memory.sentiment_trend.append(turn.sentiment_score)
            # Keep only last 10 scores
            memory.sentiment_trend = memory.sentiment_trend[-10:]
        
        logger.debug(f"Added turn for customer {customer_id}, total turns: {len(memory.turns)}")
    
    def get_history_text(self, customer_id: str, limit: int = 10) -> str:
        """
        Get formatted conversation history for a customer.
        
        Args:
            customer_id: Customer identifier
            limit: Maximum number of turns to return
            
        Returns:
            Formatted history string
        """
        if customer_id not in self._store:
            return "No prior interaction history."
        
        memory = self._store[customer_id]
        
        if not memory.turns:
            return "No prior interaction history."
        
        # Get last N turns
        recent_turns = memory.turns[-limit:]
        
        # Format as text
        lines = []
        for turn in recent_turns:
            lines.append(f"[{turn.channel.upper()}] {turn.role}: {turn.content}")
        
        return "\n".join(lines)
    
    def mark_escalated(self, customer_id: str):
        """
        Mark customer conversation as escalated.
        
        Args:
            customer_id: Customer identifier
        """
        memory = self.get_or_create(customer_id)
        memory.status = "escalated"
        memory.escalated = True
        logger.info(f"Marked customer {customer_id} as escalated")
    
    def mark_resolved(self, customer_id: str):
        """
        Mark customer conversation as resolved.
        
        Args:
            customer_id: Customer identifier
        """
        memory = self.get_or_create(customer_id)
        memory.status = "resolved"
        memory.escalated = False
        logger.info(f"Marked customer {customer_id} as resolved")
    
    def get_sentiment_trend(self, customer_id: str) -> List[float]:
        """
        Get customer's sentiment trend.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of sentiment scores (most recent last)
        """
        if customer_id not in self._store:
            return []
        
        return self._store[customer_id].sentiment_trend.copy()
    
    def clear(self):
        """Clear all customer memory (for testing)."""
        self._store.clear()
        logger.info("Cleared all customer memory")
