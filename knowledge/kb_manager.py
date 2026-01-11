"""
Lucy Knowledge Base Manager
Handles Qdrant queries and knowledge retrieval for all assistants
"""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

@dataclass
class SearchResult:
    """Single search result from knowledge base"""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str  # Collection name
    
class KnowledgeBaseManager:
    """Manages all knowledge base operations for Lucy"""
    
    def __init__(self, qdrant_host: str = "192.168.1.129", qdrant_port: int = 6333):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collections = self._discover_collections()
        
    def _discover_collections(self) -> List[str]:
        """Discover available collections"""
        try:
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            print(f"Error discovering collections: {e}")
            return []
    
    def search_emails(
        self,
        query: str = None,
        sender: str = None,
        subject: str = None,
        date_from: str = None,
        date_to: str = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search email history"""
        
        filters = []
        
        if sender:
            filters.append(FieldCondition(
                key="sender",
                match=MatchValue(value=sender)
            ))
        
        if subject:
            filters.append(FieldCondition(
                key="subject",
                match=MatchValue(value=subject)
            ))
        
        # For now, simple text search in payload
        # TODO: Add vector search with embeddings
        try:
            points = self.client.scroll(
                collection_name="email_history",
                limit=limit,
                with_payload=True,
                with_vectors=False
            )[0]
            
            results = []
            for point in points:
                # Simple text matching for now
                payload = point.payload
                if query:
                    content = payload.get('content', '') + ' ' + payload.get('subject', '')
                    if query.lower() not in content.lower():
                        continue
                
                results.append(SearchResult(
                    content=payload.get('content', ''),
                    score=1.0,  # Placeholder
                    metadata={
                        'sender': payload.get('sender'),
                        'subject': payload.get('subject'),
                        'date': payload.get('date'),
                        'thread_id': payload.get('thread_id')
                    },
                    source='email_history'
                ))
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def search_tech_docs(
        self,
        query: str,
        tool: str = None,
        doc_type: str = None,
        limit: int = 5
    ) -> List[SearchResult]:
        """Search technical documentation"""
        
        try:
            # Build filter
            must_conditions = []
            
            if tool:
                must_conditions.append(FieldCondition(
                    key="tool",
                    match=MatchValue(value=tool.lower())
                ))
            
            if doc_type:
                must_conditions.append(FieldCondition(
                    key="type",
                    match=MatchValue(value=doc_type)
                ))
            
            filter_obj = Filter(must=must_conditions) if must_conditions else None
            
            # For now, scroll and filter (TODO: proper vector search)
            points = self.client.scroll(
                collection_name="tech_docs_vectors",
                limit=limit * 3,  # Get more to filter
                with_payload=True,
                with_vectors=False,
                scroll_filter=filter_obj
            )[0]
            
            results = []
            for point in points:
                payload = point.payload
                content = payload.get('content', '')
                title = payload.get('title', '')
                
                # Simple text matching
                if query.lower() in content.lower() or query.lower() in title.lower():
                    results.append(SearchResult(
                        content=content[:2000],  # Limit content
                        score=1.0,  # Placeholder
                        metadata={
                            'title': title,
                            'url': payload.get('url'),
                            'tool': payload.get('tool'),
                            'type': payload.get('type')
                        },
                        source='tech_docs_vectors'
                    ))
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            print(f"Error searching tech docs: {e}")
            return []
    
    def search_beeper(
        self,
        query: str = None,
        network: str = None,
        participant: str = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search Beeper chat history"""
        
        try:
            # Check if collection exists
            if "beeper_history" not in self.collections:
                return []
            
            must_conditions = []
            
            if network:
                must_conditions.append(FieldCondition(
                    key="network",
                    match=MatchValue(value=network)
                ))
            
            filter_obj = Filter(must=must_conditions) if must_conditions else None
            
            points = self.client.scroll(
                collection_name="beeper_history",
                limit=limit,
                with_payload=True,
                with_vectors=False,
                scroll_filter=filter_obj
            )[0]
            
            results = []
            for point in points:
                payload = point.payload
                conversation = payload.get('conversation', '')
                
                if query and query.lower() not in conversation.lower():
                    continue
                
                results.append(SearchResult(
                    content=conversation[:2000],
                    score=1.0,
                    metadata={
                        'chat_name': payload.get('chat_name'),
                        'network': payload.get('network'),
                        'participants': payload.get('participants', []),
                        'message_count': payload.get('message_count')
                    },
                    source='beeper_history'
                ))
            
            return results
            
        except Exception as e:
            print(f"Error searching Beeper: {e}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                'name': collection_name,
                'points_count': info.points_count,
                'vectors_count': info.vectors_count,
                'indexed_vectors_count': info.indexed_vectors_count,
                'status': info.status
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all collections"""
        stats = {}
        for collection in self.collections:
            stats[collection] = self.get_collection_stats(collection)
        return stats
    
    def search_cross_collection(
        self,
        query: str,
        collections: List[str],
        limit_per_collection: int = 5
    ) -> Dict[str, List[SearchResult]]:
        """Search across multiple collections"""
        results = {}
        
        for collection in collections:
            if collection == "email_history":
                results[collection] = self.search_emails(query=query, limit=limit_per_collection)
            elif collection == "tech_docs_vectors":
                results[collection] = self.search_tech_docs(query=query, limit=limit_per_collection)
            elif collection == "beeper_history":
                results[collection] = self.search_beeper(query=query, limit=limit_per_collection)
        
        return results


if __name__ == "__main__":
    # Test knowledge base
    kb = KnowledgeBaseManager()
    
    print("📚 Lucy Knowledge Base Manager")
    print("=" * 70)
    
    # Show stats
    print("\n📊 Collection Statistics:")
    stats = kb.get_all_stats()
    for name, stat in stats.items():
        if 'error' in stat:
            print(f"   ❌ {name}: {stat['error']}")
        else:
            print(f"   ✅ {name}: {stat['points_count']:,} points")
    
    # Test searches
    print("\n🔍 Test Searches:")
    
    print("\n1. Search tech docs (Qdrant):")
    results = kb.search_tech_docs("query", tool="qdrant", limit=3)
    for r in results:
        print(f"   • {r.metadata.get('title', 'No title')[:60]}...")
    
    print("\n2. Search emails:")
    results = kb.search_emails(query="project", limit=3)
    for r in results:
        print(f"   • From: {r.metadata.get('sender', 'Unknown')[:40]}")
        print(f"     Subject: {r.metadata.get('subject', 'No subject')[:60]}")
    
    print("\n✅ Knowledge Base Manager Ready!")
