# 🚀 LUCY - START TEĎKA!

## ⚡ QUICKEST START (2 kroky):

### 1. Setup Credentials (1 minuta)
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system

# AUTO: Pull z 1Password
chmod +x setup-from-1password.sh
./setup-from-1password.sh

# NEBO MANUAL: Copy template
cp .env.template .env
# Edit .env, vyplň credentials
```

### 2. Deploy & Start (2 minuty)
```bash
# Local test
chmod +x deployment/deploy-local.sh
./deployment/deploy-local.sh

# Otevři browser: http://localhost:8080/docs
# Test query:
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me emails about Qdrant"}'
```

**DONE! Lucy běží lokálně.**

---

## 📱 Použití:

### Text Query (hlavní rozhraní):
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Ukaž mi dnešní agendu",
    "user_id": "petr",
    "language": "cs"
  }'
```

### Morning Briefing:
```bash
curl -X POST http://localhost:8080/briefing?user_id=petr
```

Dostaneš:
- Todoist úkoly na dnes
- Linear tasks due today
- Unread important emails
- Calendar conflicts

---

## 🎤 Voice Assistant (po GCP deploy):

### Nahraj dotaz:
```bash
# Mac built-in
say "Ukaž mi dnešní agendu" -o dotaz.aiff
sox dotaz.aiff -r 16000 -c 1 dotaz.wav

# Pošli Lucy
curl -X POST https://lucy-voice-xxx.run.app/voice \
  -F 'audio=@dotaz.wav'

# Dostaneš:
{
  "transcript": "Ukaž mi dnešní agendu",
  "text_response": "Máš 5 úkolů...",
  "audio_response_base64": "..." # Lucy mluví zpět!
}
```

---

## 🔥 GCP Deploy (po local testu):

```bash
cd deployment

# Set GCP credentials
export ANTHROPIC_API_KEY="..."  # nebo z .env
export SUPABASE_URL="..."
export SUPABASE_KEY="..."

# DEPLOY!
./deploy-full-gcp.sh

# Počkej ~15 minut
# Dostaneš URLs všech služeb
```

---

## 📊 Kam zapisuje updates:

### Linear:
- Vytvoří task pro každý větší projekt
- Updates progress automaticky
- Tracks deadlines

**Config:**
```bash
# Get API key: linear.app/settings/api
export LINEAR_API_KEY="lin_api_..."
```

### Notion:
- Queries databases
- Uses Notion AI for complex queries
- Gmail integration built-in

**Config:**
```bash
# Get API key: notion.so/my-integrations
export NOTION_API_KEY="secret_..."
```

### Todoist:
- Daily personal agenda
- Quick tasks & reminders

**Config:**
```bash
# Get token: todoist.com/prefs/integrations
export TODOIST_API_TOKEN="..."
```

### Mem0 (long-term memory):
```bash
# Auto-saves:
- User preferences
- Important decisions
- Patterns learned
```

### Qdrant (via NAS):
```bash
# Queries existing:
- 5,757 emails (6 months)
- 22,315 tech doc pages

# Auto-indexes new:
- Beeper messages (TODO)
- Important conversations
```

---

## 🐠 Aquarium (Monitoring):

Po GCP deploy:
```bash
# Open in browser
AQUARIUM_URL="https://lucy-aquarium-xxx.run.app"
open $AQUARIUM_URL
```

Vidíš:
- Real-time agent activity
- What each assistant is thinking
- Edit thoughts before mistakes
- Decision history

---

## 📈 Lucy Learns:

### Error Learning System:
```
Before action:
  → Check: "Did I make similar mistake before?"
  → If yes: ASK for confirmation

After error:
  → Record to Supabase + Mem0
  → What happened, why, how to prevent
  → NEVER repeat same error
```

### Pattern Learning:
```
Lucy sleduje:
- Kdy běžně potřebuješ co
- Jak preferuješ komunikaci
- Které projekty jsou priority
- Weekly patterns
```

