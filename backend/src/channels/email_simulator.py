"""Email channel simulator for Customer Success FTE."""

from typing import Dict, Any
from datetime import datetime
from src.channels.base import Channel, ChannelMessage


class EmailSimulator:
    """Simulates Gmail email channel for Phase 1 testing."""
    
    @staticmethod
    def parse_email(raw_email: Dict[str, Any]) -> ChannelMessage:
        """
        Parse raw email data into ChannelMessage.
        
        Args:
            raw_email: Dictionary with email data from sample-tickets.json
            
        Returns:
            ChannelMessage object with email-specific fields populated
        """
        return ChannelMessage(
            channel=Channel.EMAIL,
            content=raw_email.get('content', ''),
            customer_email=raw_email.get('customer_email'),
            customer_name=raw_email.get('customer_name'),
            subject=raw_email.get('subject'),
            channel_message_id=raw_email.get('id'),
            metadata={
                'expected_escalate': raw_email.get('expected_escalate', False),
                'expected_topic': raw_email.get('expected_topic', '')
            }
        )
    
    @staticmethod
    def format_response(message: ChannelMessage, response: str) -> str:
        """
        Format response for email channel.
        
        Args:
            message: Original customer message
            response: AI-generated response text
            
        Returns:
            Formatted email with greeting and signature
        """
        greeting = f"Dear {message.customer_name}," if message.customer_name else "Dear Customer,"
        
        formatted = f"""{greeting}

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reach out.

Best regards,
TechCorp AI Support Team
---
Ticket: {message.channel_message_id or 'N/A'}"""
        
        return formatted
