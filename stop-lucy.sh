#!/bin/bash
# Lucy System Stop Script
# Bezpečně zastavuje všechny Lucy služby

set -e

echo "🛑 Stopping Lucy System..."
echo "================================"

# Function to kill process on port
kill_port() {
    local port=$1
    local service=$2
    
    if lsof -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
        echo "🔪 Stopping $service (port $port)..."
        PID=$(lsof -ti:$port)
        kill -15 $PID 2>/dev/null || kill -9 $PID 2>/dev/null
        sleep 1
        
        if lsof -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
            echo "⚠️  Process still running, force killing..."
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
        echo "✅ $service stopped"
    else
        echo "ℹ️  $service not running (port $port)"
    fi
}

# Stop all Lucy processes
kill_port 8080 "Orchestrator"
kill_port 8081 "Aquarium"

# Kill any remaining launcher or aquarium processes
echo ""
echo "🧹 Cleaning up remaining processes..."
pkill -f "launcher.py" 2>/dev/null || true
pkill -f "aquarium_server.py" 2>/dev/null || true

sleep 1

# Verify everything is stopped
if ps aux | grep -E "(launcher|aquarium)" | grep -v grep | grep -v stop-lucy >/dev/null 2>&1; then
    echo "⚠️  Some processes still running:"
    ps aux | grep -E "(launcher|aquarium)" | grep -v grep | grep -v stop-lucy
else
    echo "✅ All Lucy processes stopped"
fi

echo ""
echo "✅ Lucy System Stopped"
echo ""
