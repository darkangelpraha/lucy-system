"""
Lucy Memory Manager - Mem0 Integration
Handles all memory operations for Lucy assistants
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class Memory:
    """Single memory entry"""
    content: str
    category: str
    namespace: str
    created_at: str
    metadata: Dict[str, Any]
    memory_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MemoryManager:
    """Manages Lucy's memory system using Mem0"""
    
    def __init__(self, storage_dir: str = "./lucy_memories"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Namespace storage
        self.namespaces = {}
        self._load_all_namespaces()
    
    def _load_all_namespaces(self):
        """Load all existing memory namespaces"""
        for file in self.storage_dir.glob("*.json"):
            namespace = file.stem
            with open(file) as f:
                self.namespaces[namespace] = json.load(f)
    
    def _save_namespace(self, namespace: str):
        """Save namespace to disk"""
        file_path = self.storage_dir / f"{namespace}.json"
        with open(file_path, 'w') as f:
            json.dump(self.namespaces.get(namespace, {}), f, indent=2)
    
    def create_namespace(self, namespace: str, description: str = ""):
        """Create new memory namespace"""
        if namespace not in self.namespaces:
            self.namespaces[namespace] = {
                "namespace": namespace,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "memories": [],
                "categories": {}
            }
            self._save_namespace(namespace)
            return True
        return False
    
    def add_memory(
        self,
        namespace: str,
        content: str,
        category: str,
        metadata: Dict[str, Any] = None
    ) -> Memory:
        """Add memory to namespace"""
        
        # Ensure namespace exists
        if namespace not in self.namespaces:
            self.create_namespace(namespace)
        
        # Create memory
        memory = Memory(
            content=content,
            category=category,
            namespace=namespace,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
            memory_id=f"{namespace}_{len(self.namespaces[namespace]['memories'])}"
        )
        
        # Add to namespace
        self.namespaces[namespace]['memories'].append(memory.to_dict())
        
        # Update category count
        if category not in self.namespaces[namespace]['categories']:
            self.namespaces[namespace]['categories'][category] = 0
        self.namespaces[namespace]['categories'][category] += 1
        
        # Save
        self._save_namespace(namespace)
        
        return memory
    
    def search_memories(
        self,
        namespace: str,
        query: str = None,
        category: str = None,
        limit: int = 10
    ) -> List[Memory]:
        """Search memories in namespace"""
        
        if namespace not in self.namespaces:
            return []
        
        memories = self.namespaces[namespace]['memories']
        results = []
        
        for mem_dict in memories:
            # Category filter
            if category and mem_dict['category'] != category:
                continue
            
            # Text search
            if query:
                if query.lower() not in mem_dict['content'].lower():
                    continue
            
            results.append(Memory(**mem_dict))
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_memories_by_category(
        self,
        namespace: str,
        category: str
    ) -> List[Memory]:
        """Get all memories in a category"""
        return self.search_memories(namespace, category=category, limit=1000)
    
    def search_cross_namespace(
        self,
        query: str,
        namespaces: List[str] = None,
        limit_per_namespace: int = 5
    ) -> Dict[str, List[Memory]]:
        """Search across multiple namespaces"""
        
        if namespaces is None:
            namespaces = list(self.namespaces.keys())
        
        results = {}
        for ns in namespaces:
            results[ns] = self.search_memories(ns, query=query, limit=limit_per_namespace)
        
        return results
    
    def update_memory(
        self,
        namespace: str,
        memory_id: str,
        content: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update existing memory"""
        
        if namespace not in self.namespaces:
            return False
        
        for mem in self.namespaces[namespace]['memories']:
            if mem['memory_id'] == memory_id:
                if content:
                    mem['content'] = content
                if metadata:
                    mem['metadata'].update(metadata)
                
                self._save_namespace(namespace)
                return True
        
        return False
    
    def delete_memory(self, namespace: str, memory_id: str) -> bool:
        """Delete memory"""
        
        if namespace not in self.namespaces:
            return False
        
        memories = self.namespaces[namespace]['memories']
        initial_count = len(memories)
        
        self.namespaces[namespace]['memories'] = [
            m for m in memories if m['memory_id'] != memory_id
        ]
        
        if len(self.namespaces[namespace]['memories']) < initial_count:
            self._save_namespace(namespace)
            return True
        
        return False
    
    def get_namespace_stats(self, namespace: str) -> Dict:
        """Get statistics for namespace"""
        
        if namespace not in self.namespaces:
            return {}
        
        ns = self.namespaces[namespace]
        return {
            "namespace": namespace,
            "description": ns.get('description', ''),
            "total_memories": len(ns['memories']),
            "categories": ns.get('categories', {}),
            "created_at": ns.get('created_at')
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all namespaces"""
        return {
            ns: self.get_namespace_stats(ns)
            for ns in self.namespaces.keys()
        }
    
    def export_namespace(self, namespace: str, output_file: str):
        """Export namespace to JSON file"""
        if namespace in self.namespaces:
            with open(output_file, 'w') as f:
                json.dump(self.namespaces[namespace], f, indent=2)
    
    def import_namespace(self, namespace: str, input_file: str):
        """Import namespace from JSON file"""
        with open(input_file) as f:
            data = json.load(f)
            self.namespaces[namespace] = data
            self._save_namespace(namespace)


# Learning System - Auto-saves corrections and patterns
class LearningSystem:
    """Handles automatic learning from corrections and patterns"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
    
    def save_correction(
        self,
        namespace: str,
        original_query: str,
        incorrect_response: str,
        correct_response: str,
        context: Dict[str, Any] = None
    ):
        """Save a correction for learning"""
        
        content = f"Query: {original_query}\nIncorrect: {incorrect_response}\nCorrect: {correct_response}"
        
        self.memory.add_memory(
            namespace=namespace,
            content=content,
            category="correction",
            metadata={
                "type": "correction",
                "original_query": original_query,
                "learned_at": datetime.now().isoformat(),
                **(context or {})
            }
        )
    
    def save_successful_pattern(
        self,
        namespace: str,
        query_type: str,
        successful_approach: str,
        outcome: str,
        metadata: Dict[str, Any] = None
    ):
        """Save a successful pattern for reuse"""
        
        content = f"Type: {query_type}\nApproach: {successful_approach}\nOutcome: {outcome}"
        
        self.memory.add_memory(
            namespace=namespace,
            content=content,
            category="successful_pattern",
            metadata={
                "type": "success_pattern",
                "query_type": query_type,
                "saved_at": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
    
    def save_user_preference(
        self,
        namespace: str,
        preference_type: str,
        preference_value: Any,
        context: str = ""
    ):
        """Save user preference"""
        
        content = f"{preference_type}: {preference_value}\nContext: {context}"
        
        self.memory.add_memory(
            namespace=namespace,
            content=content,
            category="user_preference",
            metadata={
                "type": "preference",
                "preference_type": preference_type,
                "value": str(preference_value),
                "saved_at": datetime.now().isoformat()
            }
        )
    
    def get_relevant_learnings(
        self,
        namespace: str,
        query: str,
        limit: int = 5
    ) -> List[Memory]:
        """Get relevant past learnings for a query"""
        
        # Search corrections
        corrections = self.memory.search_memories(
            namespace, query=query, category="correction", limit=limit
        )
        
        # Search successful patterns
        patterns = self.memory.search_memories(
            namespace, query=query, category="successful_pattern", limit=limit
        )
        
        return corrections + patterns


if __name__ == "__main__":
    # Test memory system
    print("🧠 Lucy Memory Manager Test")
    print("=" * 70)
    
    # Create manager
    mm = MemoryManager(storage_dir="./test_lucy_memories")
    learning = LearningSystem(mm)
    
    # Create namespaces for Lucy assistants
    namespaces = [
        "lucy_communications",
        "lucy_knowledge",
        "lucy_projects",
        "lucy_orchestrator"
    ]
    
    for ns in namespaces:
        mm.create_namespace(ns, description=f"Memory namespace for {ns}")
    
    # Add test memories
    mm.add_memory(
        namespace="lucy_communications",
        content="User prefers email summaries to be concise",
        category="user_preference",
        metadata={"type": "email_preference"}
    )
    
    mm.add_memory(
        namespace="lucy_knowledge",
        content="Qdrant filters use FieldCondition with MatchValue",
        category="technical_knowledge",
        metadata={"tool": "qdrant", "topic": "filters"}
    )
    
    learning.save_correction(
        namespace="lucy_projects",
        original_query="show me linear tasks",
        incorrect_response="Showed all tasks",
        correct_response="Should show only active tasks by default"
    )
    
    # Show stats
    print("\n📊 Memory Statistics:")
    stats = mm.get_all_stats()
    for ns, stat in stats.items():
        print(f"\n   {ns}:")
        print(f"      Total memories: {stat['total_memories']}")
        print(f"      Categories: {stat['categories']}")
    
    print("\n✅ Memory Manager Ready!")
