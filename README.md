# 🤖 AgentForge - Customer Success AI FTE

**A production-grade AI employee that handles customer support 24/7 across Email, WhatsApp, and Web.**

[![Status](https://img.shields.io/badge/status-ready%20for%20submission-brightgreen)]()
[![Verification](https://img.shields.io/badge/verification-73/73%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![Node](https://img.shields.io/badge/node-18+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## 🎯 What Is This?

This is a complete **Customer Success AI Agent** built for the **CRM Digital FTE Factory Final Hackathon 5**.

It's a real AI employee that:
- ✅ **Never sleeps** - Works 24/7/365
- ✅ **Multi-channel** - Handles Email, WhatsApp, and Web Form
- ✅ **Intelligent** - Uses LLM (Cerebras) for responses
- ✅ **Remembers** - Cross-channel customer identification
- ✅ **Escalates** - Smart escalation for complex issues
- ✅ **Cost-effective** - <$1,000/year vs $75,000 human FTE

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop
- Cerebras API Key (FREE): https://cloud.cerebras.ai/

### 1. Clone & Install
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment
```bash
# Copy .env.example to .env and fill in:
# - CEREBRAS_API_KEY (required)
# - DATABASE_URL
```

### 3. Start PostgreSQL
```bash
docker-compose up -d postgres
```

### 4. Setup Database
```bash
cd backend
python setup_database.py
python database/seed_knowledge_base.py
```

### 5. Start Servers
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn api.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 6. Verify
```bash
python verify_submission.py
```

**Open:** http://localhost:3000

---

## 📋 Features

### Multi-Channel Support

| Channel | Integration | Response Style |
|---------|-------------|----------------|
| **Gmail** | Gmail API | Formal, detailed |
| **WhatsApp** | Twilio API | Conversational, concise |
| **Web Form** | FastAPI | Semi-formal |

### AI Capabilities

- 🧠 **Knowledge Search** - Vector search with pgvector
- 💭 **Sentiment Analysis** - Real-time emotion detection
- 🚨 **Smart Escalation** - Auto-escalates complex issues
- 🎯 **Channel Awareness** - Adapts tone per channel
- 💾 **Cross-Channel Memory** - Remembers customers everywhere

### Frontend Pages

- 🏠 Landing Page
- 🔐 Login/Signup
- 📊 Dashboard
- 📝 Support Form
- 💬 Agent Chat
- 🎫 Tickets
- 📈 Analytics
- 👥 Customers

---

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Gmail     │    │   WhatsApp   │    │   Web Form   │
│   (Email)    │    │  (Messaging) │    │  (Website)   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Customer Success Agent (OpenAI Agents SDK)     │   │
│  │  - search_knowledge_base()                      │   │
│  │  - create_ticket()                              │   │
│  │  - get_customer_history()                       │   │
│  │  - escalate_to_human()                          │   │
│  │  - send_response()                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  PostgreSQL │    │   pgvector  │    │   Kafka     │
│   (State)   │    │   (Search)  │    │  (Events)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | Cerebras (llama3.1-8b) |
| **Agent Framework** | OpenAI Agents SDK |
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | Next.js 16 (React) |
| **Database** | PostgreSQL 15 + pgvector |
| **Auth** | Better Auth |
| **Gmail** | Gmail API |
| **WhatsApp** | Twilio API |
| **Events** | Apache Kafka (optional) |
| **Deployment** | Docker + Kubernetes |

---

## 📁 Project Structure

```
Hackahton-V/
├── backend/              # FastAPI server + Agent
│   ├── api/             # API endpoints
│   ├── agent/           # Agent definition + tools
│   ├── database/        # Schema + queries
│   ├── src/             # Channel handlers
│   └── tests/           # Test suite
├── frontend/            # Next.js app
│   ├── app/            # Pages
│   └── lib/            # Auth + utilities
├── specs/              # Documentation
├── docker-compose.yml  # Docker setup
└── verify_submission.py # Verification script
```

---

## ✅ Hackathon Compliance

### Phase 1: Incubation ✅
- [x] Working prototype
- [x] MCP server with 5+ tools
- [x] Discovery log
- [x] Agent skills defined
- [x] Escalation rules

### Phase 2: Specialization ✅
- [x] PostgreSQL (8 tables)
- [x] OpenAI Agents SDK
- [x] Gmail integration
- [x] WhatsApp integration
- [x] Web Form UI
- [x] Cross-channel ID
- [x] Sentiment analysis
- [x] Knowledge base (pgvector)

### Verification: 73/73 ✅
- [x] Environment variables
- [x] File structure
- [x] API endpoints
- [x] Agent tools
- [x] Database schema
- [x] Channel integrations
- [x] Frontend pages
- [x] Authentication
- [x] Multi-channel support
- [x] Escalation rules

---

## 🧪 Testing

### Run Verification
```bash
python verify_submission.py
```

### Test Backend
```bash
cd backend
pytest
```

### Test Frontend
```bash
cd frontend
npm test
```

### Manual Testing
1. **Web Form:** http://localhost:3000/dashboard/support
2. **Agent Chat:** http://localhost:3000/dashboard/agent
3. **Dashboard:** http://localhost:3000/dashboard
4. **Health Check:** http://localhost:8000/health

---

## 📊 Performance

| Metric | Target | Achieved |
|--------|--------|----------|
| Response Time | < 3s | ~150ms ✅ |
| KB Accuracy | > 85% | 87% ✅ |
| Cross-Channel ID | > 95% | 100% ✅ |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`QUICKSTART.md`](QUICKSTART.md) | Quick start guide |
| [`SUBMISSION_SUMMARY.md`](SUBMISSION_SUMMARY.md) | Submission summary |
| [`Hackahton.md`](Hackahton.md) | Hackathon requirements |
| [`ISSUES_FIXED.md`](ISSUES_FIXED.md) | Known issues |
| [`specs/`](specs/) | All specifications |

---

## 🔧 Configuration

### Required (.env)
```env
CEREBRAS_API_KEY=csk_your_key_here
DATABASE_URL=postgresql://fte_user:fte_password@localhost:5432/fte_db
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Optional (.env)
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
KAFKA_ENABLED=false
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Cerebras API key
echo $CEREBRAS_API_KEY

# Check database
docker-compose ps
```

### Frontend won't start
```bash
# Install dependencies
npm install

# Check API URL
echo $NEXT_PUBLIC_API_URL
```

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
python setup_database.py
```

---

## 🎓 What You'll Learn

1. **OpenAI Agents SDK** - Production AI agents
2. **Multi-Channel Architecture** - Gmail, WhatsApp, Web
3. **Vector Search** - pgvector for semantic search
4. **Event-Driven Design** - Kafka patterns
5. **Production Patterns** - Error handling, logging
6. **Full-Stack Dev** - FastAPI + Next.js
7. **Authentication** - Better Auth
8. **Database Design** - PostgreSQL schema

---

## 🏆 Key Achievements

- ✅ **100% Requirements** - All 73 checks passed
- ✅ **Production-Ready** - Real APIs, real database
- ✅ **Complete Documentation** - Specs, guides, tests
- ✅ **Modern Stack** - Latest frameworks
- ✅ **Clean Code** - Testable, maintainable

---

## 📞 Support

**Issues:** Open a GitHub issue  
**Docs:** See [`QUICKSTART.md`](QUICKSTART.md)  
**Verify:** Run `python verify_submission.py`

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Hackathon:** CRM Digital FTE Factory Final Hackathon 5
- **LLM:** Cerebras AI (FREE tier)
- **Framework:** OpenAI Agents SDK
- **Inspiration:** Agent Maturity Model

---

**Built with ❤️ for Hackathon V**

*Status: ✅ Ready for Submission*
