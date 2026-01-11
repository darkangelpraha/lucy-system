"""
Lucy Orchestrator - Main Coordinator for Premium Gastro
Routes queries to 9 domain assistants + evaluator

INTEGRATION:
- Linear: Project tracking & tasks
- Notion: Database & notes (AI built-in)
- Todoist: Daily personal agenda
- Gmail: Built-in to Notion
- Mem0 + Qdrant: Memory & knowledge

9 ASSISTANTS:
1. Communications - Emails, chats
2. Knowledge - Tech docs
3. Projects - Linear, GitHub
4. Content - N8N automation
5. Data - Qdrant, Supabase
6. Dev - VSCode, Docker
7. Business - Finance, ops
8. Personal - Calendar, reminders
9. Evaluator - Quality control
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import os
from datetime import datetime

app = FastAPI(title="Lucy Orchestrator - Premium Gastro")

# Configuration
ASSISTANTS = {
    "communications": os.getenv("LUCY_COMMUNICATIONS_URL", "http://lucy-communications:8080"),
    "knowledge": os.getenv("LUCY_KNOWLEDGE_URL", "http://lucy-knowledge:8080"),
    "projects": os.getenv("LUCY_PROJECTS_URL", "http://lucy-projects:8080"),
    "content": os.getenv("LUCY_CONTENT_URL", "http://lucy-content:8080"),
    "data": os.getenv("LUCY_DATA_URL", "http://lucy-data:8080"),
    "dev": os.getenv("LUCY_DEV_URL", "http://lucy-dev:8080"),
    "business": os.getenv("LUCY_BUSINESS_URL", "http://lucy-business:8080"),
    "personal": os.getenv("LUCY_PERSONAL_URL", "http://lucy-personal:8080"),
    "evaluator": os.getenv("LUCY_EVALUATOR_URL", "http://lucy-evaluator:8080")
}

# System Prompt - Lucy's personality & rules
LUCY_SYSTEM_PROMPT = """
Jsi Lucy - osobní asistentka pro Premium Gastro CEO.

## IDENTITA:
- Jméno: Lucy (Lucie)
- Role: Osobní AI asistentka
- Osobnost: Profesionální, efektivní, proaktivní, učí se z chyb
- Jazyk: Primárně čeština, angličtina podle potřeby

## HLAVNÍ ZODPOVĚDNOSTI:

1. **KOMUNIKACE:**
   - Správa emailů (Notion Gmail integration)
   - Filtrování priorit
   - Drafty odpovědí
   - Sledování konverzací přes platformy

2. **PROJEKTY:**
   - Linear task management (všechny větší projekty)
   - GitHub issue tracking
   - Sledování deadlinů
   - Reporty progress

3. **OSOBNÍ AGENDA:**
   - Todoist denní plánování
   - Kalendář optimalizace
   - Priority management
   - Health & wellness reminders

4. **KNOWLEDGE:**
   - Tech dokumentace (Qdrant, 22k+ pages)
   - Email historie (5,7k+ emails)
   - Beeper konverzace (TODO)
   - Notion databáze

5. **BUSINESS:**
   - Revenue tracking
   - Invoice management
   - Customer relationships
   - Partnership deals

## PRAVIDLA CHOVÁNÍ:

✅ ALWAYS:
- Odpovídej stručně a přesně
- Používej zdroje (Qdrant, Supabase, Linear)
- Zapisuj důležité info do Mem0 (long-term memory)
- Aktualizuj Linear tasks s progressem
- Kontroluj odpovědi PŘED odesláním (Evaluator)
- Uč se z chyb (Error Learning System)
- Prioritizuj podle urgency & impact

❌ NEVER:
- Vymýšlej info - jen ověřené zdroje
- Opakuj chyby (Error Learning)
- Ignoruj explicitní požadavky
- Odpovídej bez kontextu
- Kecy - jen akce

## ERROR LEARNING (CRITICAL):
Každá chyba se zaznamenává a NESMÍ se opakovat.

1. Before action → Check if similar error happened before
2. If error → Record to Supabase + Mem0
3. Weekly review → Detect patterns
4. Repeated error = CRITICAL escalation

**Example:**
Pokud jednou nepřečteš celý request a udělám špatnou akci:
→ Zaznamená se "didn't read full request"
→ Příště PŘED akcí: "Did I make this mistake before?"
→ Pokud ano: ASK for confirmation

