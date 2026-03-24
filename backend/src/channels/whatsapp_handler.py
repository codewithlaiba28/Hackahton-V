"""Production WhatsApp handler using Twilio for Customer Success FTE.

IMPORTANT: This handler ONLY supports WhatsApp messaging, NOT SMS.
All phone numbers must be in WhatsApp format (whatsapp:+XXXXXXXXXX).
"""

import os
import logging
from typing import Dict, Any, Optional
from src.channels.base import Channel, ChannelMessage

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioRestException = Exception

logger = logging.getLogger(__name__)

class WhatsAppHandler:
    """
    Production handler for WhatsApp (Twilio) integration.
    
    IMPORTANT: This handler ONLY works with WhatsApp-enabled phone numbers.
    It will NOT send or receive SMS messages.
    
    Requirements:
    - Twilio account with WhatsApp sandbox or business API enabled
    - Phone numbers must be WhatsApp-verified
    - All numbers must use 'whatsapp:' prefix
    """

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")  # REQUIRED, no default
        
        # Validate WhatsApp configuration
        if not self.from_number:
            logger.error("TWILIO_WHATSAPP_NUMBER environment variable is REQUIRED for WhatsApp")
            logger.error("Example: whatsapp:+14155238886 (Twilio sandbox) or your business number")
        elif not self.from_number.startswith("whatsapp:"):
            logger.error(f"TWILIO_WHATSAPP_NUMBER must start with 'whatsapp:' prefix. Got: {self.from_number}")
            self.from_number = f"whatsapp:{self.from_number}"
        
        self.client = None
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token and self.from_number:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                # Test the client and verify WhatsApp capability
                account = self.client.api.accounts(self.account_sid).fetch()
                logger.info(f"Twilio client initialized for WhatsApp")
                logger.info(f"Account: {account.friendly_name}")
                logger.info(f"WhatsApp Number: {self.from_number}")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio WhatsApp client: {e}")
                self.client = None
        else:
            if not self.account_sid or not self.auth_token:
                logger.warning("Twilio credentials not found. Running in MOCK mode.")
            if not self.from_number:
                logger.warning("WhatsApp number not configured. Running in MOCK mode.")

    def parse_webhook(self, form_data: Dict[str, Any]) -> ChannelMessage:
        """
        Parse incoming Twilio WhatsApp webhook data into ChannelMessage.
        
        IMPORTANT: This ONLY processes WhatsApp messages, NOT SMS.
        Twilio sends webhook data as form-urlencoded, which FastAPI parses into a dict.
        
        WhatsApp webhook fields:
        - Body: Message content
        - From: Sender's number (format: whatsapp:+XXXXXXXXXX)
        - MessageSid: Unique message ID
        - ProfileName: Sender's WhatsApp profile name
        - WaId: WhatsApp ID (phone number without prefix)
        """
        message_body = form_data.get("Body", "")
        from_number_raw = form_data.get("From", "")
        message_sid = form_data.get("MessageSid", "")
        profile_name = form_data.get("ProfileName", "WhatsApp User")
        
        # Validate this is a WhatsApp message (not SMS)
        if not from_number_raw.startswith("whatsapp:"):
            logger.warning(f"Received non-WhatsApp message from {from_number_raw}. Ignoring.")
            raise ValueError(f"Only WhatsApp messages are supported. Got: {from_number_raw}")
        
        # Extract phone number (remove 'whatsapp:' prefix)
        from_number = from_number_raw.replace("whatsapp:", "")
        
        # Additional Twilio WhatsApp fields
        wa_id = form_data.get("WaId")  # WhatsApp ID (phone number)
        sms_message_sid = form_data.get("SmsMessageSid")  # Internal Twilio SID

        logger.info(f"✓ WhatsApp message received from {from_number}: {message_body[:50]}...")

        return ChannelMessage(
            channel=Channel.WHATSAPP,
            content=message_body,
            customer_phone=from_number,
            customer_name=profile_name,
            channel_message_id=message_sid,
            metadata={
                "wa_id": wa_id,
                "sms_message_sid": sms_message_sid,
                "raw_from": from_number_raw
            }
        )

    async def send_message(self, customer_phone: str, body: str) -> bool:
        """
        Send a WhatsApp message via Twilio.
        
        IMPORTANT: This ONLY sends WhatsApp messages, NOT SMS.
        The customer_phone MUST be a WhatsApp-enabled number.
        
        Args:
            customer_phone: Customer's phone number (with or without 'whatsapp:' prefix)
                           Must be a WhatsApp-verified number
            body: Message body content (max 4096 characters for WhatsApp)
        
        Returns:
            True if sent successfully, False otherwise
        
        Raises:
            TwilioRestException: If the number is not WhatsApp-enabled
        """
        if not self.client:
            logger.info(f"[MOCK WHATSAPP] To: {customer_phone}, Body: {body[:100]}...")
            logger.info(f"[MOCK WHATSAPP] Would send via Twilio WhatsApp from {self.from_number}")
            logger.info("[MOCK WHATSAPP] NOTE: No SMS will be sent - WhatsApp only")
            return True

        # Validate and format phone number for WhatsApp
        to_number = customer_phone.strip()
        
        # Remove any existing prefix
        if to_number.startswith("whatsapp:"):
            to_number = to_number.replace("whatsapp:", "")
        elif to_number.startswith("+"):
            pass  # Keep E.164 format
        else:
            logger.warning(f"Phone number {to_number} should be in E.164 format (e.g., +923001234567)")
        
        # Add whatsapp: prefix for Twilio WhatsApp API
        to_number_formatted = f"whatsapp:{to_number}"
        
        # Validate from_number
        from_num = self.from_number
        if not from_num.startswith("whatsapp:"):
            from_num = f"whatsapp:{from_num}"

        logger.info(f"📤 Sending WhatsApp message to {to_number_formatted}")
        logger.info(f"   From: {from_num}")
        logger.info(f"   Body: {body[:100]}...")

        try:
            message = self.client.messages.create(
                body=body,
                from_=from_num,
                to=to_number_formatted
            )
            
            # Verify it was sent via WhatsApp (not SMS)
            if hasattr(message, 'messaging_service_sid'):
                logger.info(f"✓ WhatsApp message sent! SID: {message.sid}, Status: {message.status}")
            else:
                logger.info(f"✓ Message sent! SID: {message.sid}, Status: {message.status}")
            
            return True
            
        except TwilioRestException as te:
            # Handle specific WhatsApp errors
            if te.code == 21211:
                logger.error(f"❌ Invalid phone number format: {to_number}")
            elif te.code == 21670:
                logger.error(f"❌ Phone number {to_number} is not a valid WhatsApp user")
            elif te.code == 21675:
                logger.error(f"❌ Phone number {to_number} is not opted-in for WhatsApp")
            else:
                logger.error(f"❌ Twilio WhatsApp error {te.code}: {te.msg}")
            
            return False
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp message: {e}", exc_info=True)
            return False

    async def mark_message_read(self, message_sid: str) -> bool:
        """
        Mark an incoming WhatsApp message as read via Twilio.
        """
        if not self.client:
            logger.info(f"[MOCK WHATSAPP] Would mark message {message_sid} as read")
            return True

        try:
            self.client.messages(message_sid).update(status='read')
            logger.info(f"✓ WhatsApp message {message_sid} marked as read")
            return True
        except Exception as e:
            logger.error(f"❌ Error marking WhatsApp message as read: {e}", exc_info=True)
            return False

    def validate_whatsapp_number(self, phone_number: str) -> bool:
        """
        Validate if a phone number is WhatsApp-enabled.
        
        Args:
            phone_number: Phone number to validate (with or without whatsapp: prefix)
        
        Returns:
            True if the number appears to be WhatsApp-capable
        """
        # Basic format validation
        if not phone_number:
            return False
        
        # Remove prefix for validation
        num = phone_number.replace("whatsapp:", "").strip()
        
        # Must start with + and have digits only
        if not num.startswith("+"):
            logger.warning(f"Phone number {num} should start with + (E.164 format)")
            return False
        
        # Remove + and check if rest are digits
        digits = num[1:].replace("-", "").replace(" ", "").replace(".", "")
        if not digits.isdigit():
            logger.warning(f"Phone number {num} contains non-digit characters")
            return False
        
        # Minimum length check (country code + number)
        if len(digits) < 10:
            logger.warning(f"Phone number {num} is too short")
            return False
        
        return True

    async def send_template_message(self, customer_phone: str, template_name: str, language: str = "en", components: Optional[list] = None) -> bool:
        """
        Send a WhatsApp template message (for business-initiated conversations).
        
        IMPORTANT: This ONLY works for WhatsApp, NOT SMS.
        Template messages can only be sent within 24 hours of customer interaction,
        unless you have approved template messages.
        
        Args:
            customer_phone: Customer's WhatsApp number
            template_name: Name of the WhatsApp template (must be approved by Meta)
            language: Template language code (default: "en")
            components: Optional template components (variables, buttons, etc.)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.info(f"[MOCK WHATSAPP] Template: {template_name}, To: {customer_phone}")
            return True

        # Validate number
        if not self.validate_whatsapp_number(customer_phone):
            logger.error(f"Invalid WhatsApp number: {customer_phone}")
            return False

        to_number = f"whatsapp:{customer_phone.replace('whatsapp:', '')}"
        from_num = self.from_number
        if not from_num.startswith("whatsapp:"):
            from_num = f"whatsapp:{from_num}"

        try:
            # For template messages, we use the content_sid parameter
            message = self.client.messages.create(
                content_sid=template_name,
                from_=from_num,
                to=to_number
            )
            logger.info(f"✓ WhatsApp template message sent! SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error sending WhatsApp template message: {e}", exc_info=True)
            return False
