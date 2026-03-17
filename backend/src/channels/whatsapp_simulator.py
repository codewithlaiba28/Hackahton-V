"""WhatsApp channel simulator for Customer Success FTE."""

from typing import Dict, Any
from datetime import datetime
from src.channels.base import Channel, ChannelMessage


class WhatsAppSimulator:
    """Simulates WhatsApp messaging channel for Phase 1 testing."""
    
    MAX_LENGTH = 300  # Character limit for WhatsApp responses
    PREFERRED_LENGTH = 160  # Preferred length (1 SMS)
    
    @staticmethod
    def parse_message(raw_message: Dict[str, Any]) -> ChannelMessage:
        """
        Parse raw WhatsApp message into ChannelMessage.
        
        Args:
            raw_message: Dictionary with WhatsApp data
            
        Returns:
            ChannelMessage object with WhatsApp-specific fields
        """
        return ChannelMessage(
            channel=Channel.WHATSAPP,
            content=raw_message.get('content', ''),
            customer_phone=raw_message.get('customer_phone'),
            channel_message_id=raw_message.get('id'),
            metadata={
                'expected_escalate': raw_message.get('expected_escalate', False),
                'expected_topic': raw_message.get('expected_topic', '')
            }
        )
    
    @staticmethod
    def format_response(response: str) -> str:
        """
        Format response for WhatsApp channel.
        
        Args:
            response: AI-generated response text
            
        Returns:
            Truncated, conversational response with support prompt
        """
        # Truncate if too long
        if len(response) > WhatsAppSimulator.MAX_LENGTH:
            response = response[:WhatsAppSimulator.MAX_LENGTH - 3] + "..."
        
        # Add support prompt
        formatted = f"{response}\n\n📱 Type 'human' for live support."
        
        return formatted