## INTEGRATION TOOLS:

**Linear:**
- Projekty & tasks (větší práce)
- API: linear.app/api
- Update progress pravidelně

**Notion:**
- Databáze (co si vyznam)
- Gmail built-in
- AI capabilities (použij Notion AI na složité queries)
- Poznámky & dokumentace

**Todoist:**
- Denní osobní agenda
- Quick tasks
- Habits & reminders

**Qdrant (NAS):**
- Tech docs: 22,315 pages
- Emails: 5,757 emails
- Future: Beeper messages
- Via VPN connection

**Supabase:**
- HOT buffer (recent queries)
- Error learning records
- Session states

**Mem0:**
- Long-term memory
- User preferences
- Context persistence

## COLLABORATION FLOW:

User Query
    ↓
Orchestrator (tady) - rozhoduje který assistant(y)
    ↓
1-9 Assistants (domain specialists) - generují responses
    ↓
Evaluator - kontroluje kvalitu (80%+ threshold)
    ↓
IF quality OK → Return to user
IF quality LOW → Refine or escalate

## RESPONSE STYLE:

**Good:**
"Našla jsem 12 emailů o Qdrant projektu. Top 3 z poslední týdne:
1. [2024-01-08] GitHub issue #234 - Qdrant scaling
2. [2024-01-06] Email od Andreje - API limits
3. [2024-01-05] Linear task PG-123 - Migration plan"

**Bad:**
"Hledám emaily... Našla jsem nějaké... Tady jsou..."

## MULTILINGUAL:
- Czech: Hlavní jazyk (user preference)
- English: Technical docs, code, APIs
- Auto-detect z kontextu

## PROACTIVE FEATURES:

**Morning Briefing:**
- Todoist agenda na dnes
- Linear tasks due today
- Unread important emails (Notion)
- Calendar conflicts check

**Learning:**
- Sleduj patterns v dotazech
- Navrhuj optimalizace workflows
- Upozorni na recurring issues
- Track metric improvements

## VOICE MODE:
Když pracuješ přes voice interface:
- Mluvíš profesionálně ale přirozeně
- Krátké odpovědi (voice = delší než text)
- Potvrzuj akce před executionem
- Czech language natural flow

---

**Version:** 1.0 - Production Ready
**Last Updated:** 2026-01-11
**Status:** DEPLOYED TO GCP
"""

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default"
    context: Optional[Dict] = None
    language: Optional[str] = "cs"  # cs | en

class QueryResponse(BaseModel):
    response: str
    agent: str  # Which assistant(s) answered
    confidence: float
    sources: List[Dict]
    quality_score: Optional[float] = None
    evaluated: bool = False
    needs_refinement: bool = False
    suggestions: List[str] = []

@app.get("/health")
async def health():
    """Health check - verify all assistants are reachable"""
    status = {
        "orchestrator": "healthy",
        "assistants": {}
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in ASSISTANTS.items():
            try:
                resp = await client.get(f"{url}/health")
                status["assistants"][name] = "healthy" if resp.status_code == 200 else "unhealthy"
            except:
                status["assistants"][name] = "unreachable"
    
    all_healthy = all(s == "healthy" for s in status["assistants"].values())
    
    return {
        **status,
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint
    
    1. Route to appropriate assistant(s)
    2. Get response(s)
    3. Evaluate quality
    4. Return or refine
    """
    
    # 1. Route query
    agents = route_query(request.query, request.context or {})
    
    if not agents:
        raise HTTPException(status_code=400, detail="Cannot determine appropriate assistant")
    
    # 2. Query assistant(s)
    if len(agents) == 1:
        # Single agent
        response = await query_assistant(agents[0], request.query, request.context)
    else:
        # Multi-agent collaboration
        response = await query_multi_agents(agents, request.query, request.context)
    
    # 3. Evaluate quality
    evaluation = await evaluate_response(request.query, response)
    
    # 4. Return result
    return QueryResponse(
        response=response["response"],
        agent=response["agent"],
        confidence=response.get("confidence", 0.5),
        sources=response.get("sources", []),
        quality_score=evaluation["quality_score"],
        evaluated=True,
        needs_refinement=evaluation["quality_score"] < 0.8,
        suggestions=evaluation.get("suggestions", [])
    )

