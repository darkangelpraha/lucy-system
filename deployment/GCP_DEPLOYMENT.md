# Lucy AI Assistant - GCP Deployment Guide

Complete guide for deploying Lucy to Google Cloud Platform.

---

## 📋 Prerequisites

### 1. GCP Account & Project
- Active GCP account
- Billing enabled
- Project ID ready

### 2. Local Tools
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Docker
# macOS: Download from https://www.docker.com/products/docker-desktop
# Linux: sudo apt-get install docker.io

# Install Terraform (optional)
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads
```

### 3. API Keys
- **Anthropic API Key** - Claude access
- **OpenAI API Key** (optional) - GPT access  
- **Mem0 API Key** (optional) - Memory service
- **Qdrant** - Host/IP address (can be local with VPN)

---

## 🚀 Quick Deploy

### Option A: One-Command Deploy

```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment

# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export ANTHROPIC_API_KEY="your-anthropic-key"
export QDRANT_HOST="192.168.1.129:6333"  # or cloud Qdrant

# Deploy
./deploy.sh
```

### Option B: Step-by-Step Deploy

#### 1. Authenticate with GCP
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  compute.googleapis.com
```

#### 3. Create Secrets
```bash
# Anthropic API Key
echo -n "YOUR_ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Qdrant Host
echo -n "192.168.1.129:6333" | gcloud secrets create qdrant-host \
  --data-file=- \
  --replication-policy="automatic"

# OpenAI (optional)
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key \
  --data-file=- \
  --replication-policy="automatic"
```

#### 4. Build & Push Docker Image
```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system

# Configure Docker for GCR
gcloud auth configure-docker

# Build image
docker build -t gcr.io/YOUR_PROJECT_ID/lucy-assistant:latest \
  -f deployment/Dockerfile .

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/lucy-assistant:latest
```

#### 5. Deploy to Cloud Run
```bash
# Deploy Orchestrator
gcloud run deploy lucy-orchestrator \
  --image=gcr.io/YOUR_PROJECT_ID/lucy-assistant:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --set-env-vars="LUCY_ENV=production,LUCY_MODE=orchestrator" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest,QDRANT_HOST=qdrant-host:latest"

# Deploy Communications Assistant
gcloud run deploy lucy-communications \
  --image=gcr.io/YOUR_PROJECT_ID/lucy-assistant:latest \
  --region=us-central1 \
  --platform=managed \
  --no-allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=5 \
  --set-env-vars="LUCY_ENV=production,LUCY_ASSISTANT=communications" \
  --set-secrets="QDRANT_HOST=qdrant-host:latest"

# Deploy Knowledge Assistant
gcloud run deploy lucy-knowledge \
  --image=gcr.io/YOUR_PROJECT_ID/lucy-assistant:latest \
  --region=us-central1 \
  --platform=managed \
  --no-allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=5 \
  --set-env-vars="LUCY_ENV=production,LUCY_ASSISTANT=knowledge" \
  --set-secrets="QDRANT_HOST=qdrant-host:latest"
```

---

## 🏗️ Infrastructure Options

### Option 1: Cloud Run (Recommended)
**Pros:**
- ✅ Serverless - no server management
- ✅ Auto-scaling (0 to N instances)
- ✅ Pay per use
- ✅ Simple deployment
- ✅ HTTPS out of the box

**Cons:**
- ⚠️ Cold starts (~2-5 seconds)
- ⚠️ 300 second timeout
- ⚠️ Stateless (use external storage)

**Best for:** Production, cost-effective, simple ops

### Option 2: GKE (Kubernetes)
**Pros:**
- ✅ Full control
- ✅ Complex orchestration
- ✅ Multi-region
- ✅ Advanced networking

**Cons:**
- ⚠️ Complex setup
- ⚠️ Higher costs
- ⚠️ Requires K8s expertise

**Best for:** Large scale, complex requirements

### Option 3: Compute Engine VMs
**Pros:**
- ✅ Full control
- ✅ Stateful possible
- ✅ Custom OS/software

