"""Core agent interaction loop for Customer Success FTE."""

import logging
import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.channels.base import Channel, ChannelMessage
from src.agent.normalizer import NormalizedMessage, MessageNormalizer
from src.agent.knowledge_base import KnowledgeBase
from src.agent.sentiment import SentimentAnalyzer
from src.agent.escalation import EscalationChecker
from src.agent.formatter import ChannelFormatter
from src.agent.memory import ConversationMemoryStore, ConversationTurn
from src.agent.prompts import SYSTEM_PROMPT, CHANNEL_INSTRUCTIONS

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """
    Result from agent processing.
    
    Attributes:
        ticket_id: Created ticket ID
        response: Formatted response for customer
        channel: Target channel
        escalated: Whether escalation was triggered
        escalation_reason: Reason code if escalated
        sentiment_score: Computed sentiment score
        tool_calls: List of tool calls made during processing
    """
    ticket_id: str
    response: str
    channel: str
    escalated: bool = False
    escalation_reason: Optional[str] = None
    sentiment_score: float = 0.5
    tool_calls: list = field(default_factory=list)


class CoreAgentLoop:
    """
    Main agent processing pipeline.
    
    Orchestrates all components: normalizer, knowledge base, sentiment,
    escalation, formatter, and memory.
    """
    
    def __init__(self):
        """Initialize core agent loop with all components."""
        self.memory_store = ConversationMemoryStore()
        self.normalizer = MessageNormalizer(self.memory_store)
        self.knowledge_base = KnowledgeBase()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.escalation_checker = EscalationChecker()
        self.formatter = ChannelFormatter()
        
        # In-memory ticket store (Phase 1 only)
        self.tickets: Dict[str, Dict] = {}
        
        logger.info("Core agent loop initialized")
    
    def process_message(self, message: ChannelMessage) -> AgentResult:
        """
        Process customer message through complete pipeline.
        
        Args:
            message: Raw ChannelMessage from channel simulator
            
        Returns:
            AgentResult with response and metadata
        """
        logger.info(f"Processing message from channel={message.channel}, customer={message.customer_id}")
        
        # Step 1: Create ticket (REQUIRED before any response)
        ticket_id = self._create_ticket(message)
        logger.debug(f"Created ticket {ticket_id}")
        
        # Step 2: Normalize message
        normalized = self.normalizer.normalize(message)
        logger.debug(f"Normalized: intent={normalized.intent_hint}, followup={normalized.is_followup}")
        
        # Step 3: Get customer history
        history_text = self.memory_store.get_history_text(message.customer_id)
        logger.debug(f"Retrieved history: {len(history_text)} chars")
        
        # Step 4: Analyze sentiment
        sentiment_score, sentiment_label = self.sentiment_analyzer.analyze(normalized.content)
        logger.debug(f"Sentiment: {sentiment_score:.2f} ({sentiment_label})")
        
        # Step 5: Check escalation
        should_escalate, escalation_reason = self.escalation_checker.check_escalation(
            normalized.content,
            sentiment_score,
            message.channel.value
        )
        
        if should_escalate:
            logger.info(f"Escalation triggered: {escalation_reason}")
            return self._handle_escalation(ticket_id, escalation_reason, message)
        
        # Step 6: Search knowledge base
        kb_results = self.knowledge_base.search(normalized.content, max_results=5)
        logger.debug(f"KB results: {len(kb_results)} chars")
        
        # Step 7: Generate response (simulated LLM for Phase 1)
        response_text = self._generate_response(
            normalized=normalized,
            history=history_text,
            kb_results=kb_results,
            sentiment_label=sentiment_label
        )
        
        # Step 8: Format response for channel
        formatted_response = self.formatter.format_response(
            response=response_text,
            channel=message.channel.value,
            customer_name=message.customer_name,
            ticket_id=ticket_id
        )
        
        # Step 9: Update memory
        self._update_memory(message, normalized, formatted_response, sentiment_score)
        
        # Step 10: Update ticket status
        self._update_ticket(ticket_id, "responded")
        
        # Build result
        result = AgentResult(
            ticket_id=ticket_id,
            response=formatted_response,
            channel=message.channel.value,
            escalated=False,
            sentiment_score=sentiment_score,
            tool_calls=["create_ticket", "get_customer_history", "search_knowledge_base", "send_response"]
        )
        
        logger.info(f"Processing complete: ticket={ticket_id}, escalated=False")
        return result
    
    def _create_ticket(self, message: ChannelMessage) -> str:
        """Create ticket in memory store."""
        ticket_id = f"ticket_{message.customer_id}_{int(datetime.utcnow().timestamp())}"
        
        self.tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "customer_id": message.customer_id,
            "source_channel": message.channel.value,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "issue": message.content[:200],  # First 200 chars
        }
        
        return ticket_id
    
    def _update_ticket(self, ticket_id: str, status: str):
        """Update ticket status."""
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = status
            if status == "resolved":
                self.tickets[ticket_id]["resolved_at"] = datetime.utcnow().isoformat()
    
    def _handle_escalation(
        self,
        ticket_id: str,
        reason: str,
        message: ChannelMessage
    ) -> AgentResult:
        """
        Handle escalation scenario.
        
        Args:
            ticket_id: Ticket to escalate
            reason: Escalation reason code
            message: Original message
            
        Returns:
            AgentResult with escalation response
        """
        # Update ticket status
        self._update_ticket(ticket_id, "escalated")
        
        # Mark memory as escalated
        self.memory_store.mark_escalated(message.customer_id)
        
        # Get escalation response
        escalation_response = self.escalation_checker.get_escalation_response(reason)
        
        # Format for channel
        formatted_response = self.formatter.format_response(
            response=escalation_response,
            channel=message.channel.value,
            customer_name=message.customer_name,
            ticket_id=ticket_id
        )
        
        # Update memory
        turn = ConversationTurn(
            role="agent",
            content=formatted_response,
            channel=message.channel.value,
            tool_calls=["create_ticket", "escalate_to_human"]
        )
        self.memory_store.add_turn(message.customer_id, turn)
        
        return AgentResult(
            ticket_id=ticket_id,
            response=formatted_response,
            channel=message.channel.value,
            escalated=True,
            escalation_reason=reason,
            tool_calls=["create_ticket", "escalate_to_human"]
        )
    
    def _generate_response(
        self,
        normalized: NormalizedMessage,
        history: str,
        kb_results: str,
        sentiment_label: str
    ) -> str:
        """
        Generate response text (simulated LLM for Phase 1).
        
        In Phase 2, this will call actual LLM via Anthropic SDK.
        
        Args:
            normalized: Normalized message
            history: Conversation history
            kb_results: Knowledge base results
            sentiment_label: Sentiment label
            
        Returns:
            Response text
        """
        # Simple template-based response for Phase 1
        intent = normalized.intent_hint
        
        if intent == "general":
            return f"Based on our documentation: {kb_results[:300]}"
        elif intent == "pricing":
            return "For pricing information, I'll connect you with our sales team."
        elif intent == "refund":
            return "I'll connect you with our billing team to assist with your request."
        else:
            # Use KB results
            if "No relevant documentation" in kb_results:
                return "Let me look into this further and get back to you with detailed information."
            else:
                return f"Here's what I found: {kb_results[:300]}"
    
    def _update_memory(
        self,
        message: ChannelMessage,
        normalized: NormalizedMessage,
        response: str,
        sentiment_score: float
    ):
        """Update conversation memory with both turns."""
        # Add customer turn
        customer_turn = ConversationTurn(
            role="customer",
            content=normalized.content,
            channel=message.channel.value,
            sentiment_score=sentiment_score
        )
        self.memory_store.add_turn(message.customer_id, customer_turn)
        
        # Add agent turn
        agent_turn = ConversationTurn(
            role="agent",
            content=response,
            channel=message.channel.value,
            tool_calls=["create_ticket", "send_response"]
        )
        self.memory_store.add_turn(message.customer_id, agent_turn)
