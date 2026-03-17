"""Sentiment analysis for Customer Success FTE."""

import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Keyword-based sentiment analyzer for Phase 1.
    
    Analyzes customer messages for sentiment and provides escalation recommendations.
    In Phase 2, this will be replaced with ML-based sentiment model.
    """
    
    # Negative keywords with weights
    NEGATIVE_KEYWORDS = {
        "terrible": -0.3,
        "awful": -0.3,
        "horrible": -0.3,
        "broken": -0.2,
        "useless": -0.2,
        "hate": -0.2,
        "frustrated": -0.2,
        "angry": -0.2,
        "disappointed": -0.15,
        "ridiculous": -0.15,
        "unacceptable": -0.15,
        "issue": -0.1,
        "problem": -0.1,
        "error": -0.1,
    }
    
    # Positive keywords with weights
    POSITIVE_KEYWORDS = {
        "excellent": 0.3,
        "amazing": 0.3,
        "fantastic": 0.3,
        "great": 0.2,
        "awesome": 0.2,
        "love": 0.2,
        "thank": 0.15,
        "thanks": 0.15,
        "helpful": 0.15,
        "good": 0.1,
        "perfect": 0.2,
    }
    
    # Escalation threshold
    ESCALATION_THRESHOLD = 0.3
    
    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of customer message.
        
        Args:
            text: Customer message text
            
        Returns:
            Tuple of (score, label) where score is 0.0-1.0 and label is positive/neutral/negative
        """
        if not text or not text.strip():
            return 0.5, "neutral"
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Calculate base score (start neutral)
        score = 0.5
        
        # Adjust score based on keywords
        for word in words:
            # Check negative keywords
            if word in self.NEGATIVE_KEYWORDS:
                score += self.NEGATIVE_KEYWORDS[word]
            
            # Check positive keywords
            if word in self.POSITIVE_KEYWORDS:
                score += self.POSITIVE_KEYWORDS[word]
        
        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        
        # Determine label
        label = self._score_to_label(score)
        
        logger.debug(f"Sentiment analysis: score={score:.2f}, label={label}")
        
        return score, label
    
    def _score_to_label(self, score: float) -> str:
        """
        Convert numeric score to label.
        
        Args:
            score: Sentiment score (0.0-1.0)
            
        Returns:
            Label: "positive", "neutral", or "negative"
        """
        if score < self.ESCALATION_THRESHOLD:
            return "negative"
        elif score > 0.7:
            return "positive"
        else:
            return "neutral"
    
    def should_escalate(self, score: float) -> bool:
        """
        Determine if sentiment score warrants escalation.
        
        Args:
            score: Sentiment score
            
        Returns:
            True if should escalate, False otherwise
        """
        return score < self.ESCALATION_THRESHOLD
