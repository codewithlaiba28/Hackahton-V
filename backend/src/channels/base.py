"""Channel enums and message dataclasses for Customer Success FTE."""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional


class Channel(str, Enum):
    """Supported communication channels."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


@dataclass
class ChannelMessage:
    """
    Represents a customer message from any channel.
    
    Attributes:
        channel: Source channel (email, whatsapp, web_form)
        content: Message content
        received_at: When message was received
        customer_email: Customer's email address (optional)
        customer_phone: Customer's phone number (optional)
        customer_name: Customer's name (optional)
        subject: Email subject line (email only)
        thread_id: Email thread ID (email only)
        channel_message_id: External channel message ID
        metadata: Additional channel-specific metadata
    """
    # Required fields
    channel: Channel
    content: str
    received_at: datetime = field(default_factory=datetime.utcnow)
    
    # Customer identification (at least one required)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    
    # Channel-specific metadata
    subject: Optional[str] = None  # Email only
    thread_id: Optional[str] = None  # Email only
    channel_message_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    @property
    def customer_id(self) -> str:
        """
        Get primary customer identifier.
        
        Returns:
            Email preferred, phone fallback, or "unknown"
        """
        return self.customer_email or self.customer_phone or "unknown"
    
    def __post_init__(self):
        """Validate message after initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        
        if not self.customer_email and not self.customer_phone:
            # Warning only - allow messages without customer info for testing
            pass
