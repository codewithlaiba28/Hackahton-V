"""Web form channel simulator for Customer Success FTE."""

from typing import Dict, Any
from datetime import datetime
from src.channels.base import Channel, ChannelMessage


class WebFormSimulator:
    """Simulates web support form for Phase 1 testing."""
    
    @staticmethod
    def parse_submission(raw_submission: Dict[str, Any]) -> ChannelMessage:
        """
        Parse raw web form submission into ChannelMessage.
        
        Args:
            raw_submission: Dictionary with form data
            
        Returns:
            ChannelMessage object with web form fields
        """
        return ChannelMessage(
            channel=Channel.WEB_FORM,
            content=raw_submission.get('content', ''),
            customer_email=raw_submission.get('customer_email'),
            customer_name=raw_submission.get('customer_name'),
            subject=raw_submission.get('subject'),
            channel_message_id=raw_submission.get('id'),
            metadata={
                'expected_escalate': raw_submission.get('expected_escalate', False),
                'expected_topic': raw_submission.get('expected_topic', '')
            }
        )
    
    @staticmethod
    def format_response(response: str, ticket_id: str = None) -> str:
        """
        Format response for web form channel.
        
        Args:
            response: AI-generated response text
            ticket_id: Optional ticket reference number
            
        Returns:
            Structured semi-formal response
        """
        ticket_ref = f"\n---\nTicket: {ticket_id}" if ticket_id else ""
        
        formatted = f"""{response}

---
Need more help? Reply to this message or visit our support portal.{ticket_ref}"""
        
        return formatted
