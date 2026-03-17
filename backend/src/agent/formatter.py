"""Channel-specific response formatter for Customer Success FTE."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChannelFormatter:
    """
    Formats responses based on channel requirements.
    
    Each channel has different tone, length, and formatting requirements.
    """
    
    # Channel-specific limits
    EMAIL_MAX_WORDS = 500
    WHATSAPP_MAX_CHARS = 300
    WHATSAPP_PREFERRED_CHARS = 160
    WEB_FORM_MAX_WORDS = 300
    
    @staticmethod
    def format_response(
        response: str,
        channel: str,
        customer_name: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> str:
        """
        Format response for specific channel.
        
        Args:
            response: AI-generated response text
            channel: Target channel (email, whatsapp, web_form)
            customer_name: Optional customer name for personalization
            ticket_id: Optional ticket reference number
            
        Returns:
            Formatted response appropriate for channel
        """
        if channel == "email":
            return ChannelFormatter._format_email(response, customer_name, ticket_id)
        elif channel == "whatsapp":
            return ChannelFormatter._format_whatsapp(response)
        elif channel == "web_form":
            return ChannelFormatter._format_web_form(response, ticket_id)
        else:
            logger.warning(f"Unknown channel: {channel}, using web_form format")
            return ChannelFormatter._format_web_form(response, ticket_id)
    
    @staticmethod
    def _format_email(
        response: str,
        customer_name: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> str:
        """
        Format response for email channel.
        
        Args:
            response: AI-generated response
            customer_name: Customer name for greeting
            ticket_id: Ticket reference number
            
        Returns:
            Formal email with greeting and signature
        """
        greeting = f"Dear {customer_name}," if customer_name else "Dear Customer,"
        
        # Truncate if too long
        words = response.split()
        if len(words) > ChannelFormatter.EMAIL_MAX_WORDS:
            response = " ".join(words[:ChannelFormatter.EMAIL_MAX_WORDS]) + "..."
        
        ticket_ref = f"\n---\nTicket: {ticket_id}" if ticket_id else ""
        
        formatted = f"""{greeting}

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp AI Support Team{ticket_ref}"""
        
        return formatted
    
    @staticmethod
    def _format_whatsapp(response: str) -> str:
        """
        Format response for WhatsApp channel.
        
        Args:
            response: AI-generated response
            
        Returns:
            Concise, conversational response
        """
        # Truncate if too long
        if len(response) > ChannelFormatter.WHATSAPP_MAX_CHARS:
            response = response[:ChannelFormatter.WHATSAPP_MAX_CHARS - 3] + "..."
        
        # Add support prompt
        formatted = f"{response}\n\n📱 Type 'human' for live support."
        
        return formatted
    
    @staticmethod
    def _format_web_form(response: str, ticket_id: Optional[str] = None) -> str:
        """
        Format response for web form channel.
        
        Args:
            response: AI-generated response
            ticket_id: Ticket reference number
            
        Returns:
            Semi-formal structured response
        """
        # Truncate if too long
        words = response.split()
        if len(words) > ChannelFormatter.WEB_FORM_MAX_WORDS:
            response = " ".join(words[:ChannelFormatter.WEB_FORM_MAX_WORDS]) + "..."
        
        ticket_ref = f"\n---\nTicket: {ticket_id}" if ticket_id else ""
        
        formatted = f"""{response}

---
Need more help? Reply to this message or visit our support portal.{ticket_ref}"""
        
        return formatted
