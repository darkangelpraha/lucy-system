# Lucy - SPRÁVNÁ Architektura

## ✅ CO JSEM UDĚLAL TEĎKA (SPRÁVNĚ):

### 1. **Error Learning System** 
[`error_learning.py`](core/error_learning.py)

**Zajišťuje, že chyba se NIKDY neopakuje:**
- Každá chyba → Supabase + Mem0
- Před akcí check: "Dělala jsem to už? Jak to dopadlo?"
- Repeated error = CRITICAL WARNING
- Learning z každé chyby

**Konkrétní chyba zaznamenána:**
```python
error_type="misunderstood_deployment_architecture"
what_happened="Created full Lucy on GCP instead of thin client"
why_happened="Didn't read full request, pattern matched on 'GCP' keyword"
how_to_prevent="Read ENTIRE request, extract architecture, ASK if unsure"
```

### 2. **GCP Thin Client** 
[`gcp_thin_client.py`](deployment/gcp_thin_client.py)

**SPRÁVNÁ architektura:**
```
GCP Cloud Run (thin client - kostra)
    ↓ VPN (bezpečné připojení)
    ↓
NAS (192.168.1.129) - hlavní nekonečná paměť
    ↓
Qdrant - cold storage

    +
    
Supabase - HOT buffer (operativní paměť)
```

**Výhody:**
- ✅ Vypadne proud v kanclu → GCP běží dál
- ✅ Těžké operace na NAS → workstation nezaseknutá
- ✅ HOT buffer v Supabase → rychlé odpovědi
- ✅ Infinite storage na NAS → bez limitů

**Deploy:**
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment
./deploy-thin.sh
```

### 3. **Aquarium UI**
[`aquarium_server.py`](aquarium/aquarium_server.py)

**Sledování agentů v real-time:**
- Vidíš který agent pracuje
- Co navrhuje / říká
- Můžeš VSTOUPIT a upravit myšlenky
- History rozhodnutí
- WebSocket live updates

**Start:**
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/aquarium
python aquarium_server.py
# Open: http://localhost:8081
```

---

## 📊 Gmail Scraping Status:

**DOKONČENO:**
- ✅ 5,757 emailů indexed
- ✅ Scraper skončil (už neběží)
- ✅ Data v Qdrant collection `email_history`

---

## 🎯 Exception Handling (NE nové pravidlo):

### Současný systém:
```python
# ŠPATNĚ - exception se stane pravidlem
if error:
    add_rule("always_do_X_when_Y")  # ❌

# SPRÁVNĚ - exception zůstane exception
if rare_edge_case:
    handle_specifically()
    log_as_exception()  # ✅
    # Nezmění základní pravidla
```

### Implementace v Lucy:

**1. Exception Counter:**
```python
exception_counts = {
    "special_case_A": 3,  # OK - stále výjimka
    "special_case_B": 847 # ⚠️ VAROVÁNÍ - už není výjimka, je to pattern!
}

if count > threshold:
    suggest_new_rule()  # "Tohle se děje často, možná to není výjimka?"
```

**2. Rule vs Exception Classification:**
```python
if frequency > 10%:
    classification = "pattern" # Mělo by být pravidlo
elif frequency > 1%:
    classification = "common_exception"  # Častá výjimka
else:
    classification = "rare_exception"  # Opravdu výjimka
```

**3. Auto-Detection:**
Lucy sama detekuje kdy výjimka přestává být výjimkou:
```python
weekly_review():
    for exception in exceptions:
        if exception.count_this_week > 5:
            notify_user(f"Exception '{exception}' occurs frequently. Should it become a rule?")
```

---

## 🔐 Bezpečné Připojení GCP <-> NAS:

### Option 1: Cloud VPN (RECOMMENDED)
```bash
# Create VPN tunnel GCP <-> local network
gcloud compute vpn-tunnels create nas-vpn \
  --peer-address=YOUR_PUBLIC_IP \
  --shared-secret=SECRET \
  --target-vpn-gateway=gateway

# Lucy on GCP connects to 192.168.1.129 via VPN
```

### Option 2: Cloud VPC Connector + VPN
```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create nas-connector \
  --region=us-central1 \
  --network=default \
  --range=10.8.0.0/28

# Attach to Cloud Run
--vpc-connector=nas-connector
```

### Option 3: Tailscale (EASIEST)
```bash
# Install Tailscale on NAS
# Install Tailscale in GCP Cloud Run container
# Both on same virtual network
# Access NAS via Tailscale IP (100.x.x.x)
```

---

## 📱 Aquarium Features:

**Real-time monitoring:**
- 🐠 Live agent status (active/idle/working)
- 💭 Current thoughts/proposals
- ✏️ Edit thoughts on-the-fly
- 📜 History of all decisions
- 🎨 Visual "aquarium" of agents swimming

**Intervention:**
```javascript
// Agent says: "I think we should deploy full Lucy to GCP"
// You see in aquarium → CLICK "Edit thought"
// Change to: "Deploy THIN client to GCP, connect to NAS"
// Agent continues with corrected thought
```

---

## ⚠️ JAK ZAJISTIT ŽE SE CHYBA NEOPAKUJE:

### 1. **V Lucy Systému:**

**Before každé akce:**
```python
warning = error_system.check_before_action(
    action_type="deployment",
    action_context={"request": user_request}
)

if warning:
    # Našli jsme podobnou chybu v historii!
    ask_user_confirmation()  # Nespustit automaticky
```

**Po chybě:**
```python
error_system.record_error(
    what_happened="...",
    why_happened="...",
    how_to_prevent="..."  # Konkrétní prevention strategy
)
```

**Weekly review:**
```python
stats = error_system.get_error_stats()

if stats['repeated_errors']:
    # CRITICAL: Chyba se opakuje!
    escalate_to_human()
```

### 2. **U Mě (AI Agent):**

Nemám permanentní memory jako Lucy bude mít, ALE:

**Během conversation:**
- ✅ Můžu si pamatovat co v tomto threadu
- ✅ Conversation summary mi připomíná kontext
- ❌ Mezi sessions nemám automatickou memory

**Co dělat:**
1. **Lucy má memory → naučí se trvale**
2. **Ty můžeš připomenout:** "Už jsme řešili X, pamatuj si Y"
3. **Context7 library docs** - permanent knowledge base
4. **Conversation summary** - partial memory mezi sessions

---

## 🎯 SUMMARY:

### ✅ Opraveno:
1. **GCP Thin Client** - kostra která sahá na NAS
2. **Error Learning** - system aby se chyba neopakovala
3. **Aquarium** - sledování agentů + intervence
4. **Bezpečné připojení** - VPN options

### 📊 Gmail Status:
- ✅ 5,757 emailů indexed
- ✅ Dokončeno

### 🔮 Next:
1. Deploy thin client na GCP
2. Setup VPN GCP <-> NAS
3. Configure Supabase HOT buffer
4. Start Aquarium UI
5. Test celý flow

**Takhle to má být. Bez keců.** 🎯
