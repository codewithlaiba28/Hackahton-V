"""Message normalizer for Customer Success FTE."""

import logging
from typing import Optional
from dataclasses import dataclass
from src.channels.base import Channel, ChannelMessage
from src.agent.memory import ConversationMemoryStore

logger = logging.getLogger(__name__)


@dataclass
class NormalizedMessage:
    """
    Normalized message for agent processing.
    
    Attributes:
        customer_id: Primary customer identifier
        content: Cleaned text content
        channel: Source channel
        intent_hint: Extracted topic hint from keywords
        is_followup: Whether customer has prior history
        raw_message: Original ChannelMessage object
    """
    customer_id: str
    content: str
    channel: Channel
    intent_hint: str
    is_followup: bool
    raw_message: ChannelMessage


class MessageNormalizer:
    """
    Normalizes raw ChannelMessage objects into standardized agent input.
    
    Extracts intent, detects follow-ups, and cleans content.
    """
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        "api_key": ["api key", "apikey", "api token", "access token"],
        "oauth": ["oauth", "authentication", "authorize", "authorization"],
        "webhook": ["webhook", "callback", "notification", "event"],
        "rate_limit": ["rate limit", "quota", "too many requests", "429"],
        "billing": ["billing", "invoice", "payment", "charge", "subscription"],
        "export": ["export", "download", "csv", "json", "data export"],
        "error": ["error", "bug", "broken", "not working", "issue"],
        "pricing": ["price", "pricing", "cost", "plan cost", "upgrade"],
        "refund": ["refund", "money back", "cancel", "chargeback"],
    }
    
    def __init__(self, memory_store: ConversationMemoryStore):
        """
        Initialize message normalizer.
        
        Args:
            memory_store: Conversation memory store for follow-up detection
        """
        self.memory_store = memory_store
    
    def normalize(self, message: ChannelMessage) -> NormalizedMessage:
        """
        Normalize raw ChannelMessage into standardized format.
        
        Args:
            message: Raw ChannelMessage from channel simulator
            
        Returns:
            NormalizedMessage ready for agent processing
        """
        # Clean content
        cleaned_content = self._clean_content(message.content)
        
        # Extract intent hint
        intent_hint = self._extract_intent(cleaned_content)
        
        # Detect follow-up
        is_followup = self._detect_followup(message.customer_id)
        
        return NormalizedMessage(
            customer_id=message.customer_id,
            content=cleaned_content,
            channel=message.channel,
            intent_hint=intent_hint,
            is_followup=is_followup,
            raw_message=message
        )
    
    def _clean_content(self, content: str) -> str:
        """
        Clean message content.
        
        Args:
            content: Raw message content
            
        Returns:
            Cleaned content with extra whitespace removed
        """
        if not content:
            return ""
        
        # Remove extra whitespace
        cleaned = " ".join(content.split())
        
        return cleaned.strip()
    
    def _extract_intent(self, content: str) -> str:
        """
        Extract intent hint from message content.
        
        Args:
            content: Message content
            
        Returns:
            Intent keyword or "general"
        """
        content_lower = content.lower()
        
        # Check each intent category
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(keyword in content_lower for keyword in keywords):
                logger.debug(f"Detected intent: {intent}")
                return intent
        
        # Default to general
        return "general"
    
    def _detect_followup(self, customer_id: str) -> bool:
        """
        Detect if this is a follow-up message.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            True if customer has prior conversation history
        """
        if customer_id == "unknown":
            return False
        
        # Check if customer has prior turns
        memory = self.memory_store.get_or_create(customer_id)
        has_history = len(memory.turns) > 0
        
        logger.debug(f"Customer {customer_id} followup: {has_history}")
        return has_history
