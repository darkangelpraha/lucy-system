"""
GCP Thin Client - Kostra která sahá na NAS + Supabase

Architecture:
- GCP Cloud Run: Stateless thin client (just API endpoint)
- NAS (192.168.1.129): Main infinite memory (Qdrant cold storage)
- Supabase: HOT buffer (operational memory)
- VPN: Secure connection GCP <-> NAS

Výhody:
- Když vypadne proud v kanclu, GCP běží dál
- Těžké operace na NAS, GCP jen přeposílá
- Workstation nezaseknutá
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Dict, List, Optional
import asyncio

app = FastAPI(title="Lucy Thin Client")

# Configuration
NAS_QDRANT_URL = os.getenv("NAS_QDRANT_URL", "http://192.168.1.129:6333")  # Přes VPN
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default"
    context: Optional[Dict] = None

class QueryResponse(BaseModel):
    response: str
    sources: List[Dict]
    agent: str
    timestamp: str

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "mode": "thin_client",
        "nas_connection": await check_nas_connection(),
        "supabase_connection": await check_supabase_connection()
    }

async def check_nas_connection() -> bool:
    """Check if NAS is reachable via VPN"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{NAS_QDRANT_URL}/collections", timeout=5.0)
            return response.status_code == 200
    except:
        return False

async def check_supabase_connection() -> bool:
    """Check Supabase connection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/",
                headers={"apikey": SUPABASE_KEY},
                timeout=5.0
            )
            return response.status_code in [200, 404]  # 404 is ok (no endpoint)
    except:
        return False

@app.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint - THIN CLIENT
    
    Workflow:
    1. Check HOT buffer (Supabase) for recent similar queries
    2. If found, return from buffer (fast)
    3. If not found, forward to NAS for processing (slow but thorough)
    4. Cache result in Supabase buffer
    """
    
    # 1. Check HOT buffer first
    cached = await check_hot_buffer(request.query, request.user_id)
    if cached:
        return QueryResponse(**cached)
    
    # 2. Forward to NAS (heavy lifting)
    result = await query_nas(request.query, request.user_id, request.context)
    
    # 3. Cache in HOT buffer
    await cache_to_hot_buffer(request.query, request.user_id, result)
    
    return QueryResponse(**result)

async def check_hot_buffer(query: str, user_id: str) -> Optional[Dict]:
    """Check Supabase for recent cached results"""
    
    # Implementation depends on Supabase schema
    # For now, return None (always miss)
    return None

async def query_nas(query: str, user_id: str, context: Optional[Dict]) -> Dict:
    """
    Forward query to NAS for processing
    
    NAS does:
    - Query Qdrant collections (email, docs, etc.)
    - Run heavy AI processing
    - Return results
    
    GCP just proxies the request
    """
    
    # This would call actual Lucy orchestrator on NAS
    # For now, placeholder
    
    return {
        "response": f"Query '{query}' processed on NAS",
        "sources": [],
        "agent": "lucy-orchestrator",
        "timestamp": "2026-01-11T00:00:00Z"
    }

async def cache_to_hot_buffer(query: str, user_id: str, result: Dict):
    """Cache result in Supabase HOT buffer"""
    
    # Save to Supabase for fast retrieval
    # TTL: 1 hour (configurable)
    pass

@app.get("/stats")
async def stats():
    """System stats"""
    
    return {
        "nas": {
            "status": "connected" if await check_nas_connection() else "disconnected",
            "url": NAS_QDRANT_URL
        },
        "supabase": {
            "status": "connected" if await check_supabase_connection() else "disconnected",
            "url": SUPABASE_URL
        },
        "mode": "thin_client",
        "description": "Stateless proxy to NAS + Supabase buffer"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
