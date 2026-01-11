"""
Lucy Orchestrator - Coordinates all Lucy assistants
Routes queries, manages cross-domain tasks, aggregates results
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Import Lucy components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from lucy_config import (
    LucyDomain,
    LUCY_ASSISTANTS,
    ROUTING_RULES,
    MULTI_DOMAIN_PATTERNS
)
from knowledge.kb_manager import KnowledgeBaseManager, SearchResult
from memory_manager import MemoryManager, LearningSystem

@dataclass
class RoutingDecision:
    """Decision on how to route a query"""
    primary_domain: LucyDomain
    secondary_domains: List[LucyDomain]
    strategy: str  # 'single', 'sequential', 'parallel'
    confidence: float
    reasoning: str


class LucyOrchestrator:
    """
    Main orchestrator for Lucy multi-assistant system
    Routes queries, coordinates assistants, manages workflows
    """
    
    def __init__(self):
        self.kb = KnowledgeBaseManager()
        self.memory = MemoryManager(storage_dir="./lucy_memories")
        self.learning = LearningSystem(self.memory)
        
        # Initialize all assistant namespaces
        for domain in LucyDomain:
            config = LUCY_ASSISTANTS[domain]
            self.memory.create_namespace(
                namespace=config.mem0_namespace,
                description=config.description
            )
        
        print("✅ Lucy Orchestrator initialized")
        print(f"   Assistants: {len(LUCY_ASSISTANTS)}")
        print(f"   Memory namespaces: {len(self.memory.namespaces)}")
    
    def analyze_query(self, query: str) -> RoutingDecision:
        """
        Analyze query and determine routing strategy
        """
        
        query_lower = query.lower()
        
        # Check for multi-domain patterns first
        for pattern_config in MULTI_DOMAIN_PATTERNS:
            if re.search(pattern_config['pattern'], query_lower):
                return RoutingDecision(
                    primary_domain=pattern_config['domains'][0],
                    secondary_domains=pattern_config['domains'][1:],
                    strategy=pattern_config['strategy'],
                    confidence=0.9,
                    reasoning=f"Matched multi-domain pattern: {pattern_config['pattern']}"
                )
        
        # Single domain routing
        matched_domains = []
        for keyword, domains in ROUTING_RULES.items():
            if keyword in query_lower:
                matched_domains.extend(domains)
        
        if matched_domains:
            # Most common domain wins
            from collections import Counter
            domain_counts = Counter(matched_domains)
            primary_domain = domain_counts.most_common(1)[0][0]
            
            return RoutingDecision(
                primary_domain=primary_domain,
                secondary_domains=[],
                strategy='single',
                confidence=0.8,
                reasoning=f"Matched keywords: {[k for k, d in ROUTING_RULES.items() if k in query_lower]}"
            )
        
        # Default to orchestrator for complex/unclear queries
        return RoutingDecision(
            primary_domain=LucyDomain.ORCHESTRATOR,
            secondary_domains=[],
            strategy='single',
            confidence=0.5,
            reasoning="No clear domain match - using orchestrator"
        )
    
    def route_query(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate assistant(s) and get response
        """
        
        # Analyze query
        routing = self.analyze_query(query)
        
        print(f"\n🎯 Routing Decision:")
        print(f"   Primary: {routing.primary_domain.value}")
        print(f"   Secondary: {[d.value for d in routing.secondary_domains]}")
        print(f"   Strategy: {routing.strategy}")
        print(f"   Confidence: {routing.confidence:.2f}")
        print(f"   Reasoning: {routing.reasoning}")
        
        # Execute based on strategy
        if routing.strategy == 'single':
            return self._execute_single_domain(routing.primary_domain, query, context)
        
        elif routing.strategy == 'sequential':
            return self._execute_sequential(
                routing.primary_domain,
                routing.secondary_domains,
                query,
                context
            )
        
        elif routing.strategy == 'parallel':
            return self._execute_parallel(
                routing.primary_domain,
                routing.secondary_domains,
                query,
                context
            )
        
        return {"error": "Unknown routing strategy"}
    
    def _execute_single_domain(
        self,
        domain: LucyDomain,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute query in single domain"""
        
        config = LUCY_ASSISTANTS[domain]
        
        print(f"\n🔍 Executing in {config.name}...")
        
        # Get relevant memories
        memories = self.memory.search_memories(
            namespace=config.mem0_namespace,
            query=query,
            limit=5
        )
        
        # Search knowledge base
        kb_results = self._search_knowledge_base(domain, query)
        
        # Build response
        response = {
            "domain": domain.value,
            "assistant": config.name,
            "query": query,
            "memories": [m.to_dict() for m in memories],
            "knowledge_base_results": kb_results,
            "metadata": {
                "collections_searched": config.qdrant_collections,
                "memory_namespace": config.mem0_namespace
            }
        }
        
        return response
    
    def _execute_sequential(
        self,
        primary: LucyDomain,
        secondary: List[LucyDomain],
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute query sequentially across domains"""
        
        results = []
        
        # Execute primary first
        primary_result = self._execute_single_domain(primary, query, context)
        results.append(primary_result)
        
        # Execute secondary with primary context
        enriched_context = {
            **(context or {}),
            "primary_result": primary_result
        }
        
        for domain in secondary:
            result = self._execute_single_domain(domain, query, enriched_context)
            results.append(result)
        
        return {
            "strategy": "sequential",
            "domains": [primary.value] + [d.value for d in secondary],
            "results": results,
            "aggregated": self._aggregate_results(results)
        }
    
    def _execute_parallel(
        self,
        primary: LucyDomain,
        secondary: List[LucyDomain],
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute query in parallel across domains"""
        
        all_domains = [primary] + secondary
        results = []
        
        # Execute all in parallel (simplified - TODO: async)
        for domain in all_domains:
            result = self._execute_single_domain(domain, query, context)
            results.append(result)
        
        return {
            "strategy": "parallel",
            "domains": [d.value for d in all_domains],
            "results": results,
            "aggregated": self._aggregate_results(results)
        }
    
    def _search_knowledge_base(
        self,
        domain: LucyDomain,
        query: str
    ) -> Dict[str, List[Dict]]:
        """Search knowledge base collections for domain"""
        
        config = LUCY_ASSISTANTS[domain]
        results = {}
        
        for collection in config.qdrant_collections:
            if collection == "email_history":
                search_results = self.kb.search_emails(query=query, limit=5)
            elif collection == "tech_docs_vectors":
                search_results = self.kb.search_tech_docs(query=query, limit=5)
            elif collection == "beeper_history":
                search_results = self.kb.search_beeper(query=query, limit=5)
            else:
                continue
            
            results[collection] = [
                {
                    "content": r.content[:500],  # Truncate
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in search_results
            ]
        
        return results
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate results from multiple domains"""
        
        total_memories = sum(len(r.get('memories', [])) for r in results)
        total_kb_results = sum(
            len(kb_results)
            for r in results
            for kb_results in r.get('knowledge_base_results', {}).values()
        )
        
        return {
            "total_domains": len(results),
            "total_memories": total_memories,
            "total_knowledge_base_results": total_kb_results,
            "domains_involved": [r.get('domain') for r in results]
        }
    
    def save_interaction(
        self,
        query: str,
        response: Dict[str, Any],
        user_feedback: Optional[str] = None
    ):
        """Save interaction for learning"""
        
        # Save to orchestrator memory
        self.memory.add_memory(
            namespace="lucy_orchestrator",
            content=f"Query: {query}\nResponse: {response.get('domain', 'unknown')}",
            category="routing_decision",
            metadata={
                "query": query,
                "routed_to": response.get('domain'),
                "user_feedback": user_feedback
            }
        )
    
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        
        kb_stats = self.kb.get_all_stats()
        memory_stats = self.memory.get_all_stats()
        
        return {
            "knowledge_base": kb_stats,
            "memory": memory_stats,
            "assistants": {
                domain.value: {
                    "name": config.name,
                    "collections": config.qdrant_collections,
                    "namespace": config.mem0_namespace
                }
                for domain, config in LUCY_ASSISTANTS.items()
            }
        }


if __name__ == "__main__":
    print("🎭 Lucy Orchestrator Test")
    print("=" * 70)
    
    # Initialize
    orchestrator = LucyOrchestrator()
    
    # Test queries
    test_queries = [
        "Show me emails about Qdrant from last week",
        "How do I use Qdrant filters?",
        "Find project emails and show me the relevant docs",
        "What N8N workflows do we have?",
        "Show me Linear tasks for the database project"
    ]
    
    print("\n📝 Test Queries:")
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        
        # Analyze routing
        routing = orchestrator.analyze_query(query)
        print(f"   → {routing.primary_domain.value} ({routing.strategy})")
        if routing.secondary_domains:
            print(f"   + {[d.value for d in routing.secondary_domains]}")
    
    # Show system stats
    print(f"\n{'='*70}")
    print("\n📊 System Statistics:")
    stats = orchestrator.get_system_stats()
    
    print("\n   Knowledge Base:")
    for name, stat in stats['knowledge_base'].items():
        if 'error' not in stat:
            print(f"      {name}: {stat['points_count']:,} points")
    
    print("\n   Memory:")
    for ns, stat in stats['memory'].items():
        print(f"      {ns}: {stat['total_memories']} memories")
    
    print("\n✅ Orchestrator Ready!")
