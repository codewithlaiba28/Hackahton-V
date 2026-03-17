---
name: sentiment-analysis
description: Customer sentiment analysis for support conversations with escalation triggers, sentiment tracking, emotion detection, and channel-aware sentiment thresholds.
---

# Sentiment Analysis Skill

## Purpose

This skill provides complete sentiment analysis capabilities for customer support conversations. Detect customer情绪, track sentiment trends across conversations, and automatically escalate when sentiment falls below thresholds.

## When to Use This Skill

Use this skill when you need to:
- Analyze customer sentiment in real-time
- Track sentiment trends across conversations
- Auto-escalate negative sentiment cases
- Detect emotions (anger, frustration, satisfaction)
- Generate sentiment-based metrics and reports
- Adapt responses based on customer情绪
- Monitor agent performance by sentiment

---

## Sentiment Analysis Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SENTIMENT ANALYSIS PIPELINE                               │
│                                                                              │
│  INCOMING MESSAGE                                                            │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────┐                                                         │
│  │ Pre-processing  │  - Lowercase, remove special chars                     │
│  └────────┬────────┘                                                         │
│           │                                                                  │
│           ▼                                                                    │
│  ┌─────────────────┐                                                         │
│  │ Feature Extract │  - Keywords, n-grams, punctuation                      │
│  └────────┬────────┘                                                         │
│           │                                                                  │
│           ▼                                                                    │
│  ┌─────────────────┐     ┌─────────────────┐                                 │
│  │  Rule-Based     │     │  ML Model       │                                 │
│  │  Analysis       │     │  (Optional)     │                                 │
│  │  - Keywords     │     │  - Transformer  │                                 │
│  │  - Patterns     │     │  - Fine-tuned   │                                 │
│  └────────┬────────┘     └────────┬────────┘                                 │
│           │                       │                                          │
│           └───────────┬───────────┘                                          │
│                       ▼                                                      │
│              ┌─────────────────┐                                             │
│              │  Sentiment Score │                                             │
│              │  -1.0 to +1.0   │                                             │
│              └────────┬────────┘                                             │
│                       │                                                      │
│           ┌───────────┼───────────┐                                         │
│           ▼           ▼           ▼                                          │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐                                  │
│    │ Negative │ │ Neutral  │ │ Positive │                                  │
│    │ < 0.3    │ │ 0.3-0.7  │ │ > 0.7    │                                  │
│    └────┬─────┘ └────┬─────┘ └────┬─────┘                                  │
│         │            │            │                                         │
│         ▼            ▼            ▼                                         │
│    ESCALATE      MONITOR      CONTINUE                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Sentiment Analyzer Implementation