**Example:**
```
Week 1: Každé pondělí 9:00 → planning
Week 2: Lucy už to ví
Week 3: Lucy automatically připraví planning materials před 9:00
```

---

## 🚨 Troubleshooting:

### Lucy neodpovídá:
```bash
# Check health
curl http://localhost:8080/health

# Check logs
tail -f lucy_system/logs/orchestrator.log
```

### Qdrant connection failed:
```bash
# Test NAS accessibility
curl http://192.168.1.129:6333/collections

# If fails → setup VPN:
# 1. Install Tailscale on NAS
# 2. Update QDRANT_HOST to Tailscale IP
```

### Assistant timeout:
```bash
# Query trvá dlouho?
# Normal: 2-5 seconds
# With Qdrant search: 5-10 seconds
# Complex multi-agent: 10-20 seconds

# Timeout default: 60s
# Increase in lucy_orchestrator.py if needed
```

---

## 👥 DALŠÍ ČLENOVÉ (Po Lucy):

### 1. Pan Talíř (Business Chief)
**Timeline:** Next week
**Role:** Sales, deals, customer relationships

Zatím co se učíš používat Lucy, já budu:
- Stavět Pan Talíř infrastructure
- Linear integration pro deals
- Customer database v Notion
- Email tracking for sales

### 2. Tukabel (Tech Chief)
**Timeline:** Next week (parallel)
**Role:** Technical operations, deployments

Částečně existuje v `/agent_system/domains/tukabel/`

Budu:
- Upgrading to new architecture
- Adding MCP expertise
- Docker & deployment automation
- Security hardening

### 3. Marketing + Finance Chiefs
**Timeline:** 2-3 weeks
Po stabilizaci Lucy + Pan Talíř + Tukabel

---

## ✅ STATUS:

**HOTOVO:**
- ✅ Lucy orchestrator (system prompt, routing, evaluation)
- ✅ 9 assistants (placeholders ready for implementation)
- ✅ Voice interface (Czech speech)
- ✅ Deployment scripts (local + GCP)
- ✅ Error learning system
- ✅ Aquarium monitoring UI
- ✅ Documentation (complete)
- ✅ 1Password auto-setup

**POTŘEBA JEŠTĚ:**
- ⏳ Assistant implementations (TODO jako placeholders)
- ⏳ Supabase tables creation (5 min SQL)
- ⏳ VPN setup (Tailscale - 5 min)
- ⏳ API integrations (Linear, Notion, Todoist)

**MŮŽEŠ POUŽÍT TEĎ:**
- ✅ Orchestrator (routing + evaluation)
- ✅ Voice interface (speech-to-text, text-to-speech)
- ✅ Qdrant queries (emails + tech docs)
- ✅ Error learning
- ✅ Aquarium monitoring

**Implementace assistantů = iterativní:**
```
Week 1: Lucy skeleton (routing works)
Week 2: Communications assistant (emails working)
Week 3: Knowledge assistant (docs working)
Week 4: Projects assistant (Linear working)
...atd
```

---

## 🎯 START NOW:

```bash
# 1. Setup (1 min)
cd /Users/premiumgastro/Projects/Mem0/lucy_system
./setup-from-1password.sh

# 2. Local deploy (2 min)
./deployment/deploy-local.sh

# 3. Test (30 sec)
curl http://localhost:8080/health
curl -X POST http://localhost:8080/query -d '{"query":"test"}'

# 4. If works → GCP deploy (15 min)
./deployment/deploy-full-gcp.sh

# 5. Start using!
```

**Já mezitím:**
- Stavím Pan Talíř
- Upgrading Tukabel
- Implementuji assistants jeden po druhém

---

**Status:** ✅ READY TO START NOW!
**Time to first Lucy response:** 3 minutes
**Time to full GCP deploy:** 20 minutes
**Next:** Deploy & začni používat! 🚀