def route_query(query: str, context: Dict) -> List[str]:
    """Determine which assistant(s) should handle the query"""
    
    agents = []
    q_lower = query.lower()
    
    # Email/messaging keywords
    if any(kw in q_lower for kw in ["email", "mail", "zpráv", "chat", "conversation", "beeper"]):
        agents.append("communications")
    
    # Tech docs
    if any(kw in q_lower for kw in ["docs", "documentation", "how to", "tutorial", "qdrant", "supabase", "api"]):
        agents.append("knowledge")
    
    # Projects
    if any(kw in q_lower for kw in ["linear", "github", "project", "task", "issue", "pr", "deadline"]):
        agents.append("projects")
    
    # Automation
    if any(kw in q_lower for kw in ["n8n", "workflow", "automation", "trigger", "webhook"]):
        agents.append("content")
    
    # Database/data
    if any(kw in q_lower for kw in ["database", "query", "data", "collection", "vector"]):
        agents.append("data")
    
    # Development
    if any(kw in q_lower for kw in ["code", "vscode", "docker", "deploy", "build", "debug"]):
        agents.append("dev")
    
    # Business
    if any(kw in q_lower for kw in ["invoice", "revenue", "customer", "deal", "contract", "finance"]):
        agents.append("business")
    
    # Personal
    if any(kw in q_lower for kw in ["calendar", "todoist", "reminder", "schedule", "agenda", "meeting"]):
        agents.append("personal")
    
    # Default: knowledge (fallback)
    if not agents:
        agents.append("knowledge")
    
    return agents

async def query_assistant(agent_name: str, query: str, context: Optional[Dict]) -> Dict:
    """Query single assistant"""
    
    url = ASSISTANTS.get(agent_name)
    if not url:
        raise HTTPException(status_code=500, detail=f"Assistant {agent_name} not configured")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{url}/query",
                json={"query": query, "context": context or {}}
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"Assistant {agent_name} timeout")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Assistant {agent_name} error: {str(e)}")
    
    return {
        "response": data.get("response", "No response"),
        "agent": agent_name,
        "confidence": data.get("confidence", 0.5),
        "sources": data.get("sources", []),
        "reasoning": data.get("reasoning", "")
    }

async def query_multi_agents(agents: List[str], query: str, context: Optional[Dict]) -> Dict:
    """Query multiple assistants in parallel and merge results"""
    
    import asyncio
    
    # Query all agents in parallel
    tasks = [query_assistant(agent, query, context) for agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    valid_results = [r for r in results if not isinstance(r, Exception)]
    
    if not valid_results:
        raise HTTPException(status_code=500, detail="All assistants failed")
    
    # Merge responses
    merged_response = "\n\n".join([
        f"**{r['agent'].upper()}:**\n{r['response']}"
        for r in valid_results
    ])
    
    merged_sources = []
    for r in valid_results:
        merged_sources.extend(r.get("sources", []))
    
    avg_confidence = sum(r["confidence"] for r in valid_results) / len(valid_results)
    
    return {
        "response": merged_response,
        "agent": "multi-agent",
        "confidence": avg_confidence,
        "sources": merged_sources,
        "agents_used": [r["agent"] for r in valid_results]
    }

async def evaluate_response(query: str, response: Dict) -> Dict:
    """Evaluate response quality using Evaluator assistant"""
    
    evaluator_url = ASSISTANTS["evaluator"]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{evaluator_url}/evaluate",
                json={
                    "query": query,
                    "response": response["response"],
                    "agent": response["agent"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.5)
                }
            )
            resp.raise_for_status()
            return resp.json()
        except:
            # Fallback if evaluator fails
            return {
                "quality_score": 0.7,
                "issues": [],
                "suggestions": [],
                "reasoning": "Evaluator unavailable"
            }

@app.post("/briefing")
async def morning_briefing(user_id: str = "default"):
    """
    Generate morning briefing
    
    - Todoist agenda
    - Linear tasks due today
    - Unread important emails
    - Calendar conflicts
    """
    
    # Query personal assistant for briefing
    response = await query_assistant("personal", "Generate morning briefing", {"user_id": user_id})
    
    return response

@app.get("/stats")
async def stats():
    """System statistics"""
    
    # Placeholder - implement actual stats
    return {
        "orchestrator_uptime": "healthy",
        "total_queries_today": 0,  # TODO: Track in Supabase
        "active_assistants": len(ASSISTANTS),
        "avg_response_time": "2.3s"  # TODO: Calculate
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
