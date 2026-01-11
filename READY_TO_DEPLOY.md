# 🚀 LUCY - READY TO DEPLOY!

## ✅ Co je PŘIPRAVENO:

### 1. **Orchestrator** (lucy_orchestrator.py)
- Routes queries to 9 assistants
- Evaluator quality check
- Multi-agent collaboration
- **System Prompt:** Czech/English, professional, learns from errors

### 2. **9 Assistants** (assistant_server.py + evaluator.py)
- Communications (emails, messages)
- Knowledge (tech docs)
- Projects (Linear, GitHub)
- Content (N8N automation)
- Data (Qdrant, Supabase)
- Dev (VSCode, Docker)
- Business (finance, deals)
- Personal (Todoist, calendar)
- **Evaluator** (quality control - NEW!)

### 3. **Voice Interface** (voice_server.py)
- Google Cloud Speech-to-Text (Czech)
- Google Cloud Text-to-Speech (Czech female voice)
- WebSocket streaming
- Audio file upload

### 4. **Launcher** (launcher.py)
- Dynamic entry point based on LUCY_MODE
- Single Docker image, multiple services
- Environment-based configuration

### 5. **Deployment Scripts**
- `deploy-full-gcp.sh` - Full GCP Cloud Run deployment
- `deploy-local.sh` - Local testing (NEW!)
- `deploy-thin.sh` - Thin client (if needed)

### 6. **Documentation**
- DEPLOYMENT_GUIDE.md - Complete setup instructions
- VPN_VS_SSL_SSH.md - Why VPN (Tailscale recommended)
- ARCHITECTURE_FIXED.md - Correct architecture

### 7. **Integrations Ready**
- ✅ Qdrant (5,757 emails + 22,315 tech pages)
- ✅ Supabase (HOT buffer - tables ready)
- ⏳ Notion (API key needed)
- ⏳ Linear (API key needed)
- ⏳ Todoist (API token needed)
- ⏳ Gmail (OAuth from 1Password)
- ⏳ Beeper (MCP integration TODO)

---

## 🎯 DEPLOY TEĎKA - 3 OPTIONS:

### OPTION 1: Local Test First (RECOMMENDED)
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment

# 1. Setup credentials
cp ../.env.template ../.env
# Edit .env with credentials from 1Password AI vault

# 2. Deploy locally
chmod +x deploy-local.sh
./deploy-local.sh

# 3. Test
curl http://localhost:8080/health
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me emails about Qdrant"}'

# 4. If works → deploy to GCP
```

**Advantage:** Test everything locally before GCP

---

### OPTION 2: Direct GCP Deployment (FAST)
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment

# Set credentials
export ANTHROPIC_API_KEY="sk-ant-..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="eyJ..."
export QDRANT_HOST="192.168.1.129:6333"

# DEPLOY!
./deploy-full-gcp.sh

# Wait ~15 minutes
# Get URLs from output
```

**Advantage:** Lucy live on GCP immediately

---

### OPTION 3: Step-by-Step Manual
```bash
# 1. Authenticate GCP
gcloud auth login
gcloud config set project premium-gastro

# 2. Create secrets
echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-

# 3. Build image
cd /Users/premiumgastro/Projects/Mem0
docker build -t gcr.io/premium-gastro/lucy-assistant:latest -f lucy_system/deployment/Dockerfile.production lucy_system

# 4. Push
docker push gcr.io/premium-gastro/lucy-assistant:latest

# 5. Deploy orchestrator
gcloud run deploy lucy-orchestrator \
  --image=gcr.io/premium-gastro/lucy-assistant:latest \
  --region=us-central1 \
  --set-env-vars=LUCY_MODE=orchestrator \
  --set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest
```

**Advantage:** Full control over each step

---

## 📋 MISSING PIECES (Quick Setup):

### 1. Supabase Tables (5 min)
```sql
-- In Supabase SQL editor:

CREATE TABLE query_cache (
    query_hash TEXT PRIMARY KEY,
    query TEXT,
    result JSONB,
    user_id TEXT,
    cached_at TIMESTAMP DEFAULT NOW(),
    ttl INTERVAL DEFAULT '1 hour'
);

CREATE TABLE lucy_errors (
    error_id TEXT PRIMARY KEY,
    error_type TEXT,
    what_happened TEXT,
    why_happened TEXT,
    how_to_prevent TEXT,
    context JSONB,
    severity TEXT,
    occurrence_count INT DEFAULT 1,
    occurred_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE lucy_memory (
    memory_id TEXT PRIMARY KEY,
    user_id TEXT,
    content TEXT,
    memory_type TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. VPN Setup - Tailscale (5 min)
```bash
# On NAS:
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Note Tailscale IP (e.g., 100.x.x.x)
tailscale ip

