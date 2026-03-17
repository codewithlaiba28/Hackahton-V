"""Agent skills manifest for Customer Success FTE."""

# Agent Skills Definition
# Each skill defines when to use it, inputs, outputs, and fallback behavior

AGENT_SKILLS = {
    "knowledge_retrieval": {
        "description": "Search product documentation for relevant information",
        "trigger_conditions": [
            "customer asks product question",
            "how-to inquiry",
            "technical information needed",
            "feature question"
        ],
        "inputs": {
            "query": "str - Customer's search query",
            "max_results": "int (optional, default 5) - Maximum results to return",
            "category": "str (optional) - Category filter"
        },
        "outputs": {
            "snippets": "str - Formatted document sections with relevance scores"
        },
        "fallback": "No relevant docs found. Let me connect you with a specialist who has more detailed information.",
        "tool_name": "search_knowledge_base"
    },
    
    "sentiment_analysis": {
        "description": "Analyze customer sentiment to determine emotional state",
        "trigger_conditions": [
            "every incoming customer message"
        ],
        "inputs": {
            "text": "str - Customer message to analyze"
        },
        "outputs": {
            "score": "float (0.0-1.0) - Sentiment score",
            "label": "str - positive/neutral/negative",
            "should_escalate": "bool - Whether escalation is needed"
        },
        "fallback": "Unable to analyze sentiment. Proceeding with caution.",
        "tool_name": "analyze_sentiment"
    },
    
    "escalation_decision": {
        "description": "Determine if customer should be escalated to human support",
        "trigger_conditions": [
            "after response generation",
            "negative sentiment detected",
            "pricing/legal/refund keywords detected",
            "customer requests human"
        ],
        "inputs": {
            "message": "str - Customer message",
            "sentiment_score": "float - Computed sentiment score",
            "channel": "str - Source channel"
        },
        "outputs": {
            "should_escalate": "bool - Whether to escalate",
            "reason": "str - Escalation reason code"
        },
        "fallback": "When in doubt, escalate to ensure customer satisfaction.",
        "tool_name": "escalate_to_human"
    },
    
    "channel_adaptation": {
        "description": "Format response appropriately for the target channel",
        "trigger_conditions": [
            "before sending any response"
        ],
        "inputs": {
            "response": "str - Generated response text",
            "channel": "str - Target channel (email/whatsapp/web_form)",
            "customer_name": "str (optional) - For personalization",
            "ticket_id": "str (optional) - For reference"
        },
        "outputs": {
            "formatted_response": "str - Channel-appropriate response"
        },
        "fallback": "Use web_form format as default if channel unknown.",
        "tool_name": "send_response (includes formatting)"
    },
    
    "customer_identification": {
        "description": "Identify customer and retrieve unified history across channels",
        "trigger_conditions": [
            "every incoming message"
        ],
        "inputs": {
            "message_metadata": "dict - Email, phone, or other identifiers"
        },
        "outputs": {
            "customer_id": "str - Unified customer identifier",
            "history": "str - Conversation history across all channels"
        },
        "fallback": "Treat as new customer if no identifier found.",
        "tool_name": "get_customer_history"
    }
}

# Skill execution order
SKILL_EXECUTION_ORDER = [
    "customer_identification",      # First: Identify customer
    "sentiment_analysis",           # Second: Analyze sentiment
    "knowledge_retrieval",          # Third: Search for answers
    "escalation_decision",          # Fourth: Check if escalation needed
    "channel_adaptation",           # Fifth: Format response
]

# Escalation reason codes
ESCALATION_REASONS = {
    "pricing_inquiry": "Customer asked about pricing, cost, or quotes",
    "legal_concern": "Customer mentioned legal action, lawyer, or lawsuit",
    "refund_request": "Customer requested refund or chargeback",
    "negative_sentiment": "Customer sentiment score below 0.3 threshold",
    "human_requested": "Customer explicitly requested human agent",
    "no_information": "Could not find relevant information after 2 searches",
    "competitor_inquiry": "Customer mentioned competitor products",
}

# Channel-specific response limits
CHANNEL_LIMITS = {
    "email": {
        "max_words": 500,
        "style": "formal",
        "requires_greeting": True,
        "requires_signature": True
    },
    "whatsapp": {
        "max_chars": 300,
        "preferred_chars": 160,
        "style": "conversational",
        "requires_greeting": False,
        "requires_signature": False
    },
    "web_form": {
        "max_words": 300,
        "style": "semi_formal",
        "requires_greeting": False,
        "requires_signature": False
    }
}