**Cons:**
- ⚠️ Manual scaling
- ⚠️ Server management
- ⚠️ Higher maintenance

**Best for:** Legacy apps, special requirements

---

## 🗄️ Data Storage Options

### Qdrant Deployment

#### Option A: Keep Local (VPN Tunnel)
```bash
# Create Cloud VPN to your local network
# Lucy on GCP → VPN → Local Qdrant (192.168.1.129:6333)

# Pros: Existing setup, no migration
# Cons: VPN dependency, latency
```

#### Option B: Qdrant Cloud
```bash
# Sign up at https://cloud.qdrant.io
# Create cluster
# Migrate data from local to cloud

# Pros: Managed, scalable, global
# Cons: Cost, migration effort
```

#### Option C: Self-Hosted on GCP
```bash
# Deploy Qdrant on GCP Compute Engine or GKE
# Migrate local data to GCP instance

# Terraform example in deployment/terraform/qdrant.tf
```

### Mem0 Deployment

#### Option A: Mem0 Cloud
```bash
# Use Mem0's hosted service
# API key in secrets

# Pros: Managed, simple
# Cons: Cost, vendor lock-in
```

#### Option B: Self-Hosted
```bash
# Deploy Mem0 on GCP
# Use Cloud SQL for storage

# See deployment/terraform/mem0.tf
```

---

## 🔒 Security Best Practices

### 1. Secret Management
```bash
# NEVER commit secrets to git
# Use Secret Manager for all credentials
# Rotate secrets regularly

# Grant least privilege access
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:lucy-sa@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 2. Network Security
```bash
# Use VPC for internal communication
# Enable Cloud Armor for DDoS protection
# Use Identity-Aware Proxy for admin access
```

### 3. Service Accounts
```bash
# Create dedicated service account
gcloud iam service-accounts create lucy-assistant-sa \
  --display-name="Lucy AI Assistant"

# Grant minimal permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:lucy-assistant-sa@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📊 Monitoring & Logging

### Cloud Logging
```bash
# View logs
gcloud run services logs read lucy-orchestrator --region=us-central1

# Stream logs
gcloud run services logs tail lucy-orchestrator --region=us-central1

# Filter logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lucy-orchestrator" \
  --limit 50 \
  --format json
```

### Cloud Monitoring
```bash
# Create uptime check
gcloud monitoring uptime-checks create lucy-health \
  --display-name="Lucy Orchestrator Health" \
  --resource-type=uptime-url \
  --http-check-path=/health

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL \
  --display-name="Lucy High Error Rate" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s
```

### Metrics Dashboard
- Request count
- Response time (p50, p95, p99)
- Error rate
- Memory usage
- CPU usage
- Active instances

---

## 💰 Cost Optimization

### Cloud Run Pricing
```
Instance hours: $0.00002400 per vCPU-second
               $0.00000250 per GiB-second
Requests:      $0.40 per million requests
```

### Example Monthly Cost (Light usage):
```
Orchestrator (2 CPU, 2GB):
  - 100 hours/month runtime
  - 10,000 requests
  = ~$20/month

3 Assistants (1 CPU, 1GB each):
  - 50 hours/month each
  - 5,000 requests each
  = ~$15/month

Total: ~$35/month
```

