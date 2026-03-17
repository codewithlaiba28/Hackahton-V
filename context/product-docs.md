# TechCorp Product Documentation

## Table of Contents

1. [API Key Management](#api-key-management)
2. [OAuth 2.0 Authentication](#oauth-20-authentication)
3. [Webhook Configuration](#webhook-configuration)
4. [Rate Limits & Quotas](#rate-limits--quotas)
5. [Data Export](#data-export)
6. [Billing Overview](#billing-overview)
7. [Onboarding Checklist](#onboarding-checklist)
8. [Troubleshooting & Common Errors](#troubleshooting--common-errors)

---

## API Key Management

### Overview

API keys are the simplest way to authenticate with the TechCorp API. Each key is tied to your account and inherits your plan's rate limits and permissions.

### Creating an API Key

1. Log in to your TechCorp dashboard
2. Navigate to **Settings > API > Keys**
3. Click **"Create New Key"**
4. Give your key a descriptive name (e.g., "Production Server", "Local Development")
5. Copy the key immediately — **you cannot view it again**
6. Store the key securely (see Best Practices below)

### Rotating API Keys

For security, rotate your API keys regularly:

1. Go to **Settings > API > Keys**
2. Find the key you want to rotate
3. Click **"Rotate Key"**
4. Copy the new key immediately
5. Update your application with the new key
6. The old key remains valid for 24 hours to allow for a smooth transition
7. After 24 hours, the old key is automatically revoked

### Deleting Compromised Keys

If you suspect a key has been compromised:

1. Go to **Settings > API > Keys** immediately
2. Click **"Revoke"** on the compromised key
3. The key is invalidated instantly
4. Create a new key to replace it
5. Review your API usage logs for suspicious activity

### Best Practices

- **Use environment variables**: Never hardcode API keys in your source code
- **Use separate keys per environment**: Production, staging, and development should each have their own keys
- **Rotate keys quarterly**: Set a calendar reminder to rotate keys every 3 months
- **Monitor usage**: Set up alerts for unusual API activity
- **Limit key exposure**: Only share keys with team members who need access

### Example Usage

```bash
# Using curl
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.techcorp.com/v1/users

# Using Python
import os
import requests

api_key = os.getenv("TECHCORP_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get("https://api.techcorp.com/v1/users", headers=headers)
```

---

## OAuth 2.0 Authentication

### Overview

OAuth 2.0 is recommended for applications that need to access TechCorp on behalf of users. This flow allows users to grant your application limited access to their TechCorp account without sharing credentials.

### Registration

Before implementing OAuth, register your application:

1. Go to **Developer Dashboard > Applications**
2. Click **"Register New Application"**
3. Fill in the required fields:
   - Application name
   - Description
   - Website URL
   - Redirect URI (callback URL)
4. Note your **Client ID** and **Client Secret**

### Authorization Code Flow

The authorization code flow is the most secure OAuth 2.0 flow:

**Step 1: Redirect to Authorization**

```
GET https://auth.techcorp.com/oauth/authorize?
    client_id=YOUR_CLIENT_ID&
    redirect_uri=YOUR_REDIRECT_URI&
    response_type=code&
    scope=read+write&
    state=RANDOM_STATE_TOKEN
```

**Step 2: User Grants Permission**

The user logs in and approves your application's access request.

**Step 3: Receive Authorization Code**

TechCorp redirects to your `redirect_uri` with an authorization code:

```
GET YOUR_REDIRECT_URI?code=AUTH_CODE&state=RANDOM_STATE_TOKEN
```

**Step 4: Exchange Code for Access Token**

```bash
curl -X POST https://auth.techcorp.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI"
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
  "scope": "read write"
}
```

**Step 5: Use Access Token**

```bash
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIs..." \
     https://api.techcorp.com/v1/users/me
```

### Refresh Tokens

Access tokens expire after 1 hour. Use refresh tokens to obtain new access tokens:

```bash
curl -X POST https://auth.techcorp.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### Token Storage

- **Access tokens**: Store in memory or short-lived cache (1 hour max)
- **Refresh tokens**: Store securely in encrypted database or secure cookie
- **Never** store tokens in localStorage or sessionStorage (XSS vulnerability)

### Scopes

Available scopes for OAuth 2.0:

| Scope | Description |
|-------|-------------|
| `read` | Read-only access to resources |
| `write` | Create and update resources |
| `delete` | Delete resources |
| `admin` | Full administrative access |

---

## Webhook Configuration

### Overview

Webhooks allow TechCorp to push real-time events to your application. Instead of polling our API, you receive instant notifications when events occur.

### Setting Up Webhooks

1. Go to **Settings > Webhooks**
2. Click **"Add Endpoint"**
3. Enter your webhook URL (must use HTTPS)
4. Select events to subscribe to
5. Click **"Save"**
6. Verify the endpoint using the verification token

### Supported Events

| Event | Description | Payload Example |
|-------|-------------|-----------------|
| `user.created` | New user registered | `{"type": "user.created", "data": {"id": "usr_123", ...}}` |
| `user.updated` | User profile updated | `{"type": "user.updated", "data": {...}}` |
| `user.deleted` | User account deleted | `{"type": "user.deleted", "data": {...}}` |
| `payment.completed` | Payment successful | `{"type": "payment.completed", "data": {...}}` |
| `payment.failed` | Payment failed | `{"type": "payment.failed", "data": {...}}` |
| `subscription.created` | New subscription | `{"type": "subscription.created", "data": {...}}` |
| `subscription.cancelled` | Subscription cancelled | `{"type": "subscription.cancelled", "data": {...}}` |
| `api.rate_limit.exceeded` | Rate limit exceeded | `{"type": "api.rate_limit.exceeded", "data": {...}}` |

### Retry Logic

TechCorp automatically retries failed webhook deliveries:

- **Attempt 1**: Immediate
- **Attempt 2**: 1 minute later
- **Attempt 3**: 5 minutes later
- **Attempt 4**: 30 minutes later
- **Attempt 5**: 2 hours later

After 5 failed attempts, the webhook is marked as inactive and you'll receive an email notification.

### Verifying Webhooks

Always verify webhook signatures to ensure requests are from TechCorp:

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature."""
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# Usage in your webhook handler
@app.post("/webhook")
async def webhook_handler(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-TechCorp-Signature")
    
    if not verify_webhook(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook...
```

### Testing Webhooks

Use our webhook testing tool in the dashboard:

1. Go to **Settings > Webhooks > Test**
2. Select an event type
3. Enter your webhook URL
4. Click **"Send Test Event"**
5. Verify your endpoint receives and processes the event correctly

---

## Rate Limits & Quotas

### Overview

TechCorp enforces rate limits to ensure fair usage and platform stability. Limits are applied per API key or OAuth token.

### Rate Limit Tiers

| Plan | Requests/Hour | Requests/Day | Burst Limit |
|------|---------------|--------------|-------------|
| Free | 100 | 1,000 | 10/sec |
| Pro | 1,000 | 20,000 | 50/sec |
| Enterprise | Custom | Custom | Custom |

### Rate Limit Headers

Every API response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1647360000
Retry-After: 3600  (only when rate limited)
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded your rate limit. Please retry after 3600 seconds.",
  "retry_after": 3600
}
```

**Best practices:**

1. **Implement exponential backoff**: Wait progressively longer between retries
2. **Cache responses**: Reduce API calls by caching frequently accessed data
3. **Use webhooks**: Subscribe to events instead of polling
4. **Batch requests**: Combine multiple operations into single requests when possible

### Example: Exponential Backoff

```python
import time
import requests
from requests.exceptions import HTTPError

def make_request_with_backoff(url, max_retries=5):
    """Make API request with exponential backoff."""
    base_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', base_delay * (2 ** attempt)))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
```

### Quota Management

Monitor your usage in the dashboard:

- **Current usage**: Real-time API call count
- **Quota remaining**: Calls remaining in current period
- **Reset time**: When your quota resets
- **Usage trends**: Graph of API usage over time

---

## Data Export

### Overview

Export all your data from TechCorp in CSV or JSON format. This is useful for backups, analytics, or migrating to another platform.

### Initiating an Export

1. Go to **Settings > Data Export**
2. Select export format: **CSV** or **JSON**
3. Choose data types to export:
   - Users
   - API usage logs
   - Webhook logs
   - Billing history
   - All data (recommended)
4. Click **"Start Export"**

### Processing Time

- **Small accounts (<10,000 records)**: 5-10 minutes
- **Medium accounts (10,000-100,000 records)**: 10-30 minutes
- **Large accounts (>100,000 records)**: 30-60 minutes

You'll receive an email when your export is ready.

### Downloading Your Export

1. Check your email for the "Export Ready" notification
2. Click the download link in the email
3. Or go to **Settings > Data Export > Recent Exports**
4. Download expires after 24 hours for security

### Export Format

**JSON Example:**

```json
{
  "exported_at": "2024-03-17T10:30:00Z",
  "account_id": "acc_123456",
  "data": {
    "users": [
      {"id": "usr_001", "email": "user@example.com", "created_at": "2024-01-01T00:00:00Z"},
      {"id": "usr_002", "email": "user2@example.com", "created_at": "2024-01-02T00:00:00Z"}
    ],
    "api_logs": [...],
    "webhook_logs": [...]
  }
}
```

**CSV Format:**

- One CSV file per data type
- Files are zipped together for download
- UTF-8 encoding with headers

### Scheduled Exports (Enterprise Only)

Enterprise customers can schedule automatic exports:

- **Frequency**: Daily, weekly, or monthly
- **Destination**: S3 bucket, SFTP server, or email
- **Retention**: Keep last N exports automatically

---

## Billing Overview

### Subscription Management

Manage your subscription in the **Billing Dashboard**:

- **View current plan**: See your plan tier and features
- **Upgrade/downgrade**: Change plans at any time
- **Payment methods**: Add or remove credit cards
- **Billing history**: View and download invoices
- **Usage metrics**: Track API usage against quota

### Payment Methods

We accept:

- Credit cards (Visa, MasterCard, American Express)
- Debit cards
- PayPal (Pro and Enterprise only)
- Bank transfer (Enterprise only)
- Purchase orders (Enterprise only)

### Billing Cycle

- **Billing date**: Same day each month as your signup date
- **Proration**: Upgrades are prorated; downgrades take effect next cycle
- **Invoices**: Sent via email on billing date
- **Payment terms**: Net 30 for Enterprise customers

### Plan Changes

**Upgrading:**

1. Go to **Billing > Plan**
2. Select new plan
3. Changes take effect immediately
4. You're charged prorated amount for remainder of cycle

**Downgrading:**

1. Go to **Billing > Plan**
2. Select new plan
3. Changes take effect at start of next billing cycle
4. No refund for unused portion of current cycle

**Cancelling:**

1. Go to **Billing > Plan > Cancel Subscription**
2. Access continues until end of billing cycle
3. Data is retained for 90 days after cancellation
4. Export your data before cancellation

### Refund Policy

- **Free tier**: No refunds (no charges)
- **Pro tier**: Refunds within 14 days of charge if unused
- **Enterprise tier**: Custom refund terms in contract

**Note**: For specific pricing information, please contact our sales team at sales@techcorp.com.

---

## Onboarding Checklist

### Getting Started with TechCorp

Use this checklist to get your application up and running:

#### 1. Account Setup (15 minutes)

- [ ] Create TechCorp account
- [ ] Verify email address
- [ ] Complete profile information
- [ ] Set up two-factor authentication (recommended)

#### 2. API Configuration (30 minutes)

- [ ] Create API key for development
- [ ] Create API key for production
- [ ] Store keys in environment variables
- [ ] Test API connection with a simple request

#### 3. Application Integration (1-2 hours)

- [ ] Install SDK or set up HTTP client
- [ ] Implement authentication (API key or OAuth)
- [ ] Make your first API call
- [ ] Handle errors and rate limits
- [ ] Set up logging for API requests

#### 4. Webhook Setup (30 minutes)

- [ ] Create webhook endpoint in your application
- [ ] Implement signature verification
- [ ] Register webhook URL in dashboard
- [ ] Test with sample events
- [ ] Set up monitoring for webhook failures

#### 5. Testing (1 hour)

- [ ] Test in sandbox environment
- [ ] Verify all API endpoints you'll use
- [ ] Test error scenarios (4xx, 5xx responses)
- [ ] Test rate limit handling
- [ ] Load test with expected traffic volume

#### 6. Production Deployment (30 minutes)

- [ ] Rotate API keys (generate production-specific keys)
- [ ] Update environment variables with production keys
- [ ] Enable production webhooks
- [ ] Set up monitoring and alerts
- [ ] Document API integration for your team

#### 7. Go Live! (5 minutes)

- [ ] Deploy to production
- [ ] Verify API connectivity
- [ ] Monitor initial traffic
- [ ] Celebrate! 🎉

### Next Steps

After completing onboarding:

- Review [API Best Practices](#best-practices)
- Join our [Developer Community](https://community.techcorp.com)
- Subscribe to [API Changelog](https://techcorp.com/changelog)
- Follow us on [Twitter](https://twitter.com/techcorp) for updates

---

## Troubleshooting & Common Errors

### Authentication Errors

#### 401 Unauthorized

**Cause**: Invalid or missing API key

**Solution:**

1. Check that you're including the `Authorization` header
2. Verify your API key is correct (no extra spaces)
3. Ensure the key hasn't been revoked or expired
4. Check you're using the correct environment (production vs sandbox)

**Example:**

```python
# Correct
headers = {"Authorization": f"Bearer {api_key}"}

# Wrong - missing "Bearer " prefix
headers = {"Authorization": api_key}
```

#### 403 Forbidden

**Cause**: Valid authentication but insufficient permissions

**Solution:**

1. Check your plan includes access to this endpoint
2. Verify OAuth scopes include required permissions
3. Contact your account admin to request access

### Rate Limit Errors

#### 429 Too Many Requests

**Cause**: Exceeded rate limit

**Solution:**

1. Check `X-RateLimit-Remaining` header
2. Wait until `X-RateLimit-Reset` time
3. Implement exponential backoff
4. Consider upgrading your plan for higher limits

**Example:**

```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request
```

### Validation Errors

#### 400 Bad Request

**Cause**: Invalid request parameters

**Solution:**

1. Read the error message in the response body
2. Check required fields are present
3. Verify field formats (email, date, etc.)
4. Check field length limits

**Example Response:**

```json
{
  "error": "validation_error",
  "message": "Invalid email format",
  "field": "email",
  "value": "not-an-email"
}
```

#### 404 Not Found

**Cause**: Resource doesn't exist or wrong endpoint

**Solution:**

1. Verify the resource ID is correct
2. Check you're using the correct API version
3. Ensure you have permission to access this resource

### Server Errors

#### 500 Internal Server Error

**Cause**: Bug on TechCorp side

**Solution:**

1. Retry the request (transient errors often resolve)
2. Check our [Status Page](https://status.techcorp.com) for outages
3. If persistent, contact support with request ID from response headers

#### 503 Service Unavailable

**Cause**: TechCorp API is temporarily down for maintenance

**Solution:**

1. Check [Status Page](https://status.techcorp.com)
2. Retry after the maintenance window
3. Implement retry logic with exponential backoff

### Webhook Issues

#### Webhooks Not Received

**Cause**: Endpoint unreachable or returning errors

**Solution:**

1. Verify your endpoint is publicly accessible (not localhost)
2. Check your server logs for incoming requests
3. Ensure you're returning 2xx status code
4. Verify webhook signature is correct
5. Check webhook is active in dashboard

#### Invalid Signature

**Cause**: Webhook secret mismatch

**Solution:**

1. Verify you're using the correct webhook secret
2. Check you're hashing the raw payload (not parsed JSON)
3. Ensure you're using SHA-256 algorithm
4. Regenerate webhook secret if needed

### Getting Help

If you can't resolve your issue:

1. **Search Documentation**: Use the search bar to find relevant docs
2. **Community Forum**: Ask in [Developer Community](https://community.techcorp.com)
3. **Email Support**: support@techcorp.com (Pro and Enterprise)
4. **Live Chat**: Available in dashboard (Enterprise only)

**When contacting support, include:**

- Your account ID or email
- API endpoint and method
- Request ID from response headers
- Timestamp of the error
- Error message and status code
- Steps to reproduce