```python
# agent/sentiment.py

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SentimentLabel(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class Emotion(str, Enum):
    ANGER = "anger"
    FRUSTRATION = "frustration"
    CONFUSION = "confusion"
    SATISFACTION = "satisfaction"
    GRATITUDE = "gratitude"
    FEAR = "fear"
    URGENCY = "urgency"

@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    score: float  # -1.0 to 1.0
    label: SentimentLabel
    confidence: float  # 0.0 to 1.0
    emotions: List[Emotion]
    should_escalate: bool
    escalation_reason: Optional[str]
    keywords_detected: List[str]
    analyzed_at: datetime

class SentimentAnalyzer:
    """Analyze customer sentiment for escalation decisions."""
    
    # Negative keywords with weights
    NEGATIVE_KEYWORDS = {
        # Very strong negative (-0.3 each)
        "terrible": -0.3,
        "awful": -0.3,
        "horrible": -0.3,
        "disgusting": -0.3,
        "worst": -0.3,
        
        # Strong negative (-0.2 each)
        "hate": -0.2,
        "useless": -0.2,
        "broken": -0.2,
        "failed": -0.2,
        "error": -0.15,
        "bug": -0.15,
        "issue": -0.1,
        "problem": -0.1,
        
        # Frustration indicators (-0.15 each)
        "ridiculous": -0.15,
        "unacceptable": -0.15,
        "disappointed": -0.15,
        "frustrated": -0.15,
        "annoyed": -0.15,
        
        # Urgency indicators (-0.1 each)
        "urgent": -0.1,
        "asap": -0.1,
        "immediately": -0.1,
        "emergency": -0.1,
    }
    
    # Positive keywords with weights
    POSITIVE_KEYWORDS = {
        # Very strong positive (+0.3 each)
        "excellent": 0.3,
        "amazing": 0.3,
        "fantastic": 0.3,
        "wonderful": 0.3,
        "love": 0.25,
        
        # Strong positive (+0.2 each)
        "great": 0.2,
        "awesome": 0.2,
        "perfect": 0.2,
        "helpful": 0.15,
        "thanks": 0.15,
        "thank you": 0.15,
        
        # Moderate positive (+0.1 each)
        "good": 0.1,
        "nice": 0.1,
        "works": 0.1,
        "satisfied": 0.15,
        "appreciate": 0.15,
    }
    
    # Escalation trigger keywords
    ESCALATION_KEYWORDS = {
        "lawyer": "legal_concern",
        "legal": "legal_concern",
        "sue": "legal_concern",
        "attorney": "legal_concern",
        "lawsuit": "legal_concern",
        
        "refund": "refund_request",
        "cancel": "cancellation_request",
        "unsubscribe": "cancellation_request",
        
        "manager": "escalation_request",
        "supervisor": "escalation_request",
        "human": "human_requested",
        "agent": "human_requested",
        "representative": "human_requested",
        "real person": "human_requested",
        
        "complaint": "formal_complaint",
        "report": "formal_complaint",
    }
    
    # Emotion detection patterns
    EMOTION_PATTERNS = {
        Emotion.ANGER: ["angry", "furious", "enraged", "livid", "outraged"],
        Emotion.FRUSTRATION: ["frustrated", "annoyed", "irritated", "fed up"],
        Emotion.CONFUSION: ["confused", "unclear", "don't understand", "lost"],
        Emotion.SATISFACTION: ["satisfied", "happy", "pleased", "delighted"],
        Emotion.GRATITUDE: ["thank", "grateful", "appreciate", "thanks"],
        Emotion.FEAR: ["worried", "concerned", "afraid", "scared"],
        Emotion.URGENCY: ["urgent", "asap", "immediately", "emergency"],
    }
    
    def __init__(self, escalation_threshold: float = 0.3):
        self.escalation_threshold = escalation_threshold
    
    async def analyze(self, message: str, context: Dict = None) -> SentimentResult:
        """
        Analyze sentiment of a customer message.
        
        Args:
            message: Customer message text
            context: Optional context (channel, customer history, etc.)
        
        Returns:
            SentimentResult with score, label, and escalation decision
        """
        message_lower = message.lower()
        
        # Calculate base sentiment score
        score = 0.5  # Neutral default
        
        # Detect keywords and adjust score
        keywords_detected = []
        for keyword, weight in self.NEGATIVE_KEYWORDS.items():
            if keyword in message_lower:
                score += weight
                keywords_detected.append(keyword)
        
        for keyword, weight in self.POSITIVE_KEYWORDS.items():
            if keyword in message_lower:
                score += weight
                keywords_detected.append(keyword)
        
        # Clamp score to [-1.0, 1.0]
        score = max(-1.0, min(1.0, score))
        
        # Determine label
        label = self._score_to_label(score)
        
        # Detect emotions
        emotions = self._detect_emotions(message_lower)
        
        # Check for escalation triggers
        should_escalate, escalation_reason = self._check_escalation_triggers(
            message_lower, score
        )
        
        # Calculate confidence (based on keyword matches)
        confidence = min(1.0, 0.5 + (len(keywords_detected) * 0.1))
        
        # Adjust for channel (WhatsApp tends to be more casual)
        if context and context.get('channel') == 'whatsapp':
            # Slightly more lenient for WhatsApp
            if score < 0.3:
                score = min(score + 0.05, 0.3)
        
        return SentimentResult(
            score=round(score, 3),
            label=label,
            confidence=round(confidence, 2),
            emotions=emotions,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            keywords_detected=keywords_detected,
            analyzed_at=datetime.utcnow()
        )
    
    def _score_to_label(self, score: float) -> SentimentLabel:
        """Convert numeric score to label."""
        if score < -0.6:
            return SentimentLabel.VERY_NEGATIVE
        elif score < 0.3:
            return SentimentLabel.NEGATIVE
        elif score < 0.7:
            return SentimentLabel.NEUTRAL
        elif score < 0.9:
            return SentimentLabel.POSITIVE
        else:
            return SentimentLabel.VERY_POSITIVE
    
    def _detect_emotions(self, message: str) -> List[Emotion]:
        """Detect emotions in message."""
        detected = []
        
        for emotion, patterns in self.EMOTION_PATTERNS.items():
            if any(pattern in message for pattern in patterns):
                detected.append(emotion)
        
        return detected
    
    def _check_escalation_triggers(
        self,
        message: str,
        score: float
    ) -> Tuple[bool, Optional[str]]:
        """Check if message triggers escalation."""
        
        # Check explicit escalation keywords
        for keyword, reason in self.ESCALATION_KEYWORDS.items():
            if keyword in message:
                return True, reason
        
        # Check sentiment threshold
        if score < self.escalation_threshold:
            return True, "negative_sentiment"
        
        # Check for multiple negative keywords
        negative_count = sum(
            1 for kw in self.NEGATIVE_KEYWORDS if kw in message
        )
        if negative_count >= 3:
            return True, "multiple_negative_indicators"
        
        return False, None
    
    async def analyze_conversation_trend(
        self,
        messages: List[Dict]
    ) -> Dict:
        """
        Analyze sentiment trend across a conversation.
        
        Args:
            messages: List of messages with 'content' and 'role' keys
        
        Returns:
            Trend analysis with direction and recommendations
        """
        customer_messages = [
            m['content'] for m in messages if m.get('role') == 'customer'
        ]
        
        if not customer_messages:
            return {
                'trend': 'unknown',
                'average_score': 0.5,
                'recommendation': 'no_data'
            }
        
        # Analyze each message
        scores = []
        for msg in customer_messages:
            result = await self.analyze(msg)
            scores.append(result.score)
        
        # Calculate trend
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            older_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else recent_avg
            
            if recent_avg < older_avg - 0.1:
                trend = "declining"
            elif recent_avg > older_avg + 0.1:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        average_score = sum(scores) / len(scores)
        
        # Recommendation
        if average_score < 0.3:
            recommendation = "escalate_immediately"
        elif trend == "declining":
            recommendation = "monitor_closely"
        elif average_score > 0.7:
            recommendation = "positive_interaction"
        else:
            recommendation = "continue_standard_support"
        
        return {
            'trend': trend,
            'average_score': round(average_score, 3),
            'message_count': len(scores),
            'recommendation': recommendation
        }
```

