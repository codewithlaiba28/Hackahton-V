# Customer Success FTE - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites

- Python 3.10+ installed
- Node.js 18+ installed
- Docker Desktop installed (for PostgreSQL)
- Cerebras API Key (FREE): https://cloud.cerebras.ai/
- Twilio Account (FREE sandbox): https://www.twilio.com/try-twilio

### Step 1: Install Dependencies

#### Backend (Python)
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend
npm install
```

### Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env` in the root directory
2. Fill in your API keys:
   - `CEREBRAS_API_KEY` (required for LLM)
   - `TWILIO_ACCOUNT_SID` (optional, for WhatsApp)
   - `TWILIO_AUTH_TOKEN` (optional, for WhatsApp)

**Minimum Configuration (for testing without WhatsApp):**
```env
CEREBRAS_API_KEY=csk_your_key_here
DATABASE_URL=postgresql://fte_user:fte_password@localhost:5432/fte_db
KAFKA_ENABLED=false
```

### Step 3: Start PostgreSQL (Docker)

```bash
# From project root
docker-compose up -d postgres
```

Wait 30 seconds for PostgreSQL to initialize.

### Step 4: Setup Database

```bash
cd backend
python setup_database.py
python seed_knowledge_base.py
```

### Step 5: Start Backend Server

```bash
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "channels": {
    "email": "active",
    "whatsapp": "active",
    "web_form": "active"
  }
}
```

### Step 6: Start Frontend

Open a new terminal:
```bash
cd frontend
npm run dev
```

Open browser to: http://localhost:3000

---

## 🧪 Testing the System

### Test 1: Web Form Submission

1. Go to http://localhost:3000/dashboard/support
2. Fill out the form:
   - Name: Test User
   - Email: test@example.com
   - Subject: How do I reset my password?
   - Category: Technical Support
   - Message: I forgot my password and need help resetting it.
3. Click "Submit Support Ticket"
4. You should receive a ticket ID and AI response

### Test 2: Agent Chat

1. Go to http://localhost:3000/dashboard/agent
2. Type a message: "How do I use your product?"
3. The AI should respond with helpful information from the knowledge base

### Test 3: Dashboard

1. Go to http://localhost:3000/dashboard
2. You should see:
   - Total Conversations
   - Average Sentiment
   - Channel Breakdown
   - Recent Tickets

### Test 4: Authentication

1. Go to http://localhost:3000/signup
2. Create an account with email/password
3. Login at http://localhost:3000/login
4. You should be redirected to the dashboard

---

## 🐛 Troubleshooting

### Backend won't start

**Error: Missing CEREBRAS_API_KEY**
```
Solution: Set CEREBRAS_API_KEY in your .env file
```

**Error: Database connection failed**
```
Solution: 
1. Ensure PostgreSQL is running: docker-compose ps
2. Check DATABASE_URL in .env
3. Run: python setup_database.py
```

### Frontend won't start

**Error: Module not found**
```
Solution: Run npm install in the frontend directory
```

**Error: API connection failed**
```
Solution: 
1. Ensure backend is running on port 8000
2. Check NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend/.env
```

### WhatsApp not working

**Error: Twilio credentials invalid**
```
Solution:
1. Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
2. Ensure TWILIO_WHATSAPP_NUMBER starts with 'whatsapp:'
3. Check Twilio sandbox is active
```

**Error: Daily message limit exceeded**
```
Solution: Twilio sandbox has 5 messages/day limit. Wait 24 hours or upgrade.
```

### Gmail not working

**Error: OAuth credentials missing**
```
Solution:
1. Set up Gmail OAuth in Google Cloud Console
2. Download credentials.json to backend/
3. Run: python gmail_auth_setup.py
```

---

## 📋 Hackahton Requirements Checklist

### Phase 1: Incubation ✅
- [x] Working prototype that handles customer queries
- [x] MCP server with 5+ tools
- [x] Discovery log documenting requirements
- [x] Agent skills defined
- [x] Escalation rules crystallized
- [x] Channel-specific response templates

### Phase 2: Specialization ✅
- [x] PostgreSQL database with 8 tables
- [x] OpenAI Agents SDK integration (via Cerebras)
- [x] Gmail integration (with polling)
- [x] WhatsApp integration (via Twilio)
- [x] Web Support Form (React component)
- [x] Cross-channel customer identification
- [x] Sentiment analysis
- [x] Knowledge base with vector search (pgvector)
- [x] FastAPI backend with all endpoints
- [x] Next.js frontend with dashboard

### Multi-Channel Support ✅
- [x] **Gmail**: Email intake and response
- [x] **WhatsApp**: WhatsApp messaging via Twilio
- [x] **Web Form**: Standalone support form UI

### Authentication ✅
- [x] Better Auth integration
- [x] Login/Signup pages
- [x] Session management
- [x] Protected dashboard routes

### Frontend Pages ✅
- [x] Landing page (http://localhost:3000)
- [x] Login page (http://localhost:3000/login)
- [x] Signup page (http://localhost:3000/signup)
- [x] Dashboard (http://localhost:3000/dashboard)
- [x] Support Form (http://localhost:3000/dashboard/support)
- [x] Agent Chat (http://localhost:3000/dashboard/agent)
- [x] Tickets List (http://localhost:3000/dashboard/tickets)
- [x] Analytics (http://localhost:3000/dashboard/analytics)
- [x] Customers (http://localhost:3000/dashboard/customers)

---

## 🎯 Submission Checklist

Before submitting, verify:

- [ ] All environment variables are configured
- [ ] PostgreSQL is running and database is initialized
- [ ] Knowledge base is seeded with product documentation
- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Web form submission works
- [ ] Agent chat responds correctly
- [ ] Dashboard displays metrics
- [ ] Authentication (login/signup) works
- [ ] All tests pass: `cd backend && pytest`

---

## 📚 Documentation Files

- `Hackahton.md` - Main hackathon requirements
- `specs/customer-success-fte-spec.md` - Feature specification
- `specs/transition-checklist.md` - Phase 1→2 transition
- `ISSUES_FIXED.md` - Known issues and fixes
- `backend/WHATSAPP_SETUP.md` - WhatsApp setup guide

---

## 🆘 Getting Help

If you encounter issues:

1. Check `ISSUES_FIXED.md` for known problems
2. Review backend logs for error messages
3. Verify all environment variables are set correctly
4. Ensure PostgreSQL is running: `docker-compose ps`
5. Test backend directly: `curl http://localhost:8000/health`

---

## 🎓 What You'll Learn

By completing this hackathon, you'll have hands-on experience with:

- **OpenAI Agents SDK** - Production AI agent framework
- **FastAPI** - Modern Python web framework
- **PostgreSQL + pgvector** - Vector database for AI
- **Apache Kafka** - Event streaming architecture
- **Kubernetes** - Container orchestration
- **Next.js** - React full-stack framework
- **Better Auth** - Authentication system
- **Multi-channel integrations** - Gmail, WhatsApp APIs
- **Production patterns** - Error handling, monitoring, scaling

---

**Good luck with your submission! 🚀**
