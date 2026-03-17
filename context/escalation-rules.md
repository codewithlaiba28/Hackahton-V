# Escalation Rules

## Purpose

This document defines when the AI agent should escalate customer inquiries to human support agents.

---

## Category-Based Triggers

### Pricing Inquiries

**Trigger Keywords:**
- "price", "pricing", "cost", "how much"
- "enterprise plan", "enterprise pricing"
- "quote", "quotation"
- "discount", "volume discount"
- "billing plan", "subscription cost"

**Action:** Create ticket → Escalate immediately
**Reason Code:** `pricing_inquiry`
**Response:** "I'll connect you with our sales team who can provide detailed pricing information. They'll contact you within 24 hours."

---

### Legal Threats

**Trigger Keywords:**
- "lawyer", "attorney", "legal"
- "sue", "lawsuit", "litigation"
- "court", "legal action"
- "breach of contract"
- "formal notice"

**Action:** Create ticket → Escalate with HIGH urgency
**Reason Code:** `legal_threat`
**Response:** "Your concern is important. A specialist will review this matter and contact you shortly."

---

### Refund Requests

**Trigger Keywords:**
- "refund", "money back"
- "chargeback", "charge back"
- "cancel subscription", "cancel order"
- "reversal", "reimburse"

**Action:** Create ticket → Escalate to billing team
**Reason Code:** `refund_request`
**Response:** "I'll connect you with our billing team who can assist with your refund request."

---

### Competitor Inquiries

**Trigger Keywords:**
- Competitor names mentioned
- "better than", "compared to"
- "switching from", "migrating from"
- "why choose you over"

**Action:** Create ticket → Escalate to sales
**Reason Code:** `competitor_inquiry`
**Response:** "I'll have a specialist discuss how TechCorp can meet your specific needs."

---

## Sentiment-Based Triggers

### Negative Sentiment (Score < 0.3)

**Detection:**
- Sentiment analysis score below 0.3
- Multiple negative keywords in single message
- Aggressive language or tone

**Action:** Respond with empathy → Escalate
**Reason Code:** `negative_sentiment`
**Response:** "I understand your frustration. Let me connect you with someone who can help resolve this issue."

---

### Extremely Angry Customers

**Detection:**
- ALL CAPS messages
- Multiple exclamation marks (!!!)
- Profanity or abusive language
- Threats to leave or switch

**Action:** Empathetic response → Immediate escalation
**Reason Code:** `negative_sentiment`
**Response:** "I sincerely apologize for the frustration you've experienced. I'm escalating this to our support team for immediate attention."

---

## Channel-Specific Triggers

### WhatsApp

**Explicit Human Request Keywords:**
- "human", "agent", "representative"
- "real person", "speak to someone"
- "call me", "phone support"

**Action:** Immediate escalation
**Reason Code:** `human_requested`
**Response:** "I'll connect you with a human agent who can assist you further."

---

### Email

**Formal Complaint Indicators:**
- "formal complaint"
- "escalate this"
- "speak to your manager"
- "supervisor"
- Multiple recipients CC'd

**Action:** Create ticket → Escalate
**Reason Code:** `formal_complaint`
**Response:** "Your concern has been escalated to our support management team."

---

### Web Form

**Urgent Keywords:**
- "urgent", "ASAP", "immediately"
- "emergency", "critical"
- "production down", "outage"

**Action:** Create ticket → Escalate with urgency flag
**Reason Code:** `urgent_issue`
**Response:** "We understand this is urgent. Our team will prioritize your request."

---

## Knowledge Base Failure Triggers

### No Results After Multiple Searches

**Detection:**
- 2+ consecutive knowledge base searches return no results
- Agent cannot find relevant information

**Action:** Escalate to specialist
**Reason Code:** `no_information`
**Response:** "Let me connect you with a specialist who has more detailed information about this topic."

---

### Complex Technical Issues

**Detection:**
- Issues requiring code debugging
- Integration problems beyond documentation
- Custom implementation questions

**Action:** Escalate to engineering support
**Reason Code:** `complex_technical`
**Response:** "This requires specialized technical assistance. I'm escalating to our engineering team."

---

## Fallback Rule

**When in Doubt, Escalate**

If the AI agent is uncertain about how to handle a situation:
- Confidence score below threshold
- Unusual request not covered by guidelines
- Potential compliance or security concern

**Action:** Escalate
**Reason Code:** `uncertain`
**Response:** "Let me connect you with someone who can better assist with this matter."

---

## Escalation Priority Levels

### HIGH Priority

- Legal threats
- Security breaches
- Production outages for Enterprise customers
- Threats to leave/churn

**Response Time:** < 1 hour

### MEDIUM Priority

- Pricing inquiries
- Refund requests
- Negative sentiment escalations
- Complex technical issues

**Response Time:** < 4 hours

### LOW Priority

- General questions beyond AI knowledge
- Feature requests
- Competitor comparisons

**Response Time:** < 24 hours

---

## Escalation Response Template

**For All Escalations:**

1. **Acknowledge the issue**
   - "I understand your concern..."
   - "I can see this is important..."

2. **Explain the escalation**
   - "I'm connecting you with..."
   - "A specialist will..."

3. **Set expectations**
   - "They will contact you within..."
   - "You can expect a response..."

4. **Provide reference**
   - "Your ticket number is..."
   - "Reference ID: ..."

---

## Post-Escalation Actions

**AI Agent Must:**

1. Create complete ticket with full conversation history
2. Tag ticket with appropriate escalation reason code
3. Set priority level based on urgency
4. Log escalation in discovery log
5. Do NOT continue conversation after escalation (unless customer asks new unrelated question)

---

## Review and Updates

This escalation rules document should be reviewed and updated:
- Weekly during Phase 1 incubation
- Based on discovered edge cases
- After each false positive/negative escalation
- Before Phase 2 transition

**Last Updated:** 2026-03-17
**Version:** 1.0
