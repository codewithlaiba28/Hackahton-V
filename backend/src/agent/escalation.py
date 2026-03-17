"""Escalation logic for Customer Success FTE."""

import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class EscalationChecker:
    """
    Rule-based escalation decision maker for Phase 1.
    
    Checks for various escalation triggers including keywords, sentiment, and explicit requests.
    """
    
    # Legal threat keywords
    LEGAL_KEYWORDS = ["lawyer", "legal", "sue", "attorney", "lawsuit", "court", "litigation"]
    
    # Pricing inquiry keywords
    PRICING_KEYWORDS = ["price", "pricing", "cost", "how much", "enterprise plan", "quote", "quotation"]
    
    # Refund request keywords
    REFUND_KEYWORDS = ["refund", "money back", "chargeback", "charge back", "cancel subscription"]
    
    # Human request keywords
    HUMAN_KEYWORDS = ["human", "agent", "representative", "real person", "speak to someone"]
    
    # Negative sentiment threshold
    SENTIMENT_THRESHOLD = 0.3
    
    def check_escalation(self, message: str, sentiment_score: float, channel: str = "") -> Tuple[bool, str]:
        """
        Check if message should be escalated to human support.
        
        Args:
            message: Customer message text
            sentiment_score: Sentiment analysis score (0.0-1.0)
            channel: Source channel (email, whatsapp, web_form)
            
        Returns:
            Tuple of (should_escalate, reason_code)
        """
        message_lower = message.lower()
        
        # Check legal threats (highest priority)
        if any(keyword in message_lower for keyword in self.LEGAL_KEYWORDS):
            logger.info("Escalation triggered: legal threat")
            return True, "legal_threat"
        
        # Check pricing inquiries
        if any(keyword in message_lower for keyword in self.PRICING_KEYWORDS):
            logger.info("Escalation triggered: pricing inquiry")
            return True, "pricing_inquiry"
        
        # Check refund requests
        if any(keyword in message_lower for keyword in self.REFUND_KEYWORDS):
            logger.info("Escalation triggered: refund request")
            return True, "refund_request"
        
        # Check human requests
        if any(keyword in message_lower for keyword in self.HUMAN_KEYWORDS):
            logger.info("Escalation triggered: human requested")
            return True, "human_requested"
        
        # Check negative sentiment
        if sentiment_score < self.SENTIMENT_THRESHOLD:
            logger.info(f"Escalation triggered: negative sentiment ({sentiment_score:.2f})")
            return True, "negative_sentiment"
        
        # No escalation needed
        return False, ""
    
    def get_escalation_response(self, reason: str) -> str:
        """
        Get appropriate response message for escalation.
        
        Args:
            reason: Escalation reason code
            
        Returns:
            Empathetic response message
        """
        responses = {
            "legal_threat": "Your concern is important. A specialist will review this matter and contact you shortly.",
            "pricing_inquiry": "I'll connect you with our sales team who can provide detailed pricing information. They'll contact you within 24 hours.",
            "refund_request": "I'll connect you with our billing team who can assist with your refund request.",
            "human_requested": "I'll connect you with a human agent who can assist you further.",
            "negative_sentiment": "I understand your frustration. Let me connect you with someone who can help resolve this issue.",
        }
        
        return responses.get(reason, "Let me connect you with a specialist who can better assist you.")
