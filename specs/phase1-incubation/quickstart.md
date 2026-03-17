# Quick Start Guide: Phase 1 Incubation

**Purpose**: Get your development environment set up for Phase 1 prototype development.

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Claude Code access (configured)
- Text editor (VS Code recommended)

## Step 1: Create Project Structure

```bash
# Navigate to project root
cd C:\Code-journy\Quator-4\Hackahton-V

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate
```

## Step 2: Install Dependencies

Create `requirements.txt`:

```txt
mcp>=0.1.0
anthropic>=0.10.0
pydantic>=2.0
python-dotenv>=1.0
pytest>=7.0
pytest-asyncio>=0.21
textblob>=0.17
rich>=13.0
```

Install:

```bash
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt
```

## Step 3: Create Context Directory

Create the `context/` directory with 5 required files:

### context/company-profile.md

```markdown
# TechCorp - Developer Platform SaaS

## Company Overview
TechCorp provides a REST API platform for developers to build and deploy applications.

## Product
- REST API with authentication (OAuth 2.0, API keys)
- Webhook configuration and management
- Rate limiting and quota management
- Developer dashboard and analytics

## Plans
- Free: Limited API calls, basic features
- Pro: Higher limits, priority support
- Enterprise: Custom limits, dedicated support (pricing not public)

## Support Model
- AI handles 24/7 routine inquiries
- Human agents: Mon-Fri 9am-6pm EST
- Escalations reviewed within 24 hours
```

### context/product-docs.md

```markdown
# TechCorp Product Documentation

## API Key Management
- Create API keys in Settings > API > Keys
- Rotate keys without downtime
- Delete compromised keys immediately
- Best practice: Use environment variables

## OAuth 2.0 Authentication
- Register your application in Developer Dashboard
- Obtain client_id and client_secret
- Implement authorization code flow
- Refresh tokens valid for 30 days

## Webhooks
- Configure webhook URLs in dashboard
- Automatic retry on failure (3 attempts)
- Verify webhook signatures
- Supported events: user.created, payment.completed, etc.

## Rate Limits
- Free: 100 requests/hour
- Pro: 1000 requests/hour
- Enterprise: Custom limits
- Rate limit headers included in responses

## Data Export
- Export data in CSV or JSON format
- Available in Settings > Data Export
- Processing time: 5-10 minutes
- Download link valid for 24 hours

## Billing & Subscriptions
- Manage subscription in Billing dashboard
- Upgrade/downgrade anytime
- Prorated billing for mid-cycle changes
- Contact support for enterprise pricing

## Common Errors
- 401 Unauthorized: Invalid/expired credentials
- 403 Forbidden: Insufficient permissions
- 429 Too Many Requests: Rate limit exceeded
- 500 Server Error: Contact support
```

### context/sample-tickets.json

```json
[
  {
    "id": 1,
    "channel": "email",
    "customer_email": "john@example.com",
    "content": "How do I reset my API key?",
    "expected_category": "how-to",
    "expected_escalation": false
  },
  {
    "id": 2,
    "channel": "whatsapp",
    "customer_phone": "+1234567890",
    "content": "hey can i export my data?",
    "expected_category": "how-to",
    "expected_escalation": false
  },
  {
    "id": 3,
    "channel": "email",
    "customer_email": "sarah@company.com",
    "content": "What's the price of the Enterprise plan?",
    "expected_category": "pricing_inquiry",
    "expected_escalation": true
  },
  {
    "id": 4,
    "channel": "whatsapp",
    "customer_phone": "+1987654321",
    "content": "This is BROKEN and your support is USELESS!",
    "expected_category": "negative_sentiment",
    "expected_escalation": true
  },
  {
    "id": 5,
    "channel": "web_form",
    "customer_email": "dev@startup.io",
    "content": "I want to speak to a human agent",
    "expected_category": "human_requested",
    "expected_escalation": true
  }
  // Add 45+ more samples...
]
```

### context/escalation-rules.md

