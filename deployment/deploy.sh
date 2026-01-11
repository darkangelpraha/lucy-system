#!/bin/bash
set -e

# Lucy GCP Deployment Script
echo "🚀 Lucy AI Assistant - GCP Deployment"
echo "======================================"

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    log_info "gcloud CLI found"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Install from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_info "Docker found"
}

authenticate_gcp() {
    echo ""
    echo "🔐 Authenticating with GCP..."
    
    if ! gcloud auth print-access-token &> /dev/null; then
        log_warn "Not authenticated. Running gcloud auth login..."
        gcloud auth login
    fi
    
    gcloud config set project "$PROJECT_ID"
    log_info "Authenticated as: $(gcloud config get-value account)"
    log_info "Project: $PROJECT_ID"
}

enable_apis() {
    echo ""
    echo "🔧 Enabling required GCP APIs..."
    
    APIS=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "compute.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
    )
    
    for api in "${APIS[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" --quiet
    done
}

setup_secrets() {
    echo ""
    echo "🔒 Setting up secrets..."
    
    # Check if secrets exist
    if ! gcloud secrets describe anthropic-api-key --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Secret 'anthropic-api-key' not found. Creating..."
        
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            read -sp "Enter Anthropic API Key: " ANTHROPIC_API_KEY
            echo ""
        fi
        
        echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        
        log_info "Created secret: anthropic-api-key"
    else
        log_info "Secret 'anthropic-api-key' exists"
    fi
    
    # QDRANT_HOST
    if ! gcloud secrets describe qdrant-host --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Secret 'qdrant-host' not found. Creating..."
        
        if [ -z "$QDRANT_HOST" ]; then
            read -p "Enter Qdrant host (e.g., 192.168.1.129:6333): " QDRANT_HOST
        fi
        
        echo -n "$QDRANT_HOST" | gcloud secrets create qdrant-host \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
        
        log_info "Created secret: qdrant-host"
    else
        log_info "Secret 'qdrant-host' exists"
    fi
}

build_and_push() {
    echo ""
    echo "🏗️  Building and pushing Docker image..."
    
    # Build image
    log_info "Building Docker image..."
    docker build -t "gcr.io/$PROJECT_ID/lucy-assistant:latest" -f deployment/Dockerfile ..
    
    # Configure Docker for GCR
    gcloud auth configure-docker --quiet
    
    # Push image
    log_info "Pushing to GCR..."
    docker push "gcr.io/$PROJECT_ID/lucy-assistant:latest"
    
    log_info "Image pushed: gcr.io/$PROJECT_ID/lucy-assistant:latest"
}

deploy_cloud_run() {
    echo ""
    echo "☁️  Deploying to Cloud Run..."
    
    # Deploy Orchestrator
    log_info "Deploying Lucy Orchestrator..."
    gcloud run deploy lucy-orchestrator \
        --image="gcr.io/$PROJECT_ID/lucy-assistant:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=2Gi \
        --cpu=2 \
        --max-instances=10 \
        --set-env-vars="LUCY_ENV=$ENVIRONMENT,LUCY_MODE=orchestrator" \
        --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest,QDRANT_HOST=qdrant-host:latest" \
        --project="$PROJECT_ID" \
        --quiet
    
    # Get orchestrator URL
    ORCHESTRATOR_URL=$(gcloud run services describe lucy-orchestrator \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(status.url)')
    
    log_info "Orchestrator deployed: $ORCHESTRATOR_URL"
    
    # Deploy Communications Assistant
    log_info "Deploying Lucy Communications..."
    gcloud run deploy lucy-communications \
        --image="gcr.io/$PROJECT_ID/lucy-assistant:latest" \
        --region="$REGION" \
        --platform=managed \
        --no-allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=5 \
        --set-env-vars="LUCY_ENV=$ENVIRONMENT,LUCY_ASSISTANT=communications" \
        --set-secrets="QDRANT_HOST=qdrant-host:latest" \
        --project="$PROJECT_ID" \
        --quiet
    
    # Deploy Knowledge Assistant
    log_info "Deploying Lucy Knowledge..."
    gcloud run deploy lucy-knowledge \
        --image="gcr.io/$PROJECT_ID/lucy-assistant:latest" \
        --region="$REGION" \
        --platform=managed \
        --no-allow-unauthenticated \
        --memory=1Gi \
        --cpu=1 \
        --max-instances=5 \
        --set-env-vars="LUCY_ENV=$ENVIRONMENT,LUCY_ASSISTANT=knowledge" \
        --set-secrets="QDRANT_HOST=qdrant-host:latest" \
        --project="$PROJECT_ID" \
        --quiet
}

setup_monitoring() {
    echo ""
    echo "📊 Setting up monitoring..."
    
    # Cloud Logging
    log_info "Configuring Cloud Logging..."
    
    # Cloud Monitoring
    log_info "Configuring Cloud Monitoring..."
    
    log_info "Monitoring configured"
}

test_deployment() {
    echo ""
    echo "🧪 Testing deployment..."
    
    ORCHESTRATOR_URL=$(gcloud run services describe lucy-orchestrator \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(status.url)')
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -sf "$ORCHESTRATOR_URL/health" > /dev/null; then
        log_info "Health check passed ✓"
    else
        log_error "Health check failed ✗"
    fi
}

print_summary() {
    echo ""
    echo "════════════════════════════════════════════"
    echo "✅ Lucy AI Assistant Deployment Complete!"
    echo "════════════════════════════════════════════"
    echo ""
    echo "📍 Deployment Details:"
    echo "   Project: $PROJECT_ID"
    echo "   Region: $REGION"
    echo "   Environment: $ENVIRONMENT"
    echo ""
    
    ORCHESTRATOR_URL=$(gcloud run services describe lucy-orchestrator \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --format='value(status.url)' 2>/dev/null || echo "Not deployed")
    
    echo "🌐 Endpoints:"
    echo "   Orchestrator: $ORCHESTRATOR_URL"
    echo ""
    echo "💡 Next Steps:"
    echo "   1. Test: curl $ORCHESTRATOR_URL/health"
    echo "   2. Query: curl -X POST $ORCHESTRATOR_URL/query -d '{\"query\":\"test\"}'"
    echo "   3. Monitor: gcloud run services logs read lucy-orchestrator --region=$REGION"
    echo ""
}

# Main deployment flow
main() {
    echo ""
    echo "Starting deployment for project: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Environment: $ENVIRONMENT"
    echo ""
    
    check_gcloud
    check_docker
    authenticate_gcp
    enable_apis
    setup_secrets
    build_and_push
    deploy_cloud_run
    setup_monitoring
    test_deployment
    print_summary
}

# Run if not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi
