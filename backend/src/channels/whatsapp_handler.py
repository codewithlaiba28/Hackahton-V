"""Production WhatsApp handler using Twilio for Customer Success FTE."""

import os
import logging
from typing import Dict, Any, Optional
from src.channels.base import Channel, ChannelMessage

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    """Production handler for WhatsApp (Twilio) integration."""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Default sandbox
        
        self.client = None
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio WhatsApp client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
        else:
            logger.warning("Twilio credentials not found or library missing. Running in mock mode.")

    def parse_webhook(self, form_data: Dict[str, Any]) -> ChannelMessage:
        """Parse incoming Twilio webhook data into ChannelMessage."""
        
        # Twilio sends data as form-urlencoded, parsed into dict by FastAPI
        message_body = form_data.get("Body", "")
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        message_sid = form_data.get("MessageSid", "")
        profile_name = form_data.get("ProfileName", "WhatsApp User")
        
        return ChannelMessage(
            channel=Channel.WHATSAPP,
            content=message_body,
            customer_phone=from_number,
            customer_name=profile_name,
            channel_message_id=message_sid,
            metadata={
                "wa_id": form_data.get("WaId"),
                "sms_message_sid": form_data.get("SmsMessageSid")
            }
        )

    async def send_response(self, customer_phone: str, body: str) -> bool:
        """Send a WhatsApp message via Twilio."""
        if not self.client:
            logger.info(f"[MOCK WHATSAPP] To: {customer_phone}, Body: {body}")
            return True

        # Ensure correct formatting
        if not customer_phone.startswith("whatsapp:"):
            # Assuming E.164 format
            customer_phone = f"whatsapp:{customer_phone}"

        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=customer_phone
            )
            logger.info(f"WhatsApp message sent: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
