"""
Lucy Agent Collaboration Architecture

9 Agents spolupracují přes orchestrator s evaluation loop:

FLOW:
1. User query → Orchestrator
2. Orchestrator routes to primary agent(s)
3. Agent(s) generate response
4. **EVALUATOR checks quality** ← NOVÝ KROK
5. If quality OK → return to user
6. If quality LOW → request refinement or escalate to human

Agents:
1. Lucy-Communications - Emails, chats, messages
2. Lucy-Knowledge - Tech docs, documentation
3. Lucy-Projects - Linear, GitHub, project management
4. Lucy-Content - N8N workflows, automation
5. Lucy-Data - Qdrant, Supabase, databases
6. Lucy-Dev - VSCode, Docker, development
7. Lucy-Business - Business ops, invoices, finance
8. Lucy-Personal - Personal assistant tasks
9. **Lucy-Evaluator - Quality control** ← NEW
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentDomain(Enum):
    COMMUNICATIONS = "communications"
    KNOWLEDGE = "knowledge"
    PROJECTS = "projects"
    CONTENT = "content"
    DATA = "data"
    DEV = "dev"
    BUSINESS = "business"
    PERSONAL = "personal"
    EVALUATOR = "evaluator"

@dataclass
class AgentResponse:
    agent: str
    response: str
    confidence: float  # 0.0 - 1.0
    sources: List[Dict]
    reasoning: str
    metadata: Dict

@dataclass
class EvaluationResult:
    quality_score: float  # 0.0 - 1.0
    passed: bool
    issues: List[str]
    suggestions: List[str]
    evaluator_reasoning: str

class AgentCollaborationProtocol:
    """
    Jak agenti spolupracují - PRECIZNĚ
    """
    
    @staticmethod
    def route_query(query: str, context: Dict) -> List[AgentDomain]:
        """
        Routing logic - který agent(i) by měli odpovídat
        
        Může být více agentů najednou pro komplexní query:
        - "Show me emails about Qdrant docs" → Communications + Knowledge
        - "Create N8N workflow for Linear updates" → Content + Projects
        """
        
        agents = []
        query_lower = query.lower()
        
        # Email/messaging keywords
        if any(kw in query_lower for kw in ["email", "message", "chat", "conversation"]):
            agents.append(AgentDomain.COMMUNICATIONS)
        
        # Tech docs keywords
        if any(kw in query_lower for kw in ["docs", "documentation", "how to", "api", "tutorial"]):
            agents.append(AgentDomain.KNOWLEDGE)
        
        # Project management
        if any(kw in query_lower for kw in ["linear", "github", "project", "issue", "pr", "pull request"]):
            agents.append(AgentDomain.PROJECTS)
        
        # Automation
        if any(kw in query_lower for kw in ["n8n", "workflow", "automation", "trigger"]):
            agents.append(AgentDomain.CONTENT)
        
        # Database/data
        if any(kw in query_lower for kw in ["qdrant", "supabase", "database", "query", "data"]):
            agents.append(AgentDomain.DATA)
        
        # Development
        if any(kw in query_lower for kw in ["code", "vscode", "docker", "deploy", "build"]):
            agents.append(AgentDomain.DEV)
        
        # Business
        if any(kw in query_lower for kw in ["invoice", "revenue", "finance", "business"]):
            agents.append(AgentDomain.BUSINESS)
        
        # Personal
        if any(kw in query_lower for kw in ["schedule", "reminder", "personal", "todo"]):
            agents.append(AgentDomain.PERSONAL)
        
        # Default: Knowledge (fallback)
        if not agents:
            agents.append(AgentDomain.KNOWLEDGE)
        
        return agents
    
    @staticmethod
    async def evaluate_response(
        query: str,
        response: AgentResponse,
        evaluator_url: str
    ) -> EvaluationResult:
        """
        Evaluator checks response quality BEFORE returning to user
        
        Checks:
        1. Relevance - Does response answer the query?
        2. Completeness - Is all requested info included?
        3. Accuracy - Are sources valid and recent?
        4. Clarity - Is response clear and well-structured?
        5. Safety - No harmful/inappropriate content?
        
        Returns:
            EvaluationResult with quality score and pass/fail
        """
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            eval_response = await client.post(
                f"{evaluator_url}/evaluate",
                json={
                    "query": query,
                    "response": response.response,
                    "agent": response.agent,
                    "sources": response.sources,
                    "confidence": response.confidence
                },
                timeout=30.0
            )
            
            result = eval_response.json()
        
        return EvaluationResult(
            quality_score=result["quality_score"],
            passed=result["quality_score"] >= 0.8,  # Threshold: 80%
            issues=result.get("issues", []),
            suggestions=result.get("suggestions", []),
            evaluator_reasoning=result.get("reasoning", "")
        )
    
    @staticmethod
    async def orchestrate_multi_agent(
        query: str,
        agents: List[AgentDomain],
        agent_urls: Dict[str, str]
    ) -> AgentResponse:
        """
        Orchestrate multiple agents for complex query
        
        Example:
        Query: "Show me emails about Qdrant and relevant docs"
        Agents: [Communications, Knowledge]
        
        Flow:
        1. Query Communications for emails
        2. Query Knowledge for docs
        3. Merge results
        4. Return combined response
        """
        
        import httpx
        import asyncio
        
        async def query_agent(agent: AgentDomain) -> AgentResponse:
            url = agent_urls.get(agent.value)
            if not url:
                return None
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{url}/query",
                    json={"query": query},
                    timeout=60.0
                )
                data = response.json()
            
            return AgentResponse(
                agent=agent.value,
                response=data["response"],
                confidence=data.get("confidence", 0.5),
                sources=data.get("sources", []),
                reasoning=data.get("reasoning", ""),
                metadata=data.get("metadata", {})
            )
        
        # Query all agents in parallel
        tasks = [query_agent(agent) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        # Filter None results
        results = [r for r in results if r is not None]
        
        if not results:
            return None
        
        # If single agent, return directly
        if len(results) == 1:
            return results[0]
        
        # Merge multiple agent responses
        merged_response = "\n\n".join([
            f"**{r.agent.upper()}:**\n{r.response}"
            for r in results
        ])
        
        merged_sources = []
        for r in results:
            merged_sources.extend(r.sources)
        
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        return AgentResponse(
            agent="multi-agent",
            response=merged_response,
            confidence=avg_confidence,
            sources=merged_sources,
            reasoning=f"Combined response from {len(results)} agents",
            metadata={"agents_used": [r.agent for r in results]}
        )

# Example usage in orchestrator
async def handle_query_with_evaluation(
    query: str,
    agent_urls: Dict[str, str],
    evaluator_url: str
) -> Dict:
    """
    Full flow with evaluation
    
    1. Route to agent(s)
    2. Get response(s)
    3. **Evaluate quality**
    4. If pass → return
    5. If fail → refine or escalate
    """
    
    protocol = AgentCollaborationProtocol()
    
    # 1. Route
    agents = protocol.route_query(query, {})
    
    # 2. Get responses
    response = await protocol.orchestrate_multi_agent(query, agents, agent_urls)
    
    if not response:
        return {"error": "No agent available"}
    
    # 3. EVALUATE
    evaluation = await protocol.evaluate_response(query, response, evaluator_url)
    
    # 4. Check quality
    if evaluation.passed:
        # Quality OK - return to user
        return {
            "response": response.response,
            "agent": response.agent,
            "sources": response.sources,
            "confidence": response.confidence,
            "quality_score": evaluation.quality_score,
            "evaluated": True
        }
    else:
        # Quality LOW - need refinement
        return {
            "response": response.response,
            "agent": response.agent,
            "sources": response.sources,
            "quality_score": evaluation.quality_score,
            "issues": evaluation.issues,
            "suggestions": evaluation.suggestions,
            "needs_refinement": True,
            "evaluated": True
        }
