#!/bin/bash
set -e

# KOMPLETNÍ LUCY DEPLOYMENT NA GCP
# Project: Premium Gastro
# Všech 9 assistantů + orchestrator + voice interface

echo "🚀 LUCY FULL DEPLOYMENT - GCP Premium Gastro"
echo "=============================================="

# Configuration
PROJECT_ID="premium-gastro"
REGION="us-central1"
SERVICE_ACCOUNT="lucy-assistant@premium-gastro.iam.gserviceaccount.com"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# 1. AUTHENTICATE
log "Authenticating with GCP..."
gcloud config set project $PROJECT_ID
gcloud auth configure-docker gcr.io --quiet

# 2. ENABLE APIS
log "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  speech.googleapis.com \
  texttospeech.googleapis.com \
  cloudresourcemanager.googleapis.com \
  --project=$PROJECT_ID \
  --quiet

# 3. CREATE SECRETS (if not exist)
log "Setting up secrets..."

create_secret_if_not_exists() {
  SECRET_NAME=$1
  SECRET_VALUE=$2
  
  if ! gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
    echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME \
      --data-file=- \
      --replication-policy="automatic" \
      --project=$PROJECT_ID
    log "Created secret: $SECRET_NAME"
  else
    log "Secret exists: $SECRET_NAME"
  fi
}

# Read from environment or prompt
if [ -z "$ANTHROPIC_API_KEY" ]; then
  read -sp "Enter Anthropic API Key: " ANTHROPIC_API_KEY
  echo
fi

if [ -z "$QDRANT_HOST" ]; then
  QDRANT_HOST="192.168.1.129:6333"
fi

if [ -z "$SUPABASE_URL" ]; then
  read -p "Enter Supabase URL: " SUPABASE_URL
fi

if [ -z "$SUPABASE_KEY" ]; then
  read -sp "Enter Supabase Key: " SUPABASE_KEY
  echo
fi

create_secret_if_not_exists "anthropic-api-key" "$ANTHROPIC_API_KEY"
create_secret_if_not_exists "qdrant-host" "$QDRANT_HOST"
create_secret_if_not_exists "supabase-url" "$SUPABASE_URL"
create_secret_if_not_exists "supabase-key" "$SUPABASE_KEY"

# 4. BUILD DOCKER IMAGE
log "Building Lucy Docker image..."
docker build -t gcr.io/$PROJECT_ID/lucy-assistant:latest \
  -f deployment/Dockerfile.production \
  ..

# 5. PUSH TO GCR
log "Pushing to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/lucy-assistant:latest

# 6. DEPLOY ORCHESTRATOR (main coordinator)
log "Deploying Lucy Orchestrator..."
gcloud run deploy lucy-orchestrator \
  --image=gcr.io/$PROJECT_ID/lucy-assistant:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --min-instances=1 \
  --timeout=300 \
  --set-env-vars="LUCY_MODE=orchestrator,LUCY_ENV=production" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest,QDRANT_HOST=qdrant-host:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest" \
  --service-account=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --quiet

ORCHESTRATOR_URL=$(gcloud run services describe lucy-orchestrator \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

log "Orchestrator deployed: $ORCHESTRATOR_URL"

# 7. DEPLOY 9 ASSISTANTS

deploy_assistant() {
  NAME=$1
  DOMAIN=$2
  MEMORY=${3:-1Gi}
  
  log "Deploying Lucy-$NAME..."
  
  gcloud run deploy lucy-$NAME \
    --image=gcr.io/$PROJECT_ID/lucy-assistant:latest \
    --region=$REGION \
    --platform=managed \
    --no-allow-unauthenticated \
    --memory=$MEMORY \
    --cpu=1 \
    --max-instances=5 \
    --min-instances=0 \
    --timeout=300 \
    --set-env-vars="LUCY_MODE=assistant,LUCY_ASSISTANT=$DOMAIN,LUCY_ENV=production,ORCHESTRATOR_URL=$ORCHESTRATOR_URL" \
    --set-secrets="QDRANT_HOST=qdrant-host:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest" \
    --service-account=$SERVICE_ACCOUNT \
    --project=$PROJECT_ID \
    --quiet
}

# 9 Assistants deployment
deploy_assistant "communications" "communications" "1Gi"
deploy_assistant "knowledge" "knowledge" "1Gi"
deploy_assistant "projects" "projects" "1Gi"
deploy_assistant "content" "content" "1Gi"
deploy_assistant "data" "data" "1Gi"
deploy_assistant "dev" "dev" "1Gi"
deploy_assistant "business" "business" "1Gi"
deploy_assistant "personal" "personal" "1Gi"
deploy_assistant "evaluator" "evaluator" "512Mi"

# 8. DEPLOY VOICE INTERFACE
log "Deploying Voice Interface..."
gcloud run deploy lucy-voice \
  --image=gcr.io/$PROJECT_ID/lucy-assistant:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=5 \
  --min-instances=0 \
  --timeout=300 \
  --set-env-vars="LUCY_MODE=voice,ORCHESTRATOR_URL=$ORCHESTRATOR_URL" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --service-account=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --quiet

VOICE_URL=$(gcloud run services describe lucy-voice \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

# 9. DEPLOY AQUARIUM UI
log "Deploying Aquarium (monitoring UI)..."
gcloud run deploy lucy-aquarium \
  --image=gcr.io/$PROJECT_ID/lucy-assistant:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=3 \
  --min-instances=0 \
  --set-env-vars="LUCY_MODE=aquarium,ORCHESTRATOR_URL=$ORCHESTRATOR_URL" \
  --service-account=$SERVICE_ACCOUNT \
  --project=$PROJECT_ID \
  --quiet

AQUARIUM_URL=$(gcloud run services describe lucy-aquarium \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

# 10. SETUP IAM PERMISSIONS
log "Setting up IAM permissions..."
for service in lucy-communications lucy-knowledge lucy-projects lucy-content lucy-data lucy-dev lucy-business lucy-personal lucy-evaluator lucy-voice; do
  gcloud run services add-iam-policy-binding $service \
    --region=$REGION \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null || true
done

# 11. SUMMARY
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ LUCY FULLY DEPLOYED TO GCP - Premium Gastro"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 ENDPOINTS:"
echo "   Orchestrator:  $ORCHESTRATOR_URL"
echo "   Voice:         $VOICE_URL"
echo "   Aquarium:      $AQUARIUM_URL"
echo ""
echo "🤖 ASSISTANTS (9):"
echo "   • Lucy-Communications (emails, chats)"
echo "   • Lucy-Knowledge (docs, tech)"
echo "   • Lucy-Projects (Linear, GitHub)"
echo "   • Lucy-Content (N8N, automation)"
echo "   • Lucy-Data (Qdrant, Supabase)"
echo "   • Lucy-Dev (VSCode, Docker)"
echo "   • Lucy-Business (ops, finance)"
echo "   • Lucy-Personal (personal assistant)"
echo "   • Lucy-Evaluator (quality control)"
echo ""
echo "🎤 VOICE INTERFACE:"
echo "   curl -X POST $VOICE_URL/voice \\
     -F 'audio=@recording.wav'"
echo ""
echo "🐠 AQUARIUM (Monitoring):"
echo "   Open: $AQUARIUM_URL"
echo ""
echo "💬 CHAT WITH LUCY:"
echo "   curl -X POST $ORCHESTRATOR_URL/query \\
     -H 'Content-Type: application/json' \\
     -d '{\"query\": \"Show me emails about projects\"}'"
echo ""
echo "═══════════════════════════════════════════════════════════"
