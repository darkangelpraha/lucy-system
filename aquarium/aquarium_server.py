"""
Lucy Aquarium - Sledování agentů v real-time

Vidíš:
- Který agent právě pracuje
- Co navrhuje / říká
- Můžeš vstoupit a upravit myšlenky
- Historie rozhodnutí
"""

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import Dict, List
import json
from datetime import datetime
import asyncio

app = FastAPI(title="Lucy Aquarium")

# Active agents state
active_agents: Dict[str, Dict] = {}
agent_history: List[Dict] = []

@app.get("/")
async def aquarium_ui():
    """Aquarium UI - sledování agentů"""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Lucy Aquarium 🐠</title>
    <style>
        body {
            font-family: 'Monaco', 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff88;
            margin: 0;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid #00ff88;
        }
        .agents-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .agent-card {
            background: #1a1f3a;
            border: 2px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            position: relative;
        }
        .agent-card.active {
            border-color: #ff00ff;
            box-shadow: 0 0 20px rgba(255,0,255,0.5);
        }
        .agent-name {
            font-size: 20px;
            font-weight: bold;
            color: #ff00ff;
            margin-bottom: 10px;
        }
        .agent-status {
            color: #00ffff;
            font-size: 12px;
            margin-bottom: 10px;
        }
        .thought-bubble {
            background: #0f1729;
            border-left: 3px solid #00ff88;
            padding: 10px;
            margin: 10px 0;
            font-size: 14px;
            max-height: 200px;
            overflow-y: auto;
        }
        .actions {
            margin-top: 10px;
        }
        button {
            background: #00ff88;
            color: #0a0e27;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            font-weight: bold;
        }
        button:hover {
            background: #ff00ff;
            color: #fff;
        }
        .history {
            margin-top: 30px;
            padding: 20px;
            background: #1a1f3a;
            border-radius: 10px;
        }
        .history-item {
            padding: 10px;
            margin: 5px 0;
            background: #0f1729;
            border-left: 3px solid #00ffff;
        }
        .edit-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1f3a;
            border: 2px solid #ff00ff;
            padding: 30px;
            border-radius: 10px;
            z-index: 1000;
            min-width: 500px;
        }
        .edit-modal.show {
            display: block;
        }
        textarea {
            width: 100%;
            height: 200px;
            background: #0f1729;
            color: #00ff88;
            border: 1px solid #00ff88;
            padding: 10px;
            font-family: 'Monaco', monospace;
            font-size: 14px;
        }
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 999;
        }
        .overlay.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐠 Lucy Aquarium 🐠</h1>
        <p>Real-time agent monitoring & intervention</p>
    </div>
    
    <div class="agents-container" id="agents">
        <!-- Agents filled by WebSocket -->
    </div>
    
    <div class="history">
        <h2>📜 History</h2>
        <div id="history">
            <!-- History filled by WebSocket -->
        </div>
    </div>
    
    <!-- Edit Modal -->
    <div class="overlay" id="overlay"></div>
    <div class="edit-modal" id="editModal">
        <h3>Edit Agent Thought</h3>
        <textarea id="thoughtEditor"></textarea>
        <div style="margin-top: 20px;">
            <button onclick="saveThought()">💾 Save</button>
            <button onclick="closeModal()">❌ Cancel</button>
        </div>
    </div>
    
    <script>
        let ws;
        let currentAgent = null;
        
        function connect() {
            ws = new WebSocket('ws://' + window.location.host + '/ws');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'agent_update') {
                    updateAgent(data.agent);
                } else if (data.type === 'history_update') {
                    addHistory(data.item);
                }
            };
            
            ws.onclose = function() {
                setTimeout(connect, 1000);
            };
        }
        
        function updateAgent(agent) {
            const container = document.getElementById('agents');
            let card = document.getElementById('agent-' + agent.id);
            
            if (!card) {
                card = document.createElement('div');
                card.id = 'agent-' + agent.id;
                card.className = 'agent-card';
                container.appendChild(card);
            }
            
            card.className = 'agent-card' + (agent.active ? ' active' : '');
            card.innerHTML = `
                <div class="agent-name">${agent.name}</div>
                <div class="agent-status">Status: ${agent.status}</div>
                <div class="thought-bubble">
                    <strong>Current Thought:</strong><br>
                    ${agent.current_thought || 'Idle...'}
                </div>
                <div class="actions">
                    <button onclick="editThought('${agent.id}', '${agent.name}')">✏️ Edit</button>
                    <button onclick="viewDetails('${agent.id}')">👁️ Details</button>
                </div>
            `;
        }
        
        function addHistory(item) {
            const container = document.getElementById('history');
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <strong>[${item.timestamp}] ${item.agent}:</strong> ${item.action}
            `;
            container.insertBefore(div, container.firstChild);
            
            // Keep only last 20
            while (container.children.length > 20) {
                container.removeChild(container.lastChild);
            }
        }
        
        function editThought(agentId, agentName) {
            currentAgent = agentId;
            const modal = document.getElementById('editModal');
            const overlay = document.getElementById('overlay');
            const editor = document.getElementById('thoughtEditor');
            
            // Get current thought
            const card = document.getElementById('agent-' + agentId);
            const thought = card.querySelector('.thought-bubble').textContent.split('Current Thought:')[1].trim();
            
            editor.value = thought;
            modal.querySelector('h3').textContent = 'Edit ' + agentName + ' Thought';
            
            modal.classList.add('show');
            overlay.classList.add('show');
        }
        
        function closeModal() {
            document.getElementById('editModal').classList.remove('show');
            document.getElementById('overlay').classList.remove('show');
        }
        
        function saveThought() {
            const thought = document.getElementById('thoughtEditor').value;
            
            ws.send(JSON.stringify({
                type: 'edit_thought',
                agent_id: currentAgent,
                new_thought: thought
            }));
            
            closeModal();
        }
        
        function viewDetails(agentId) {
            alert('Details for agent: ' + agentId);
        }
        
        // Connect on load
        connect();
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time agent updates"""
    await websocket.accept()
    
    try:
        while True:
            # Simulate agent updates (replace with actual agent monitoring)
            for agent_id, agent_data in active_agents.items():
                await websocket.send_json({
                    "type": "agent_update",
                    "agent": agent_data
                })
            
            # Wait for client messages
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)
                
                if data['type'] == 'edit_thought':
                    # User edited agent thought
                    agent_id = data['agent_id']
                    new_thought = data['new_thought']
                    
                    # Update agent thought
                    if agent_id in active_agents:
                        active_agents[agent_id]['current_thought'] = new_thought
                        active_agents[agent_id]['thought_edited'] = True
                    
                    # Add to history
                    await websocket.send_json({
                        "type": "history_update",
                        "item": {
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "agent": active_agents[agent_id]['name'],
                            "action": f"Thought edited: {new_thought[:50]}..."
                        }
                    })
            
            except asyncio.TimeoutError:
                pass
            
            await asyncio.sleep(0.5)
    
    except Exception as e:
        print(f"WebSocket error: {e}")

# API for agents to report their status
@app.post("/agent/status")
async def agent_status(agent_id: str, status: Dict):
    """Agent reports its current status"""
    
    active_agents[agent_id] = {
        "id": agent_id,
        "name": status.get("name", agent_id),
        "status": status.get("status", "idle"),
        "current_thought": status.get("thought", ""),
        "active": status.get("active", False),
        "thought_edited": False
    }
    
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
