#!/bin/bash
# Lucy System Status Check
# Zobrazuje stav všech Lucy služeb

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📊 Lucy System Status"
echo "================================"
echo ""

# Check ports
echo "🔌 Ports:"
for port in 8080 8081; do
    if lsof -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
        PID=$(lsof -ti:$port)
        CMD=$(ps -p $PID -o command= 2>/dev/null || echo "unknown")
        case $port in
            8080) SERVICE="Orchestrator" ;;
            8081) SERVICE="Aquarium" ;;
        esac
        echo "   ✅ $SERVICE (port $port, PID $PID)"
        echo "      $CMD"
    else
        case $port in
            8080) SERVICE="Orchestrator" ;;
            8081) SERVICE="Aquarium" ;;
        esac
        echo "   ❌ $SERVICE (port $port) - NOT RUNNING"
    fi
done

echo ""

# Check processes
echo "🔍 Processes:"
if ps aux | grep -E "(launcher|aquarium)" | grep -v grep | grep -v status-lucy >/dev/null 2>&1; then
    ps aux | grep -E "(launcher|aquarium)" | grep -v grep | grep -v status-lucy | awk '{printf "   PID %s: %s\n", $2, $11}'
else
    echo "   No Lucy processes running"
fi

echo ""

# Test orchestrator health
if command -v curl >/dev/null 2>&1; then
    echo "🏥 Health Checks:"
    
    # Orchestrator
    if lsof -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
        if curl -s http://localhost:8080/health >/dev/null 2>&1; then
            STATUS=$(curl -s http://localhost:8080/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            echo "   🎯 Orchestrator: $STATUS"
        else
            echo "   🎯 Orchestrator: NOT RESPONDING"
        fi
    fi
    
    # Aquarium
    if lsof -iTCP:8081 -sTCP:LISTEN >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081 2>/dev/null)
        if [ "$HTTP_CODE" = "200" ]; then
            echo "   🐠 Aquarium: OK (HTTP $HTTP_CODE)"
        else
            echo "   🐠 Aquarium: ERROR (HTTP $HTTP_CODE)"
        fi
    fi
fi

echo ""

# Show recent logs
echo "📝 Recent Logs:"
if [ -f "$SCRIPT_DIR/lucy.log" ]; then
    echo "   Orchestrator (last 3 lines):"
    tail -3 "$SCRIPT_DIR/lucy.log" | sed 's/^/      /'
fi

if [ -f "$SCRIPT_DIR/aquarium.log" ]; then
    echo ""
    echo "   Aquarium (last 3 lines):"
    tail -3 "$SCRIPT_DIR/aquarium.log" | sed 's/^/      /'
fi

echo ""
echo "================================"
echo "🔧 Commands:"
echo "   Start:  ./start-lucy.sh"
echo "   Stop:   ./stop-lucy.sh"
echo "   Logs:   tail -f lucy.log aquarium.log"
echo ""
