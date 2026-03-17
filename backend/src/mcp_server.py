"""MCP Server for Customer Success FTE with all 6 tools."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from mcp.server import Server
from src.agent.knowledge_base import KnowledgeBase
from src.agent.memory import ConversationMemoryStore, ConversationTurn
from src.agent.sentiment import SentimentAnalyzer

logger = logging.getLogger(__name__)

# Create MCP server
server = Server("customer-success-fte")

# Initialize components
knowledge_base = KnowledgeBase()
memory_store = ConversationMemoryStore()
sentiment_analyzer = SentimentAnalyzer()

# In-memory ticket store for Phase 1
tickets = {}
escalations = {}


@server.tool("search_knowledge_base")
async def search_knowledge_base(query: str, max_results: int = 5, category: Optional[str] = None) -> str:
    """
    Search product documentation for relevant information.
    
    Use this tool when: Customer asks product questions, how-to inquiries, or technical information needs.
    
    Args:
        query: Customer's search query
        max_results: Maximum number of results to return (default: 5)
        category: Optional category filter (how-to, troubleshooting, feature, faq)
    
    Returns:
        Formatted string of relevant document sections with relevance scores,
        or "No relevant documentation found. Consider escalating to human support." if no matches.
    
    Example return: "**API Key Management** (relevance: 0.92)\nTo reset your API key..."
    """
    try:
        logger.info(f"Searching knowledge base for: {query}")
        results = knowledge_base.search(query, max_results)
        return results
    except Exception as e:
        logger.error(f"Knowledge base search failed: {e}")
        return "Knowledge base temporarily unavailable. Consider escalating to human support."


@server.tool("create_ticket")
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "medium",
    channel: str = "email"
) -> str:
    """
    Create a support ticket in the system with channel tracking.
    
    Use this tool when: Receiving ANY customer message. This MUST be called before any response is sent.
    
    Args:
        customer_id: Unique customer identifier (email or phone)
        issue: Customer issue description
        priority: Ticket priority level (low, medium, high, critical)
        channel: Channel the customer used (email, whatsapp, web_form)
    
    Returns:
        The created ticket ID (e.g., "ticket_cust123_1711234567")
    
    Example return: "ticket_cust123_1711234567"
    """
    try:
        ticket_id = f"ticket_{customer_id}_{int(datetime.utcnow().timestamp())}"
        
        tickets[ticket_id] = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "issue": issue,
            "priority": priority,
            "channel": channel,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Created ticket {ticket_id} for customer {customer_id}")
        return ticket_id
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        return f"ticket_error_{customer_id}"


@server.tool("get_customer_history")
async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """
    Get customer's interaction history across ALL channels.
    
    Use this tool when: You need to understand customer context before responding, or customer asks follow-up questions.
    
    Args:
        customer_id: Unique customer identifier
        limit: Number of recent interactions to return (default: 10)
    
    Returns:
        Formatted customer history including past conversations across all channels,
        or "No prior interaction history." if customer is new.
    
    Example return: "[EMAIL] customer: How do I reset my API key?\n[AGENT]: To reset your API key..."
    """
    try:
        logger.info(f"Retrieving history for customer {customer_id}")
        history = memory_store.get_history_text(customer_id, limit)
        return history
    except Exception as e:
        logger.error(f"Failed to get customer history: {e}")
        return "Unable to retrieve customer history. Proceeding as new customer."


@server.tool("escalate_to_human")
async def escalate_to_human(
    ticket_id: str,
    reason: str,
    context: str,
    urgency: str = "medium"
) -> str:
    """
    Escalate a ticket to human support.
    
    Use this tool when: Customer asks about pricing, mentions legal action, requests refund, has negative sentiment, or explicitly requests human.
    
    Args:
        ticket_id: Ticket to escalate
        reason: Reason for escalation (pricing_inquiry, legal_concern, refund_request, negative_sentiment, human_requested, no_information)
        context: Summary of the conversation context
        urgency: Escalation urgency (low, medium, high)
    
    Returns:
        Escalation ID and next steps confirmation.
    
    Example return: "Escalation created successfully. Escalation ID: esc_ticket123. Reason: pricing_inquiry. A human agent will review this within 24 hours."
    """
    try:
        escalation_id = f"esc_{ticket_id}"
        
        escalations[escalation_id] = {
            "escalation_id": escalation_id,
            "ticket_id": ticket_id,
            "reason": reason,
            "context": context,
            "urgency": urgency,
            "escalated_at": datetime.utcnow().isoformat(),
        }
        
        # Update ticket status
        if ticket_id in tickets:
            tickets[ticket_id]["status"] = "escalated"
        
        # Mark memory as escalated
        if ticket_id in tickets:
            customer_id = tickets[ticket_id]["customer_id"]
            memory_store.mark_escalated(customer_id)
        
        logger.info(f"Escalated ticket {ticket_id} with reason {reason}")
        
        return (
            f"Escalation created successfully.\n"
            f"Escalation ID: {escalation_id}\n"
            f"Reason: {reason}\n"
            f"Urgency: {urgency}\n"
            f"A human agent will review this within 24 hours."
        )
    except Exception as e:
        logger.error(f"Failed to escalate: {e}")
        return f"Escalation failed: {str(e)}. Please inform the customer a human will contact them."


@server.tool("send_response")
async def send_response(
    ticket_id: str,
    message: str,
    channel: str,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None
) -> str:
    """
    Send response to the customer via the appropriate channel.
    
    Use this tool when: You have generated a response and are ready to send it to the customer. This is the FINAL tool to call.
    
    Args:
        ticket_id: Ticket ID to respond to
        message: Response message (should already be formatted for channel)
        channel: Channel to send via (email, whatsapp, web_form)
        customer_email: Customer email (for email channel)
        customer_phone: Customer phone (for WhatsApp)
    
    Returns:
        Delivery status confirmation.
    
    Example return: "Response sent successfully via email. Status: delivered"
    """
    try:
        # Update ticket status
        if ticket_id in tickets:
            tickets[ticket_id]["status"] = "responded"
            tickets[ticket_id]["responded_at"] = datetime.utcnow().isoformat()
        
        # In Phase 1, we just log the response (no actual sending)
        logger.info(f"Response sent via {channel} for ticket {ticket_id}")
        logger.debug(f"Message: {message[:200]}...")
        
        return f"Response sent successfully via {channel}. Status: delivered"
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
        return f"Failed to send response: {str(e)}. Please try again or escalate."


@server.tool("analyze_sentiment")
async def analyze_sentiment(text: str) -> str:
    """
    Analyze customer sentiment in a message.
    
    Use this tool when: Every incoming customer message to determine emotional state and escalation need.
    
    Args:
        text: Customer message to analyze
    
    Returns:
        Sentiment analysis result with score (0.0-1.0), label (positive/neutral/negative), and escalation recommendation.
    
    Example return: "Score: 0.15 | Label: negative | Should Escalate: True | Reason: negative_sentiment"
    """
    try:
        score, label = sentiment_analyzer.analyze(text)
        should_escalate = sentiment_analyzer.should_escalate(score)
        reason = "negative_sentiment" if should_escalate else ""
        
        result = (
            f"Score: {score:.2f} | "
            f"Label: {label} | "
            f"Should Escalate: {should_escalate}"
        )
        
        if should_escalate:
            result += f" | Reason: {reason}"
        
        logger.debug(f"Sentiment analysis: {result}")
        return result
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "Score: 0.50 | Label: neutral | Should Escalate: False"


# Server entry point
if __name__ == "__main__":
    import mcp.server.stdio
    
    logger.info("Starting Customer Success FTE MCP Server...")
    logger.info("Available tools: search_knowledge_base, create_ticket, get_customer_history, escalate_to_human, send_response, analyze_sentiment")
    
    mcp.server.stdio.run_server(server)