---

## Sentiment Tracking in Database

```python
# database/sentiment_queries.py

from typing import Optional, List, Dict
from datetime import datetime, timedelta
import asyncpg

class SentimentQueries:
    """Database queries for sentiment tracking."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def create_pool(self):
        """Create database connection pool."""
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def record_sentiment(
        self,
        conversation_id: str,
        message_id: str,
        sentiment_score: float,
        sentiment_label: str,
        emotions: List[str],
        should_escalate: bool,
        escalation_reason: Optional[str] = None
    ):
        """Record sentiment analysis result."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO messages (
                    id, conversation_id, sentiment_score, sentiment_label,
                    emotions, should_escalate, escalation_reason
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    sentiment_score = $3,
                    sentiment_label = $4,
                    emotions = $5,
                    should_escalate = $6,
                    escalation_reason = $7
                """,
                message_id, conversation_id, sentiment_score, sentiment_label,
                emotions, should_escalate, escalation_reason
            )
    
    async def get_conversation_sentiment_trend(
        self,
        conversation_id: str
    ) -> List[Dict]:
        """Get sentiment trend for a conversation."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT message_id, sentiment_score, sentiment_label, created_at
                FROM messages
                WHERE conversation_id = $1
                AND sentiment_score IS NOT NULL
                ORDER BY created_at
                """,
                conversation_id
            )
            return [dict(row) for row in rows]
    
    async def get_customer_sentiment_history(
        self,
        customer_id: str,
        days: int = 30
    ) -> Dict:
        """Get customer's sentiment history."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    AVG(sentiment_score) as avg_sentiment,
                    MIN(sentiment_score) as min_sentiment,
                    MAX(sentiment_score) as max_sentiment,
                    COUNT(*) as message_count,
                    COUNT(CASE WHEN should_escalate THEN 1 END) as escalation_count
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                AND m.created_at > NOW() - INTERVAL '%s days'
                AND m.sentiment_score IS NOT NULL
                """,
                customer_id
            )
            return dict(row) if row else None
    
    async def get_sentiment_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        channel: Optional[str] = None
    ) -> Dict:
        """Get sentiment metrics for a time period."""
        async with self.pool.acquire() as conn:
            if channel:
                row = await conn.fetchrow(
                    """
                    SELECT 
                        AVG(m.sentiment_score) as avg_sentiment,
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN m.sentiment_score < 0.3 THEN 1 END) as negative_count,
                        COUNT(CASE WHEN m.sentiment_score > 0.7 THEN 1 END) as positive_count,
                        COUNT(CASE WHEN m.should_escalate THEN 1 END) as escalations
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE m.created_at BETWEEN $1 AND $2
                    AND c.initial_channel = $3
                    """,
                    start_date, end_date, channel
                )
            else:
                row = await conn.fetchrow(
                    """
                    SELECT 
                        AVG(sentiment_score) as avg_sentiment,
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN sentiment_score < 0.3 THEN 1 END) as negative_count,
                        COUNT(CASE WHEN sentiment_score > 0.7 THEN 1 END) as positive_count,
                        COUNT(CASE WHEN should_escalate THEN 1 END) as escalations
                    FROM messages
                    WHERE created_at BETWEEN $1 AND $2
                    """,
                    start_date, end_date
                )
            
            return dict(row) if row else None
```