### Cost Saving Tips:
1. **Min instances = 0** - Scale to zero when idle
2. **Request timeout** - Set to minimum needed
3. **CPU allocation** - "CPU allocated only during request processing"
4. **Memory** - Right-size (don't over-provision)
5. **Concurrency** - Increase to 80-100 per instance

---

## 🔧 Terraform Deployment (Advanced)

```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system/deployment/terraform

# Initialize
terraform init

# Plan
terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="region=us-central1" \
  -var="environment=production"

# Apply
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="region=us-central1" \
  -var="environment=production"
```

---

## 🧪 Testing Deployment

### 1. Health Check
```bash
ORCHESTRATOR_URL=$(gcloud run services describe lucy-orchestrator \
  --region=us-central1 \
  --format='value(status.url)')

curl $ORCHESTRATOR_URL/health
```

### 2. Test Query
```bash
curl -X POST $ORCHESTRATOR_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me emails about projects"}'
```

### 3. Load Test
```bash
# Install Apache Bench
# macOS: already installed
# Linux: sudo apt-get install apache2-utils

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -T "application/json" \
  -p query.json \
  $ORCHESTRATOR_URL/query
```

---

## 🚨 Troubleshooting

### Issue: Container won't start
```bash
# Check logs
gcloud run services logs read lucy-orchestrator --region=us-central1 --limit=50

# Common fixes:
# 1. Check Dockerfile CMD is correct
# 2. Verify secrets are accessible
# 3. Check memory/CPU limits
```

### Issue: High latency
```bash
# Check metrics
gcloud monitoring time-series list \
  --filter="resource.type=cloud_run_revision"

# Fixes:
# 1. Increase min instances (reduce cold starts)
# 2. Optimize code (profiling)
# 3. Use caching
# 4. Increase memory/CPU
```

### Issue: Secrets not accessible
```bash
# Verify secret exists
gcloud secrets describe anthropic-api-key

# Check IAM permissions
gcloud secrets get-iam-policy anthropic-api-key

# Grant access
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📈 Scaling Strategy

### Horizontal Scaling (Cloud Run)
```bash
# Set max instances
--max-instances=10

# Set min instances (reduce cold starts)
--min-instances=1

# Concurrency (requests per instance)
--concurrency=80
```

### Vertical Scaling
```bash
# Increase resources per instance
--memory=4Gi
--cpu=4
```

### Multi-Region
```bash
# Deploy to multiple regions
REGIONS=("us-central1" "europe-west1" "asia-southeast1")

for region in "${REGIONS[@]}"; do
  gcloud run deploy lucy-orchestrator-$region \
    --image=gcr.io/PROJECT/lucy-assistant:latest \
    --region=$region \
    ...
done

# Use Cloud Load Balancer for global distribution
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy Lucy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - uses: google-github-actions/setup-gcloud@v1
      
      - name: Build and push
        run: |
          gcloud builds submit \
            --config=deployment/cloudbuild.yaml
```

### Cloud Build Trigger
```bash
# Create trigger from GitHub
gcloud builds triggers create github \
  --repo-name=lucy-assistant \
  --repo-owner=YOUR_GITHUB \
  --branch-pattern="^main$" \
  --build-config=deployment/cloudbuild.yaml
```

---

## 📱 Client Access

### Web Interface
```bash
# Deploy frontend (optional)
# See deployment/frontend/ for React app
```

### API Client
```python
import requests

LUCY_URL = "https://lucy-orchestrator-xxx.run.app"

response = requests.post(
    f"{LUCY_URL}/query",
    json={"query": "Show me emails about Qdrant"},
    headers={"Authorization": "Bearer YOUR_TOKEN"}  # if auth enabled
)

print(response.json())
```

### CLI Client
```bash
# Local CLI talks to GCP Lucy
cd /Users/premiumgastro/Projects/Mem0/lucy_system

# Configure remote endpoint
export LUCY_ENDPOINT="https://lucy-orchestrator-xxx.run.app"

# Query
python lucy query "Show me emails about projects"
```

---

## ✅ Production Checklist

- [ ] GCP project created & billing enabled
- [ ] All APIs enabled
- [ ] Secrets created in Secret Manager
- [ ] Docker image built & pushed to GCR
- [ ] Cloud Run services deployed
- [ ] Health checks passing
- [ ] Monitoring & logging configured
- [ ] Alerts set up
- [ ] Backup strategy defined
- [ ] Cost monitoring enabled
- [ ] Security review completed
- [ ] Load testing done
- [ ] Documentation updated
- [ ] Team trained on deployment

---

## 🆘 Support

### GCP Resources
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)
- [Cloud Build Docs](https://cloud.google.com/build/docs)

### Lucy Resources
- Lucy System Docs: `/lucy_system/docs/`
- Architecture: `/lucy_system/ARCHITECTURE.md`
- API Docs: `/lucy_system/API.md`

---

**Ready to deploy Lucy to the cloud!** 🚀☁️
