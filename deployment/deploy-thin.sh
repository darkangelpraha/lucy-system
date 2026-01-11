#!/bin/bash
set -e

# Deploy THIN CLIENT to GCP Cloud Run
# Connects to NAS via VPN + Supabase buffer

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"

echo "🚀 Deploying Lucy THIN CLIENT to GCP"
echo "====================================="
echo "Architecture:"
echo "  - GCP Cloud Run: Stateless API proxy"
echo "  - NAS: Main storage (via VPN)"
echo "  - Supabase: HOT buffer"
echo ""

# Build thin client image
echo "📦 Building thin client image..."
docker build \
  -t "gcr.io/$PROJECT_ID/lucy-thin-client:latest" \
  -f deployment/Dockerfile.thin \
  .

# Push to GCR
echo "⬆️  Pushing to GCR..."
gcloud auth configure-docker --quiet
docker push "gcr.io/$PROJECT_ID/lucy-thin-client:latest"

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy lucy-thin-client \
  --image="gcr.io/$PROJECT_ID/lucy-thin-client:latest" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=0 \
  --set-env-vars="NAS_QDRANT_URL=http://192.168.1.129:6333" \
  --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --vpc-connector="nas-vpn-connector" \
  --project="$PROJECT_ID" \
  --quiet

# Get URL
URL=$(gcloud run services describe lucy-thin-client \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format='value(status.url)')

echo ""
echo "✅ THIN CLIENT DEPLOYED!"
echo "   URL: $URL"
echo "   Mode: Stateless proxy"
echo "   Data: NAS (192.168.1.129) + Supabase buffer"
echo ""
echo "Test: curl $URL/health"
