"""Core agent loop tests for Customer Success FTE."""

import pytest
from src.channels.base import Channel, ChannelMessage
from src.agent.core_loop import CoreAgentLoop
from datetime import datetime


@pytest.fixture
def agent_loop():
    """Create agent loop instance for testing."""
    return CoreAgentLoop()


@pytest.fixture
def sample_messages():
    """Sample test messages for all channels."""
    return {
        "web_form": ChannelMessage(
            channel=Channel.WEB_FORM,
            content="How do I reset my API key?",
            customer_email="test@example.com",
            customer_name="Test User",
            subject="API Key Reset"
        ),
        "whatsapp": ChannelMessage(
            channel=Channel.WHATSAPP,
            content="hey can i export my data?",
            customer_phone="+1234567890"
        ),
        "email": ChannelMessage(
            channel=Channel.EMAIL,
            content="Dear Support, I need a detailed walkthrough of the OAuth 2.0 authentication flow. Can you provide step-by-step instructions?",
            customer_email="developer@company.com",
            customer_name="Developer",
            subject="OAuth 2.0 Help"
        ),
        "pricing": ChannelMessage(
            channel=Channel.EMAIL,
            content="What's the price of the Enterprise plan?",
            customer_email="pricing@company.com"
        ),
        "angry": ChannelMessage(
            channel=Channel.WHATSAPP,
            content="This is BROKEN and your support is USELESS!",
            customer_phone="+1987654321"
        ),
        "human_request": ChannelMessage(
            channel=Channel.WHATSAPP,
            content="I want to speak to a human agent",
            customer_phone="+1122334455"
        ),
        "followup": ChannelMessage(
            channel=Channel.EMAIL,
            content="Following up on my API key question, what about OAuth?",
            customer_email="test@example.com"
        )
    }


class TestWebFormScenario:
    """Test Scenario 1: Product Question via Web Form."""
    
    def test_web_form_ticket_created(self, agent_loop, sample_messages):
        """Ticket must be created before response."""
        result = agent_loop.process_message(sample_messages["web_form"])
        
        assert result.ticket_id.startswith("ticket_")
        assert result.ticket_id in agent_loop.tickets
    
    def test_web_form_response_length(self, agent_loop, sample_messages):
        """Response must be under 300 words."""
        result = agent_loop.process_message(sample_messages["web_form"])
        
        words = result.response.split()
        assert len(words) <= 300
    
    def test_web_form_semi_formal_tone(self, agent_loop, sample_messages):
        """Response should be semi-formal."""
        result = agent_loop.process_message(sample_messages["web_form"])
        
        # Should not have email-style greeting
        assert "Dear" not in result.response or "support portal" in result.response


class TestWhatsAppScenario:
    """Test Scenario 2: Casual WhatsApp Inquiry."""
    
    def test_whatsapp_response_length(self, agent_loop, sample_messages):
        """Response must be under 300 characters."""
        result = agent_loop.process_message(sample_messages["whatsapp"])
        
        assert len(result.response) <= 300
    
    def test_whatsapp_conversational_tone(self, agent_loop, sample_messages):
        """Response should be conversational."""
        result = agent_loop.process_message(sample_messages["whatsapp"])
        
        # Should have WhatsApp support prompt
        assert "human" in result.response.lower() or "📱" in result.response


class TestEmailScenario:
    """Test Scenario 3: Detailed Email Inquiry."""
    
    def test_email_greeting_and_signature(self, agent_loop, sample_messages):
        """Response must include greeting and signature."""
        result = agent_loop.process_message(sample_messages["email"])
        
        assert "Dear" in result.response or "Hello" in result.response
        assert "regards" in result.response.lower() or "Support" in result.response


class TestPricingEscalation:
    """Test Scenario 4: Pricing Inquiry Escalation."""
    
    def test_pricing_escalates(self, agent_loop, sample_messages):
        """Pricing questions must escalate."""
        result = agent_loop.process_message(sample_messages["pricing"])
        
        assert result.escalated is True
        assert result.escalation_reason == "pricing_inquiry"
    
    def test_pricing_no_answer(self, agent_loop, sample_messages):
        """Pricing must NOT be answered."""
        result = agent_loop.process_message(sample_messages["pricing"])
        
        # Should not contain actual pricing
        assert "$" not in result.response
        assert "sales" in result.response.lower() or "connect" in result.response.lower()


class TestAngryCustomerEscalation:
    """Test Scenario 5: Angry Customer Escalation."""
    
    def test_negative_sentiment_escalates(self, agent_loop, sample_messages):
        """Negative sentiment must escalate."""
        result = agent_loop.process_message(sample_messages["angry"])
        
        assert result.escalated is True
        assert result.escalation_reason == "negative_sentiment"
    
    def test_angry_empathy_response(self, agent_loop, sample_messages):
        """Should respond with empathy."""
        result = agent_loop.process_message(sample_messages["angry"])
        
        assert "understand" in result.response.lower() or "frustration" in result.response.lower()


class TestHumanRequestEscalation:
    """Test Scenario 6: Human Escalation Request."""
    
    def test_human_request_escalates(self, agent_loop, sample_messages):
        """Human requests must escalate immediately."""
        result = agent_loop.process_message(sample_messages["human_request"])
        
        assert result.escalated is True
        assert result.escalation_reason == "human_requested"


class TestFollowUpScenario:
    """Test Scenario 7: Follow-Up on Same Topic."""
    
    def test_followup_retrieves_history(self, agent_loop, sample_messages):
        """Follow-up should retrieve prior context."""
        # First message
        first_msg = ChannelMessage(
            channel=Channel.EMAIL,
            content="How do I reset my API key?",
            customer_email="followup@example.com"
        )
        agent_loop.process_message(first_msg)
        
        # Follow-up message
        result = agent_loop.process_message(sample_messages["followup"])
        
        # Should not be escalated (normal follow-up)
        assert result.escalated is False


class TestChannelDetection:
    """Test channel detection accuracy."""
    
    def test_all_channels_detected(self, agent_loop, sample_messages):
        """All three channels should be correctly detected."""
        for channel_name, message in sample_messages.items():
            if channel_name in ["pricing", "angry", "human_request", "followup"]:
                continue
            
            result = agent_loop.process_message(message)
            assert result.channel == message.channel.value
