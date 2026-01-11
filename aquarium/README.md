# Lucy Aquarium 🐠

Real-time monitoring a ovládání AI agentů v Lucy systému.

## Co to je?

Lucy Aquarium je web rozhraní pro sledování a kontrolu všech běžících AI agentů:
- Vidíš, kdo právě pracuje
- Co agenti navrhují a říkají
- Můžeš vstoupit a upravit myšlenky agentů
- Historie všech rozhodnutí

## Jak spustit

### 1. Aktivuj virtuální prostředí

```bash
cd /Users/premiumgastro/Projects/Mem0/lucy_system
source venv/bin/activate
```

### 2. Spusť server

```bash
python aquarium/aquarium_server.py
```

Nebo:

```bash
cd aquarium
uvicorn aquarium_server:app --host 0.0.0.0 --port 8081 --reload
```

### 3. Otevři v prohlížeči

```
http://localhost:8081
```

## API Endpointy

### WebSocket: `/ws`
Real-time komunikace s Aquarium UI.

### POST: `/agent/status`
Agent reportuje svůj status:

```json
{
  "agent_id": "agent_001",
  "status": {
    "name": "Lucy Coordinator",
    "status": "working",
    "thought": "Analyzing user request...",
    "active": true
  }
}
```

## Integrace s agenty

Každý agent by měl periodicky odesílat svůj status:

```python
import httpx

async def report_status(agent_id: str, thought: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8081/agent/status",
            json={
                "agent_id": agent_id,
                "status": {
                    "name": "Agent Name",
                    "status": "working",
                    "thought": thought,
                    "active": True
                }
            }
        )
```

## Vlastnosti

- ✅ Real-time WebSocket komunikace
- ✅ Live monitoring agentů
- ✅ Editace myšlenek agentů
- ✅ Historie akcí
- ✅ Moderní dark mode UI
- ✅ Automatická reconnect

## Port

Default: `8081`

Můžeš změnit v poslední řádce `aquarium_server.py`.
