#!/bin/bash
# Lucy System Startup Script
# Kontroluje porty před spuštěním a startuje všechny služby

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PYTHON_BIN="$SCRIPT_DIR/venv/bin/python"
ORCHESTRATOR_PORT=8080
AQUARIUM_PORT=8081

echo "🚀 Starting Lucy System..."
echo "================================"

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    
    if lsof -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
        echo "❌ Port $port already in use by:"
        lsof -iTCP:$port -sTCP:LISTEN | tail -n +2
        echo ""
        echo "🛑 Cannot start $service - port $port is occupied"
        echo "   Run: ./stop-lucy.sh to stop all Lucy services"
        echo "   Or:  lsof -ti:$port | xargs kill -9"
        return 1
    fi
    return 0
}

# Check if Python venv exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check ports BEFORE starting anything
echo "🔍 Checking ports..."
check_port $ORCHESTRATOR_PORT "Orchestrator" || exit 1
check_port $AQUARIUM_PORT "Aquarium" || exit 1
echo "✅ Ports are free"
echo ""

# Start Orchestrator
echo "🎯 Starting Lucy Orchestrator (port $ORCHESTRATOR_PORT)..."
nohup $PYTHON_BIN launcher.py > lucy.log 2>&1 &
ORCHESTRATOR_PID=$!
echo "   PID: $ORCHESTRATOR_PID"

# Wait for orchestrator to start
sleep 3

# Check if orchestrator started successfully
if ! lsof -iTCP:$ORCHESTRATOR_PORT -sTCP:LISTEN >/dev/null 2>&1; then
    echo "❌ Orchestrator failed to start. Check lucy.log"
    tail -20 lucy.log
    exit 1
fi

# Start Aquarium
echo "🐠 Starting Lucy Aquarium (port $AQUARIUM_PORT)..."
nohup $PYTHON_BIN aquarium/aquarium_server.py > aquarium.log 2>&1 &
AQUARIUM_PID=$!
echo "   PID: $AQUARIUM_PID"

# Wait for aquarium to start
sleep 3

# Check if aquarium started successfully
if ! lsof -iTCP:$AQUARIUM_PORT -sTCP:LISTEN >/dev/null 2>&1; then
    echo "❌ Aquarium failed to start. Check aquarium.log"
    tail -20 aquarium.log
    exit 1
fi

echo ""
echo "✅ Lucy System Started Successfully!"
echo "================================"
echo ""
echo "📊 Services:"
echo "   🎯 Orchestrator: http://localhost:$ORCHESTRATOR_PORT"
echo "   🐠 Aquarium:     http://localhost:$AQUARIUM_PORT"
echo "   💬 Chat:         file://$SCRIPT_DIR/chat.html"
echo ""
echo "🔍 Check status: ./status-lucy.sh"
echo "🛑 Stop services: ./stop-lucy.sh"
echo "📝 Logs:"
echo "   tail -f lucy.log"
echo "   tail -f aquarium.log"
echo ""
