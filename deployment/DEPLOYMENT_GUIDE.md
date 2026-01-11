# LUCY DEPLOYMENT - PREMIUM GASTRO
## Complete Setup Guide

---

## 🚀 QUICK START (Deploy NOW)

### Prerequisites:
```bash
# 1. GCP Project
export PROJECT_ID="premium-gastro"

# 2. Credentials (from 1Password AI vault)
export ANTHROPIC_API_KEY="sk-ant-..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="eyJ..."
export NOTION_API_KEY="secret_..."

# 3. NAS connection
export QDRANT_HOST="192.168.1.129:6333"
```

### Deploy:
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment

# Make executable
chmod +x deploy-full-gcp.sh

# DEPLOY!
./deploy-full-gcp.sh
```

**Duration:** ~15 minutes
**Result:** Lucy + 9 assistants + Voice + Aquarium live on GCP

---

## 📱 USAGE AFTER DEPLOYMENT

### 1. Text Query (Main Interface)
```bash
# Get orchestrator URL from deployment output
LUCY_URL="https://lucy-orchestrator-xxx.run.app"

# Query Lucy
curl -X POST $LUCY_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me emails about Qdrant from last week",
    "user_id": "petr",
    "language": "cs"
  }'
```

**Response:**
```json
{
  "response": "Našla jsem 12 emailů o Qdrant...",
  "agent": "communications",
  "confidence": 0.92,
  "sources": [...],
  "quality_score": 0.89,
  "evaluated": true
}
```

### 2. Voice Query (Czech Speech)
```bash
VOICE_URL="https://lucy-voice-xxx.run.app"

# Record your voice (3-10 seconds)
# Upload audio file
curl -X POST $VOICE_URL/voice \
  -F 'audio=@my_query.wav'
```

**Response:**
```json
{
  "transcript": "Ukaž mi emaily o Qdrant",
  "text_response": "Našla jsem 12 emailů...",
  "audio_response_base64": "..." // Lucy's voice response!
}
```

### 3. Morning Briefing
```bash
curl -X POST $LUCY_URL/briefing?user_id=petr
```

**Gets:**
- Todoist agenda (today's tasks)
- Linear tasks due today
- Unread important emails
- Calendar conflicts
- Urgent messages

### 4. Aquarium (Monitoring)
```bash
# Open in browser
AQUARIUM_URL="https://lucy-aquarium-xxx.run.app"
open $AQUARIUM_URL
```

**See:**
- Which agents are working
- What they're thinking
- Edit thoughts in real-time
- Decision history

---

## 🔧 INTEGRATION SETUP

### 1. Linear (Project Management)
```bash
# Get API key: linear.app/settings/api
export LINEAR_API_KEY="lin_api_..."

# Test
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -d '{"query": "{ viewer { name } }"}'
```

**Lucy will:**
- Track all tasks in Linear
- Update progress automatically
- Create subtasks for complex work
- Report deadlines

### 2. Notion (Database + Notes)
```bash
# Get API key: notion.so/my-integrations
export NOTION_API_KEY="secret_..."

# Share databases with integration
# - Gmail database (built-in)
- Personal notes
- Project documentation
```

**Lucy will:**
- Query Notion databases
- Use Notion AI for complex queries
- Track notes and documentation
- Access Gmail via Notion integration

### 3. Todoist (Daily Agenda)
```bash
# Get API token: todoist.com/prefs/integrations
export TODOIST_API_TOKEN="..."

# Test
curl https://api.todoist.com/rest/v2/tasks \
  -H "Authorization: Bearer $TODOIST_API_TOKEN"
```

**Lucy will:**
- Manage daily personal tasks
- Schedule reminders
- Track habits
- Optimize agenda

### 4. Gmail (Direct Access - Optional)
```bash
# Enable Gmail API in GCP Console
# Create OAuth 2.0 credentials
# Store in 1Password AI vault

# Lucy prefers Notion Gmail integration
# But can use direct API for advanced features
```

### 5. Beeper (All Messaging)
```bash
# Beeper MCP integration
# TODO: Setup Beeper MCP server
# Will enable WhatsApp, Telegram, Signal, etc.
```

---

## 📊 INTEGRACE S EXISTUJÍCÍMI DATY

### Qdrant (NAS - 192.168.1.129:6333)
**Status:** ✅ READY
- Email history: 5,757 emails (6 months)
- Tech docs: 22,315 pages
- Beeper messages: TODO (pending scraper)

**Usage:**
```python
# Lucy automatically queries Qdrant for context
# Via VPN connection (Tailscale recommended)
```

### Supabase (HOT Buffer)
**Status:** ⏳ NEEDS TABLES

**Create:**
```sql
-- Query cache
CREATE TABLE query_cache (
    query_hash TEXT PRIMARY KEY,
    query TEXT,
    result JSONB,
    user_id TEXT,
    cached_at TIMESTAMP DEFAULT NOW(),
    ttl INTERVAL DEFAULT '1 hour'
);

