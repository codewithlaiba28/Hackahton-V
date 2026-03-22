# WhatsApp Configuration - IMPORTANT

## ✅ Configuration Status: COMPLETE

Your Customer Success FTE is now configured to use **WhatsApp ONLY** - NO SMS messages will be sent or received.

---

## 🔧 Twilio WhatsApp Setup

### Current Configuration

```env
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### ⚠️ IMPORTANT: WhatsApp Sandbox Limit

Your Twilio account is using the **WhatsApp Sandbox** which has these limitations:

| Limit | Value |
|-------|-------|
| **Daily Message Limit** | 5 messages/day |
| **Recipients** | Only numbers joined to sandbox |
| **Session Window** | 24 hours after customer message |

### 📋 How to Use WhatsApp Sandbox

1. **Join the Sandbox** (one-time setup):
   - Send WhatsApp message: `join <your-sandbox-keyword>`
   - To number: `+14155238886`
   - Get your keyword from: https://console.twilio.com/whatsapp/sandbox

2. **Add Test Numbers**:
   - Each number that wants to test must join the sandbox
   - Message `join <keyword>` from each test number

3. **24-Hour Session**:
   - After a customer messages you, you have 24 hours to reply
   - After 24 hours, customer must message first again

---

## 🚫 SMS is DISABLED

Your system is configured to **ONLY** use WhatsApp:

```python
# ✅ WhatsApp messages - ALLOWED
to_number = "whatsapp:+923001234567"

# ❌ SMS messages - BLOCKED
# The system will reject any non-WhatsApp number
```

### Code Protection

The `WhatsAppHandler` has built-in validation:

```python
# Validates incoming messages are WhatsApp (not SMS)
if not from_number_raw.startswith("whatsapp:"):
    logger.warning("Received non-WhatsApp message. Ignoring.")
    raise ValueError("Only WhatsApp messages are supported")

# Formats outgoing numbers for WhatsApp
to_number_formatted = f"whatsapp:{to_number}"
```

---

## 🧪 Testing Your Setup

### Test 1: Verify Configuration

```bash
cd backend
python test_whatsapp_integration.py
```

Expected output:
```
✅ Handler Initialization - PASS
✅ Webhook Parsing - PASS
✅ WhatsApp message sent successfully!
```

### Test 2: Send Test Message

1. From your WhatsApp, send: `Hello` to `+14155238886`
2. Check the API logs for received message
3. Verify response is sent back

### Test 3: Check API Endpoint

```bash
# Start the API
python -m uvicorn api.main:app --reload

# Test webhook (simulate incoming WhatsApp)
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "Body": "Test message",
    "From": "whatsapp:+923001234567",
    "MessageSid": "SMtest123",
    "ProfileName": "Test User"
  }'
```

---

## 📊 Error Codes Reference

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 63038 | Daily limit exceeded | Wait 24 hours or upgrade Twilio plan |
| 21211 | Invalid phone format | Use E.164 format: `+923001234567` |
| 21670 | Not a WhatsApp user | Number must have WhatsApp installed |
| 21675 | Not opted-in | User must join sandbox first |

---

## 🔄 Production Upgrade (Remove Limits)

To remove the 5 message/day limit:

### Step 1: Upgrade Twilio Account
1. Go to: https://console.twilio.com
2. Upgrade to paid plan
3. Cost: ~$0.005 per WhatsApp message

### Step 2: Get Dedicated WhatsApp Number
1. Apply for WhatsApp Business API
2. Submit business verification
3. Get approved phone number

### Step 3: Update Configuration
```env
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890  # Your dedicated number
```

---

## 📝 Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| WhatsApp Receiving | ✅ Working | Webhook configured |
| WhatsApp Sending | ✅ Working | 5 msg/day limit |
| SMS Blocking | ✅ Active | Only WhatsApp allowed |
| Number Validation | ✅ Active | E.164 format required |
| Error Handling | ✅ Active | Proper error codes |
| Mock Mode | ✅ Active | Fallback when API unavailable |

---

## 🎯 Next Steps

1. **For Testing** (Current Setup):
   - ✅ Already configured
   - Join sandbox from test numbers
   - Stay within 5 msg/day limit

2. **For Production** (Future):
   - Upgrade Twilio account
   - Get dedicated WhatsApp number
   - Update `TWILIO_WHATSAPP_NUMBER` in `.env`

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: Look for error codes in console
2. **Verify Sandbox**: Ensure numbers joined sandbox
3. **Check Limit**: 5 messages/day maximum
4. **Format Numbers**: Use `+countrycode<number>` format

---

**Last Updated**: 2026-03-22  
**Configuration**: WhatsApp ONLY (NO SMS)