# Update .env:
QDRANT_HOST=100.x.x.x:6333
```

### 3. API Keys (10 min)
- **Notion:** notion.so/my-integrations
- **Linear:** linear.app/settings/api
- **Todoist:** todoist.com/prefs/integrations
- **Gmail:** GCP Console → APIs → Gmail API → OAuth

---

## 🎤 VOICE ASSISTANT - Jak mluvit s Lucy:

### Po deployment:
```bash
# Get voice URL
VOICE_URL=$(gcloud run services describe lucy-voice --region=us-central1 --format='value(status.url)')

# Record voice (Mac)
sox -d recording.wav rate 16000 channels 1

# Send to Lucy
curl -X POST $VOICE_URL/voice -F 'audio=@recording.wav'

# Lucy responds:
# {
#   "transcript": "Ukaž mi dnešní agendu",
#   "text_response": "Máš 5 úkolů...",
#   "audio_response_base64": "..." 
# }

# Play Lucy's response
echo "$response" | jq -r '.audio_response_base64' | xxd -r -p > lucy_response.mp3
afplay lucy_response.mp3
```

---

## 📊 DALŠÍ ČLENOVÉ TÝMU (Po Lucy):

### 1. **Pan Talíř** (Business Chief)
**Status:** Design ready (from IMPROVEMENTS.md)
**Role:** Sales, deals, customer relationships
**Timeline:** Next week after Lucy is stable

**Implementation:**
```python
class PanTalirAgent:
    """
    Sales & Business Operations
    
    Sub-agents:
    - Lead Hunter (qualification)
    - Deal Closer (proposals)
    - Customer Success (retention)
    - Partnership Scout
    """
```

**Integrations:**
- Linear (deals as projects)
- Notion (customer database)
- Gmail (customer emails)
- Qdrant (customer history)

### 2. **Tukabel** (Tech Chief)
**Status:** Partially implemented (from agent_system)
**Role:** Technical operations, infrastructure
**Timeline:** Next week (parallel with Pan Talíř)

**Implementation:**
Already exists in `/agent_system/domains/tukabel/`

**Sub-agents:**
- Planner (architecture)
- Installer (deployment)
- Fixer (debugging)
- API Expert
- MCP Expert
- Database Expert
- Security Expert

### 3. **Marketing Chief**
**Timeline:** 2-3 weeks
**Role:** Content, SEO, social media

### 4. **Finance Chief**
**Timeline:** 2-3 weeks
**Role:** Invoices, revenue, budgets

---

## ✅ DEPLOYMENT CHECKLIST:

### Before:
- [ ] 1Password AI vault access
- [ ] GCP project (premium-gastro)
- [ ] NAS accessible (192.168.1.129)
- [ ] Supabase account
- [ ] Notion workspace
- [ ] Linear workspace
- [ ] Todoist account

### Setup:
- [ ] Create .env from template
- [ ] Fill API keys from 1Password
- [ ] Setup VPN (Tailscale)
- [ ] Create Supabase tables
- [ ] Test Qdrant connection

### Deploy:
- [ ] Run deploy-local.sh (test)
- [ ] Test query locally
- [ ] Run deploy-full-gcp.sh
- [ ] Verify all services healthy
- [ ] Test voice interface
- [ ] Open aquarium UI

### Post-Deploy:
- [ ] Setup Notion integration
- [ ] Setup Linear integration
- [ ] Setup Todoist integration
- [ ] First query: "Show me today's agenda"
- [ ] Morning briefing
- [ ] Voice test (Czech)
- [ ] Update Mem0 with preferences

---

## 🚀 RECOMMENDED: START NOW!

```bash
# 1. Local test (5 min)
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment
chmod +x deploy-local.sh
./deploy-local.sh

# 2. If works → GCP deploy (15 min)
./deploy-full-gcp.sh

# 3. Start using Lucy!
curl -X POST $LUCY_URL/query -d '{"query":"Show me today"}'
```

**Total time to Lucy live:** ~20 minutes

---

**Status:** ✅ READY
**Next Action:** Choose deployment option & GO!
**Support:** Já budu stavět další členy (Pan Talíř, Tukabel) mezitím