-- Error learning
CREATE TABLE lucy_errors (
    error_id TEXT PRIMARY KEY,
    error_type TEXT,
    what_happened TEXT,
    why_happened TEXT,
    how_to_prevent TEXT,
    context JSONB,
    severity TEXT,
    occurrence_count INT DEFAULT 1,
    occurred_at TIMESTAMP DEFAULT NOW(),
    last_occurred TIMESTAMP DEFAULT NOW()
);

-- Memory (Mem0 integration)
CREATE TABLE lucy_memory (
    memory_id TEXT PRIMARY KEY,
    user_id TEXT,
    content TEXT,
    memory_type TEXT, -- short_term | working | long_term | episodic
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    access_count INT DEFAULT 0
);
```

### Mem0 (Long-term Learning)
**Status:** ⏳ NEEDS SETUP

```bash
# Install Mem0
pip install mem0ai

# Configure
export MEM0_API_KEY="..."  # If using cloud
# Or use local Mem0 instance
```

---

## 🎯 DALŠÍ ČLENOVÉ TÝMU (Po Lucy)

### 1. Pan Talíř (Business Operations)
**Priority:** HIGH
**Timeline:** Next week

**Role:**
- Sales pipeline management
- Customer relationships
- Deal tracking
- Revenue forecasting

**Integration:**
- Linear (deals as projects)
- Notion (customer database)
- Gmail (customer emails)

### 2. Tukabel (Technical Operations) 
**Priority:** HIGH
**Timeline:** Next week

**Role:**
- Infrastructure management
- Code deployment
- Bug fixing
- API integrations
- Database management

**Integration:**
- GitHub (code repos)
- Docker (containers)
- VSCode (development)
- Qdrant/Supabase (databases)

### 3. Marketing Chief
**Priority:** MEDIUM
**Timeline:** 2-3 weeks

**Role:**
- Content creation
- SEO optimization
- Social media management
- Campaign tracking

### 4. Finance Chief
**Priority:** MEDIUM
**Timeline:** 2-3 weeks

**Role:**
- Invoice management
- Revenue tracking
- Budget monitoring
- Tax compliance

---

## 🔐 VPN SETUP (GCP ↔ NAS)

**Recommended:** Tailscale (easiest)

### On NAS:
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start
tailscale up

# Note IP (e.g., 100.x.x.x)
tailscale ip
```

### In GCP Dockerfile:
```dockerfile
# Add to Dockerfile.production
RUN curl -fsSL https://tailscale.com/install.sh | sh

# Add to entrypoint
CMD ["sh", "-c", "tailscale up && python launcher.py"]
```

### Update Config:
```bash
# Use Tailscale IP instead of 192.168.1.129
export QDRANT_HOST="100.x.x.x:6333"
```

**Done!** GCP can now securely access NAS.

---

## 📈 MONITORING & LEARNING

### Error Learning System
**Location:** `lucy_system/core/error_learning.py`

**Usage:**
```python
from core.error_learning import ErrorLearningSystem

error_system = ErrorLearningSystem()

# Before action
warning = error_system.check_before_action("deployment", context)
if warning:
    # Similar error found in history!
    ask_user_confirmation()

# After error
error_system.record_error(
    error_type="misunderstood_request",
    what_happened="Created wrong architecture",
    why_happened="Didn't read full request",
    how_to_prevent="Read ENTIRE request before acting"
)
```

### Weekly Review
```bash
# Check repeated errors
curl $LUCY_URL/stats

# Review error patterns
# Adjust behavior
# Update prevention strategies
```

---

## 🎤 VOICE FEATURES

**Czech Language:** Primary
**English:** Fallback

**Voice:** Wavenet-A (Czech female)

**Usage:**
1. Record audio (WAV, MP3)
2. POST to `/voice`
3. Lucy transcribes → processes → responds in voice

**Real-time Stream:**
- WebSocket: `wss://lucy-voice-xxx.run.app/voice-stream`
- Stream audio chunks
- Lucy responds live

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] GCP project setup (premium-gastro)
- [ ] Secrets configured (Anthropic, Supabase, Notion)
- [ ] VPN setup (Tailscale recommended)
- [ ] Supabase tables created
- [ ] Run `deploy-full-gcp.sh`
- [ ] Test orchestrator health
- [ ] Test voice interface
- [ ] Open aquarium UI
- [ ] Configure Linear integration
- [ ] Configure Notion integration
- [ ] Configure Todoist integration
- [ ] Setup Mem0
- [ ] First query: "Show me today's agenda"
- [ ] Morning briefing test
- [ ] Voice query test

**Time:** ~2 hours complete setup
**Result:** Lucy fully operational!

---

## 🚨 TROUBLESHOOTING

### Lucy not responding:
```bash
# Check health
curl $LUCY_URL/health

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lucy-orchestrator" --limit 50
```

### VPN issues:
```bash
# Test NAS connection from GCP
curl http://TAILSCALE_IP:6333/collections

# Check Tailscale status
tailscale status
```

### Assistant timeout:
```bash
# Increase timeout in orchestrator
# Default: 60s
# For complex queries: 120s
```

---

**Status:** READY TO DEPLOY
**Last Updated:** 2026-01-11
**Version:** 1.0 Production