---

## Sentiment-Based Response Adaptation

```python
# agent/response_adapter.py

from typing import Dict
from .sentiment import SentimentResult, SentimentLabel

class ResponseAdapter:
    """Adapt responses based on customer sentiment."""
    
    # Response templates for different sentiments
    TEMPLATES = {
        SentimentLabel.VERY_NEGATIVE: {
            'opening': "I sincerely apologize for the frustration you've experienced.",
            'tone': "empathetic",
            'closing': "We take your concerns very seriously and will make this right.",
            'escalation_hint': "Consider immediate escalation"
        },
        SentimentLabel.NEGATIVE: {
            'opening': "I understand your concern, and I'm here to help.",
            'tone': "empathetic",
            'closing': "Please let me know if there's anything else I can assist with.",
            'escalation_hint': "Monitor for further decline"
        },
        SentimentLabel.NEUTRAL: {
            'opening': "Thank you for reaching out.",
            'tone': "professional",
            'closing': "Feel free to ask if you have any other questions.",
            'escalation_hint': "Standard support"
        },
        SentimentLabel.POSITIVE: {
            'opening': "Great to hear from you!",
            'tone': "friendly",
            'closing': "We're always here if you need anything else!",
            'escalation_hint': "No escalation needed"
        },
        SentimentLabel.VERY_POSITIVE: {
            'opening': "We're thrilled to help!",
            'tone': "enthusiastic",
            'closing': "Thank you for being a valued customer!",
            'escalation_hint': "Consider feedback request"
        }
    }
    
    @staticmethod
    def adapt_response(
        base_response: str,
        sentiment: SentimentResult,
        channel: str = "email"
    ) -> str:
        """
        Adapt response based on sentiment and channel.
        
        Args:
            base_response: Agent's generated response
            sentiment: Sentiment analysis result
            channel: Communication channel
        
        Returns:
            Adapted response
        """
        template = ResponseAdapter.TEMPLATES.get(sentiment.label)
        
        if not template:
            return base_response
        
        # Add sentiment-appropriate opening
        adapted = f"{template['opening']}\n\n{base_response}"
        
        # Add sentiment-appropriate closing
        adapted = f"{adapted}\n\n{template['closing']}"
        
        # Channel-specific adjustments
        if channel == "whatsapp":
            # Shorten for WhatsApp
            if len(adapted) > 300:
                adapted = adapted[:297] + "..."
        
        return adapted
    
    @staticmethod
    def get_escalation_recommendation(sentiment: SentimentResult) -> Dict:
        """Get escalation recommendation based on sentiment."""
        
        if sentiment.should_escalate:
            return {
                'should_escalate': True,
                'reason': sentiment.escalation_reason,
                'urgency': 'high' if sentiment.score < 0.2 else 'medium',
                'note': f"Sentiment score: {sentiment.score}, Emotions: {sentiment.emotions}"
            }
        
        # Check for declining sentiment
        if sentiment.label == SentimentLabel.NEGATIVE:
            return {
                'should_escalate': False,
                'reason': None,
                'urgency': 'low',
                'note': "Monitor conversation - sentiment is negative but not critical"
            }
        
        return {
            'should_escalate': False,
            'reason': None,
            'urgency': None,
            'note': "No escalation needed"
        }
```

