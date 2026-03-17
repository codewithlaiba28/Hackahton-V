"""Channel-specific response formatters."""

from typing import Dict, Optional


def format_for_channel(response: str, channel: str, context: Dict) -> str:
    """
    Format response for specific channel.
    
    Args:
        response: AI-generated response text
        channel: Target channel (email, whatsapp, web_form)
        context: Context dict with customer_email, customer_phone, ticket_id
    
    Returns:
        Formatted response appropriate for channel
    """
    if channel == "email":
        return _format_email(response, context)
    elif channel == "whatsapp":
        return _format_whatsapp(response)
    elif channel == "web_form":
        return _format_web_form(response, context)
    else:
        return _format_web_form(response, context)


def _format_email(response: str, context: Dict) -> str:
    """Format for email channel (formal, detailed)."""
    customer_name = context.get("customer_email", "Customer").split("@")[0]
    ticket_id = context.get("ticket_id", "N/A")
    
    # Truncate if too long (500 words max)
    words = response.split()
    if len(words) > 500:
        response = " ".join(words[:500]) + "..."
    
    return f"""Dear {customer_name},

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp AI Support Team
---
Ticket: {ticket_id}"""


def _format_whatsapp(response: str) -> str:
    """Format for WhatsApp channel (concise, conversational)."""
    # Hard cap at 300 characters
    if len(response) > 300:
        response = response[:297] + "..."
    
    return f"{response}\n\n📱 Type 'human' for live support."


def _format_web_form(response: str, context: Dict) -> str:
    """Format for web form channel (semi-formal)."""
    ticket_id = context.get("ticket_id", "N/A")
    
    # Truncate if too long (300 words max)
    words = response.split()
    if len(words) > 300:
        response = " ".join(words[:300]) + "..."
    
    return f"""{response}

---
Need more help? Reply to this message or visit our support portal.
Ticket: {ticket_id}"""