```markdown
# Escalation Rules

## Category-Based Triggers

### Pricing Inquiries
- Keywords: "price", "cost", "pricing", "how much", "enterprise plan"
- Action: Create ticket, escalate immediately
- Response: "A specialist will contact you about pricing."

### Legal Threats
- Keywords: "lawyer", "legal", "sue", "attorney", "lawsuit"
- Action: Create ticket, escalate with HIGH urgency
- Response: "Your concern is important. A specialist will review this."

### Refund Requests
- Keywords: "refund", "money back", "chargeback"
- Action: Create ticket, escalate to billing team
- Response: "I'll connect you with our billing team."

## Sentiment-Based Triggers

- Sentiment score < 0.3 → Escalate
- Multiple negative keywords → Escalate
- Frustrated tone + threat to leave → Escalate

## Channel-Specific Triggers

### WhatsApp
- "human", "agent", "representative", "real person"
- Short, angry messages with exclamation marks

### Email
- Formal complaint language
- CC to multiple recipients
- Threatening legal action

## Fallback Rule

- 2 failed knowledge base searches → Escalate
- "I don't know" response → Escalate
```

### context/brand-voice.md

```markdown
# Brand Voice Guidelines

## Core Values

1. **Speed**: Respond quickly, get to the point
2. **Empathy**: Acknowledge frustration, show understanding
3. **Accuracy**: Only state verified facts from documentation

## Tone Per Channel

### Email (Formal)
- Greeting: "Dear [Name]," or "Dear Customer,"
- Body: Structured paragraphs, complete sentences
- Closing: "Best regards, TechCorp AI Support Team"
- Length: Up to 500 words, detailed

### WhatsApp (Conversational)
- No formal greeting needed
- Casual, friendly tone
- Emoji optional (sparingly)
- Length: Under 300 chars (preferred 160)
- Example: "Hey! To reset your API key, go to Settings > API > Keys 👍"

### Web Form (Semi-Formal)
- Friendly but professional
- Structured paragraphs
- No signature needed
- Length: Up to 300 words

## What NOT to Say

❌ "I apologize for the inconvenience" (hollow apology)
❌ "As an AI..." (breaks immersion)
❌ "I think..." or "I believe..." (state facts only)
❌ Technical jargon without explanation
❌ Competitor comparisons

## Response Patterns

### Good Opening
- "Thank you for reaching out."
- "I can help with that."
- "Great question!"

### Good Closing
- "Let me know if you need anything else!"
- "Happy to help further if needed."
- "Is there anything else I can clarify?"

### Empathy Statements
- "I understand this is frustrating."
- "I can see why this would be confusing."
- "Thanks for your patience."
```

## Step 4: Verify Setup

Run this verification script:

```python
# verify_setup.py
import os
import sys

def verify():
    print("Verifying Phase 1 setup...")
    
    # Check Python version
    assert sys.version_info >= (3, 11), "Python 3.11+ required"
    print("✅ Python version OK")
    
    # Check context files
    context_files = [
        "context/company-profile.md",
        "context/product-docs.md",
        "context/sample-tickets.json",
        "context/escalation-rules.md",
        "context/brand-voice.md"
    ]
    
    for f in context_files:
        assert os.path.exists(f), f"Missing: {f}"
    print("✅ All context files present")
    
    # Check dependencies
    try:
        import mcp
        import anthropic
        import pydantic
        import pytest
        print("✅ Dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    print("\n✅ Setup complete! Ready for Exercise 1.1")
    return True

if __name__ == "__main__":
    verify()
```

Run:

```bash
python verify_setup.py
```

## Step 5: Start Development

Begin with **Exercise 1.1: Initial Exploration** (2-3 hours):

1. Open Claude Code
2. Provide initial intent prompt (see specs/phase1-incubation/plan.md)
3. Let Claude Code explore the problem space
4. Document discoveries in `specs/discovery-log.md`

## Next Steps

After setup:

1. ✅ Exercise 1.0: Setup verification (30 min)
2. 📝 Exercise 1.1: Initial exploration (2-3 hrs)
3. 🔧 Exercise 1.2: Prototype core loop (4-5 hrs)
4. 💾 Exercise 1.3: Add memory (3-4 hrs)
5. 🔌 Exercise 1.4: Build MCP server (3-4 hrs)
6. 📋 Exercise 1.5: Define agent skills (2-3 hrs)
7. ✅ Exit: Crystallize spec (1 hr)

## Troubleshooting

**Issue**: Claude Code not configured
**Solution**: Follow Claude Code setup instructions, ensure API access

**Issue**: Import errors
**Solution**: Ensure virtual environment is activated, reinstall dependencies

**Issue**: Context files missing
**Solution**: Create all 5 files in context/ directory before starting

## Resources

- **Spec**: specs/phase1-incubation/spec.md
- **Plan**: specs/phase1-incubation/plan.md
- **Data Model**: specs/phase1-incubation/data-model.md
- **MCP Tools**: specs/phase1-incubation/contracts/mcp-tools.md