---

## Testing

```python
# tests/test_sentiment.py

import pytest
from agent.sentiment import SentimentAnalyzer, SentimentLabel, Emotion

@pytest.fixture
def analyzer():
    return SentimentAnalyzer(escalation_threshold=0.3)

class TestSentimentAnalysis:
    @pytest.mark.asyncio
    async def test_positive_message(self, analyzer):
        """Test positive message detection."""
        result = await analyzer.analyze(
            "Thank you so much! Your product is amazing and works perfectly!"
        )
        
        assert result.score > 0.5
        assert result.label == SentimentLabel.POSITIVE
        assert not result.should_escalate
        assert Emotion.GRATITUDE in result.emotions
    
    @pytest.mark.asyncio
    async def test_negative_message(self, analyzer):
        """Test negative message detection."""
        result = await analyzer.analyze(
            "This is terrible! Your product is broken and useless. I'm frustrated!"
        )
        
        assert result.score < 0.3
        assert result.label == SentimentLabel.NEGATIVE
        assert result.should_escalate
        assert Emotion.FRUSTRATION in result.emotions
    
    @pytest.mark.asyncio
    async def test_legal_escalation(self, analyzer):
        """Test legal keyword escalation."""
        result = await analyzer.analyze(
            "I want to speak to a lawyer about this issue."
        )
        
        assert result.should_escalate
        assert result.escalation_reason == "legal_concern"
    
    @pytest.mark.asyncio
    async def test_refund_escalation(self, analyzer):
        """Test refund request escalation."""
        result = await analyzer.analyze(
            "I want a refund and want to cancel my subscription."
        )
        
        assert result.should_escalate
        assert result.escalation_reason in ["refund_request", "cancellation_request"]
    
    @pytest.mark.asyncio
    async def test_neutral_message(self, analyzer):
        """Test neutral message."""
        result = await analyzer.analyze(
            "How do I reset my password?"
        )
        
        assert result.label == SentimentLabel.NEUTRAL
        assert not result.should_escalate
    
    @pytest.mark.asyncio
    async def test_conversation_trend_declining(self, analyzer):
        """Test declining conversation trend."""
        messages = [
            {"role": "customer", "content": "Thanks for the help!"},
            {"role": "customer", "content": "This is getting frustrating."},
            {"role": "customer", "content": "This is unacceptable! I'm angry!"}
        ]
        
        trend = await analyzer.analyze_conversation_trend(messages)
        
        assert trend['trend'] == "declining"
        assert trend['recommendation'] == "monitor_closely"
```

---

## Acceptance Criteria

- [ ] Sentiment analyzer detects positive/negative messages
- [ ] Escalation triggers work for all keyword categories
- [ ] Emotion detection identifies customer emotions
- [ ] Sentiment is recorded in database
- [ ] Conversation trend analysis works
- [ ] Response adaptation modifies tone appropriately
- [ ] Channel-specific adjustments applied
- [ ] All tests pass
- [ ] Metrics endpoint provides sentiment statistics

## Related Skills

- `customer-success-agent` - Uses sentiment for escalation
- `postgres-crm-schema` - Stores sentiment scores
- `kafka-event-processing` - Streams sentiment events
- `channel-integrations` - Sentiment per channel

## References

- [NLTK Sentiment Analysis](https://www.nltk.org/)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
