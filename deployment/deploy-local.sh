#!/bin/bash
# QUICK DEPLOY - Local Test First

echo "🚀 Lucy Local Test Deployment"
echo "=============================="

cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Copy .env.template to .env and fill in credentials"
    cp .env.template .env
    echo "✅ Created .env from template"
    echo ""
    echo "Please edit .env with credentials from 1Password AI vault:"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - SUPABASE_URL & SUPABASE_KEY"
    echo "  - QDRANT_HOST (192.168.1.129:6333)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Load environment
set -a
source .env
set +a

echo "✅ Environment loaded"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

echo "✅ Dependencies installed"
echo ""

# Test Qdrant connection
echo "🔍 Testing Qdrant connection..."
python -c "
from qdrant_client import QdrantClient
try:
    client = QdrantClient(host='${QDRANT_HOST%:*}', port=${QDRANT_HOST#*:})
    collections = client.get_collections()
    print('✅ Qdrant connected!')
    print(f'   Collections: {len(collections.collections)}')
    for col in collections.collections:
        info = client.get_collection(col.name)
        print(f'   - {col.name}: {info.points_count} points')
except Exception as e:
    print(f'❌ Qdrant connection failed: {e}')
    print('   Make sure NAS is accessible or VPN is connected')
"

echo ""

# Start orchestrator locally
echo "🎯 Starting Lucy Orchestrator (local test)..."
echo "   URL: http://localhost:8080"
echo "   Health: http://localhost:8080/health"
echo "   Docs: http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

export LUCY_MODE=orchestrator
python -m uvicorn lucy_orchestrator:app --host 0.0.0.0 --port 8080 --reload
