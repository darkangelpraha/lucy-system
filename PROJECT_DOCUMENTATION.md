# Lucy Multi-Assistant System - Complete Project Documentation

## Executive Summary

Lucy is a production-ready multi-assistant AI system with persistent memory, learning capabilities, and real-time monitoring. The system consists of 9 specialized AI assistants coordinated by a smart orchestrator, backed by Mem0 for memory and Qdrant for knowledge retrieval.

**Version:** 1.0.0  
**Date:** January 11, 2026  
**Status:** Production Ready  
**Deployment:** GCP Cloud Run (Recommended) | Local Development

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Infrastructure](#infrastructure)
5. [Deployment Guide](#deployment-guide)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Monitoring](#monitoring)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

### Purpose
Lucy serves as an intelligent personal assistant for Premium Gastro CEO, handling:
- Email and communication management
- Project and task coordination
- Knowledge base queries
- Automation workflows
- Database operations
- Development support
- Business operations

### Key Features
- **9 Specialized Assistants** - Domain-specific expertise
- **Smart Orchestration** - Automatic query routing
- **Persistent Memory** - Learns from interactions via Mem0
- **Knowledge Base** - 28K+ documents indexed in Qdrant
- **Real-time Monitoring** - Aquarium dashboard
- **Multi-interface** - Web chat, CLI, REST API
- **Cloud Native** - Docker & GCP Cloud Run ready

### Technology Stack

**Backend:**
- FastAPI (async web framework)
- Python 3.11+
- Uvicorn (ASGI server)

**AI & ML:**
- Anthropic Claude Sonnet 4.5
- Mem0 (memory & learning)
- Qdrant (vector database)

**Infrastructure:**
- Docker & Docker Compose
- GCP Cloud Run
- Terraform (IaC)
- GitHub Actions (CI/CD)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
├─────────────────────────────────────────────────────────┤
│  Web Chat UI  │  CLI  │  REST API  │  Aquarium Monitor │
└────────┬────────────────────┬────────────────┬──────────┘
         │                    │                │
         v                    v                v
┌─────────────────────────────────────────────────────────┐
│              Lucy Orchestrator (Port 8080)               │
│  - Query routing                                         │
│  - Multi-domain coordination                             │
│  - Response aggregation                                  │
└────────┬────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────────────┐
│                  9 Specialized Assistants                │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Comms        │ Projects     │ Knowledge    │ Content    │
│ Data         │ Dev          │ Business     │ Personal   │
│ Evaluator    │              │              │            │
└──────┬───────┴──────┬───────┴──────┬───────┴────┬───────┘
       │              │              │            │
       v              v              v            v
┌─────────────────────────────────────────────────────────┐
│                   Storage Layer                          │
├──────────────┬──────────────┬──────────────────────────┤
│  Mem0        │  Qdrant      │  Local Files             │
│  (Memory)    │  (Vectors)   │  (Logs, Config)          │
└──────────────┴──────────────┴──────────────────────────┘
```

### Component Interaction Flow

1. **Query Reception**: Client sends query via Web/CLI/API
2. **Routing**: Orchestrator analyzes and routes to appropriate assistant(s)
3. **Memory Retrieval**: Each assistant checks Mem0 for relevant memories
4. **Knowledge Search**: Qdrant searches for relevant documents
5. **AI Processing**: Claude generates response with context
6. **Learning**: Interactions saved to Mem0 for future improvement
7. **Response**: Aggregated response returned to client

---

## Components

### 1. Lucy Orchestrator (`orchestrator/lucy_orchestrator.py`)

**Purpose:** Central coordination and routing hub

**Key Functions:**
- `route_query(query: str)` - Automatically route query to appropriate assistant(s)
- `_execute_single_domain()` - Handle single-assistant queries
- `_execute_parallel()` - Handle multi-assistant queries
- `_aggregate_results()` - Combine results from multiple assistants

**Configuration:**
- Port: 8080
- Workers: 1 (async handles concurrency)
- Timeout: 300s

**Dependencies:**
- `lucy_config.py` - Assistant definitions
- `memory_manager.py` - Mem0 integration
- `knowledge/kb_manager.py` - Qdrant integration

### 2. Assistants (`assistants/assistant_server.py`)

**9 Specialized Domains:**

| Assistant | Domain | Collections | Description |
|-----------|--------|-------------|-------------|
| Communications | Email, Beeper | email_history (5,757) | Email management and messaging |
| Projects | Linear, GitHub | tech_docs | Task and project management |
| Knowledge | Docs, Research | tech_docs_vectors (22,315) | Technical documentation queries |
| Content | N8N, Automation | tech_docs_vectors | Workflow automation |
| Data | Qdrant, Supabase | tech_docs | Database operations |
| Dev | Docker, VSCode | tech_docs_vectors | Development tools support |
| Business | Finance, Invoices | emails, tech_docs | Business operations |
| Personal | Calendar, Notes | emails | Personal assistant tasks |
| Evaluator | QA, Performance | All collections | Quality assurance |

**Each Assistant Has:**
- Dedicated Mem0 namespace
- Specific Qdrant collection mappings
- Custom system prompts
- Domain-specific tools

### 3. Memory Manager (`memory_manager.py`)

**Purpose:** Persistent learning and memory storage

**Features:**
- **Memory Categories:**
  - `user_preference` - User preferences and patterns
  - `correction` - Learned corrections
  - `successful_pattern` - Proven successful approaches
  - `technical_knowledge` - Learned technical information
  - `bookmark` - Important saved items
  - `context` - Domain-specific context

**Storage:**
- Local JSON files: `lucy_memories/{namespace}.json`
- Cloud: Mem0 API integration (optional)

**Key Methods:**
```python
add_memory(namespace, content, category, metadata)
search_memories(namespace, query, category, limit)
delete_memory(namespace, memory_id)
```

### 4. Knowledge Base Manager (`knowledge/kb_manager.py`)

**Purpose:** Vector search across indexed documents

**Collections:**
- `email_history` - 5,757 email documents
- `tech_docs_vectors` - 22,315 technical documents
- `beeper_history` - Messaging history (optional)

**Search Methods:**
```python
search(collection, query, limit, filters)
get_stats() - Collection statistics
```

**Qdrant Configuration:**
- Host: 192.168.1.129 (configurable)
- Port: 6333
- Vector Size: 1536 (OpenAI embeddings)

### 5. Aquarium Monitoring (`aquarium/aquarium_server.py`)

**Purpose:** Real-time agent monitoring and intervention

**Features:**
- WebSocket live updates
- Agent status tracking
- Thought process visibility
- Manual intervention capability
- Decision history

**Port:** 8081

**Endpoints:**
- `GET /` - Dashboard UI
- `WebSocket /ws` - Live updates
- `POST /agent/status` - Agent status reporting

### 6. Web Chat Interface (`chat.html`)

**Purpose:** User-friendly chat interface

**Features:**
- Real-time messaging
- Typing indicators
- Connection status
- Message history
- Responsive design

**API Integration:**
- `POST /query` - Send query
- `GET /health` - Check orchestrator status

---

## Infrastructure

### Local Development

**Requirements:**
- Python 3.11+
- Docker (optional)
- Qdrant instance
- Environment variables (see .env.example)

**Ports:**
- 8080 - Lucy Orchestrator
- 8081 - Aquarium Monitoring
- 6333 - Qdrant (external)

**Start Locally:**
```bash
./start-lucy.sh
```

### Production Deployment (GCP Cloud Run)

**Architecture:**
```
Internet
  │
  ▼
Cloud Load Balancer
  │
  ├─> Lucy Orchestrator (Cloud Run Service)
  ├─> Lucy Aquarium (Cloud Run Service)
  ├─> Lucy Voice (Cloud Run Service)
  └─> 9x Assistant Services (Cloud Run Services)
       │
       ├─> Mem0 API (External)
       ├─> Qdrant Cloud (External)
       └─> Secret Manager (API Keys)
```

**GCP Services Used:**
- Cloud Run - Container hosting
- Cloud Build - CI/CD pipeline
- Secret Manager - API keys storage
- Cloud Storage - Logs and data
- Cloud Load Balancing - Traffic distribution
- VPC Connector - Internal networking (optional)

**Deployment Script:**
```bash
./deployment/deploy-full-gcp.sh
```

**Terraform Infrastructure:**
```bash
cd deployment/terraform
terraform init
terraform plan
terraform apply
```

### Docker Deployment

**Single Container:**
```bash
docker build -t lucy-system .
docker run -p 8080:8080 -e LUCY_MODE=orchestrator lucy-system
```

**Multi-Container (docker-compose):**
```bash
docker-compose up -d
```

**Services:**
- lucy-orchestrator
- lucy-communications
- lucy-knowledge
- lucy-projects
- lucy-content
- lucy-data
- lucy-dev
- lucy-business
- lucy-personal
- lucy-evaluator
- lucy-aquarium

---

## Deployment Guide

### Prerequisites

1. **GCP Account Setup:**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **API Enablement:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

3. **Secrets Configuration:**
```bash
echo -n "YOUR_ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "YOUR_QDRANT_HOST" | gcloud secrets create qdrant-host --data-file=-
echo -n "YOUR_MEM0_KEY" | gcloud secrets create mem0-api-key --data-file=-
```

### Step-by-Step Deployment

**1. Build Container Images:**
```bash
cd deployment
gcloud builds submit --config cloudbuild.yaml ..
```

**2. Deploy Orchestrator:**
```bash
gcloud run deploy lucy-orchestrator \
  --image gcr.io/YOUR_PROJECT/lucy-system:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars LUCY_MODE=orchestrator \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest"
```

**3. Deploy Assistants:**
```bash
for assistant in communications knowledge projects content data dev business personal evaluator; do
  gcloud run deploy lucy-$assistant \
    --image gcr.io/YOUR_PROJECT/lucy-system:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 5 \
    --set-env-vars LUCY_MODE=assistant,LUCY_ASSISTANT=$assistant \
    --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest"
done
```

**4. Deploy Aquarium:**
```bash
gcloud run deploy lucy-aquarium \
  --image gcr.io/YOUR_PROJECT/lucy-system:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars LUCY_MODE=aquarium
```

**5. Configure Load Balancer (Optional):**
```bash
# Create backend services
gcloud compute backend-services create lucy-backend \
  --global \
  --load-balancing-scheme=EXTERNAL \
  --protocol=HTTP

# Add Cloud Run NEG
gcloud compute network-endpoint-groups create lucy-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=lucy-orchestrator

# Create URL map and frontend
gcloud compute url-maps create lucy-lb \
  --default-service=lucy-backend

gcloud compute target-http-proxies create lucy-proxy \
  --url-map=lucy-lb

gcloud compute forwarding-rules create lucy-frontend \
  --global \
  --target-http-proxy=lucy-proxy \
  --ports=80
```

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Claude API key
- `QDRANT_HOST` - Qdrant server URL
- `QDRANT_PORT` - Qdrant port (default: 6333)

**Optional:**
- `LUCY_MODE` - Service mode (orchestrator|assistant|aquarium|voice)
- `LUCY_ASSISTANT` - Assistant domain (when MODE=assistant)
- `MEM0_API_KEY` - Mem0 cloud API key
- `LUCY_ENV` - Environment (development|production)
- `LOG_LEVEL` - Logging level (DEBUG|INFO|WARNING|ERROR)

### Health Checks

**Orchestrator:**
```bash
curl https://YOUR_SERVICE_URL/health
```

Expected response:
```json
{
  "orchestrator": "healthy",
  "assistants": {...},
  "status": "healthy",
  "timestamp": "2026-01-11T14:30:00"
}
```

---

## API Reference

### REST API Endpoints

#### POST /query
Execute query through Lucy system

**Request:**
```json
{
  "query": "show me recent emails",
  "domain": "communications",  // optional
  "context": {...}  // optional
}
```

**Response:**
```json
{
  "domain": "communications",
  "assistant": "Lucy-Communications",
  "memories": [...],
  "knowledge_base_results": {...},
  "response": "Found 10 recent emails...",
  "timestamp": "2026-01-11T14:30:00"
}
```

#### GET /health
System health check

**Response:**
```json
{
  "orchestrator": "healthy",
  "assistants": {
    "communications": "healthy",
    ...
  },
  "status": "healthy",
  "timestamp": "2026-01-11T14:30:00"
}
```

#### POST /learn
Save correction/learning

**Request:**
```json
{
  "original_query": "show tasks",
  "correction": "Should show only ACTIVE tasks by default",
  "domain": "projects"
}
```

#### POST /remember
Save user preference

**Request:**
```json
{
  "content": "Prefer Python examples over JavaScript",
  "category": "preference",
  "domain": "knowledge"
}
```

#### GET /memories
List memories

**Query Parameters:**
- `domain` - Filter by domain
- `category` - Filter by category
- `limit` - Max results (default: 100)

### CLI Commands

```bash
# Query
lucy query "your question"

# With specific domain
lucy query "your question" --domain knowledge

# Save learning
lucy learn "original" "correction" --domain projects

# Save preference
lucy remember "preference" --category type --domain assistant

# List memories
lucy list-memories --domain knowledge --category correction

# System stats
lucy stats
```

### WebSocket API (Aquarium)

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8081/ws');
```

**Messages:**
```json
{
  "type": "agent_status",
  "agent_id": "agent_001",
  "status": {
    "name": "Lucy Coordinator",
    "status": "working",
    "thought": "Analyzing query...",
    "active": true
  },
  "timestamp": "2026-01-11T14:30:00"
}
```

---

## Configuration

### lucy_config.py

**Assistant Configuration:**
```python
LUCY_ASSISTANTS = {
    LucyDomain.COMMUNICATIONS: LucyAssistantConfig(
        name="Lucy-Communications",
        domain=LucyDomain.COMMUNICATIONS,
        description="Email and messaging management",
        collections=["email_history", "beeper_history"],
        mem0_namespace="lucy_communications",
        system_prompt="..."
    ),
    ...
}
```

**Keyword Routing:**
```python
KEYWORD_ROUTING = {
    "email": [LucyDomain.COMMUNICATIONS],
    "task": [LucyDomain.PROJECTS],
    "docs": [LucyDomain.KNOWLEDGE],
    ...
}
```

### Environment Files

**.env (Local Development):**
```bash
ANTHROPIC_API_KEY=sk-ant-...
QDRANT_HOST=192.168.1.129
QDRANT_PORT=6333
MEM0_API_KEY=mem0_...
LUCY_ENV=development
LOG_LEVEL=DEBUG
```

**.env.production (GCP):**
```bash
# Loaded from Secret Manager
ANTHROPIC_API_KEY=${secret:anthropic-api-key}
QDRANT_HOST=${secret:qdrant-host}
MEM0_API_KEY=${secret:mem0-api-key}
LUCY_ENV=production
LOG_LEVEL=INFO
```

---

## Monitoring

### Aquarium Dashboard

**URL:** http://localhost:8081 (local) or https://lucy-aquarium-XXX.run.app (GCP)

**Features:**
- Real-time agent status
- Thought process visualization
- Active conversations
- Decision history
- Manual intervention controls

### Logs

**Local:**
```bash
tail -f lucy.log
tail -f aquarium.log
```

**GCP Cloud Run:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lucy-orchestrator" --limit 100 --format json
```

### Metrics

**Key Metrics to Monitor:**
- Request rate (queries/minute)
- Response latency (p50, p95, p99)
- Error rate (%)
- Memory usage (MB)
- CPU utilization (%)
- Assistant availability (%)

**GCP Monitoring:**
```bash
# Create custom metrics
gcloud monitoring metrics-descriptors create \
  --metric-type=custom.googleapis.com/lucy/queries \
  --value-type=INT64 \
  --metric-kind=DELTA
```

---

## Security

### API Keys

**Storage:**
- Local: .env file (gitignored)
- GCP: Secret Manager

**Access Control:**
```bash
# Grant service account access to secrets
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Network Security

**GCP:**
- Cloud Run services use IAM for authentication
- VPC Connector for internal traffic
- Cloud Armor for DDoS protection (optional)

**Firewall Rules:**
```bash
# Allow only HTTPS traffic
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0
```

### Data Privacy

**Sensitive Data Handling:**
- Email content encrypted at rest
- API responses sanitized
- Logs exclude PII
- Memory deletion on request

---

## Troubleshooting

### Common Issues

**1. Port Already in Use:**
```bash
# Check what's using the port
lsof -iTCP:8080 -sTCP:LISTEN

# Kill process if needed
kill -9 <PID>

# Or use management script
./stop-lucy.sh
```

**2. Qdrant Connection Failed:**
```bash
# Check Qdrant status
curl http://QDRANT_HOST:6333/health

# Verify network connectivity
ping QDRANT_HOST

# Check firewall rules
```

**3. Memory Not Persisting:**
```bash
# Check file permissions
ls -la lucy_memories/

# Verify Mem0 API key
echo $MEM0_API_KEY

# Check logs for errors
grep -i "memory" lucy.log
```

**4. GCP Deployment Fails:**
```bash
# Check build logs
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")

# Verify secrets exist
gcloud secrets list

# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID
```

### Debug Mode

**Enable verbose logging:**
```bash
export LOG_LEVEL=DEBUG
python launcher.py
```

**Test individual components:**
```bash
# Test orchestrator
python -m orchestrator.lucy_orchestrator

# Test memory manager
python -m memory_manager

# Test knowledge base
python -m knowledge.kb_manager
```

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/darkangelpraha/lucy-system.git
cd lucy-system

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests
pytest tests/e2e

# Coverage report
pytest --cov=. --cov-report=html
```

### Code Style

**Formatter:** Black
```bash
black .
```

**Linter:** Flake8
```bash
flake8 .
```

**Type Checker:** MyPy
```bash
mypy .
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: Your feature description

Source: Lucy Development
Linear: LUCY-XXX
GitHub: darkangelpraha/lucy-system"

# Push and create PR
git push origin feature/your-feature
gh pr create
```

---

## Maintenance

### Backup

**Memory Files:**
```bash
# Backup memories
tar -czf lucy-memories-$(date +%Y%m%d).tar.gz lucy_memories/

# Restore memories
tar -xzf lucy-memories-YYYYMMDD.tar.gz
```

**Configuration:**
```bash
# Backup config
cp .env .env.backup
cp lucy_config.py lucy_config.py.backup
```

### Updates

**Python Dependencies:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

**Docker Images:**
```bash
# Rebuild images
docker-compose build --no-cache

# Update GCP
gcloud builds submit --config cloudbuild.yaml .
```

### Scaling

**Horizontal Scaling (GCP):**
```bash
# Increase max instances
gcloud run services update lucy-orchestrator \
  --max-instances 50

# Auto-scaling metrics
gcloud run services update lucy-orchestrator \
  --cpu-throttling \
  --concurrency 100
```

**Vertical Scaling:**
```bash
# Increase resources
gcloud run services update lucy-orchestrator \
  --memory 4Gi \
  --cpu 4
```

---

## License

Proprietary - Premium Gastro

---

## Support

**Repository:** https://github.com/darkangelpraha/lucy-system  
**Issues:** https://github.com/darkangelpraha/lucy-system/issues  
**Wiki:** https://github.com/darkangelpraha/lucy-system/wiki

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Document Version:** 1.0.0  
**Last Updated:** January 11, 2026  
**Author:** Premium Gastro Development Team
