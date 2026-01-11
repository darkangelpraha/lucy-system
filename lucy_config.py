"""
LUCY SYSTEM - Complete Architecture Configuration
Production-ready multi-assistant system with shared memory
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# LUCY DOMAINS
# ============================================================================

class LucyDomain(Enum):
    """Lucy assistant domains"""
    COMMUNICATIONS = "communications"    # Email, Beeper, messaging
    PROJECTS = "projects"                # Linear, GitHub, project management
    KNOWLEDGE = "knowledge"              # Tech docs, research, learning
    CONTENT = "content"                  # N8N, automation, content creation
    DATA = "data"                        # Qdrant, Supabase, databases
    DEV = "dev"                          # VSCode, Docker, development
    BUSINESS = "business"                # Business ops, financials
    PERSONAL = "personal"                # Personal assistant tasks
    ORCHESTRATOR = "orchestrator"        # Coordinates all others


# ============================================================================
# LUCY ASSISTANT CONFIG
# ============================================================================

@dataclass
class LucyAssistantConfig:
    """Configuration for single Lucy assistant"""
    domain: LucyDomain
    name: str
    description: str
    
    # Knowledge base
    qdrant_collections: List[str]
    knowledge_categories: List[str]
    
    # Capabilities
    tools: List[str]
    actions: List[str]
    
    # Memory
    mem0_namespace: str
    memory_categories: List[str]
    
    # Behavior
    temperature: float = 0.7
    max_tokens: int = 4000
    model: str = "claude-sonnet-4"
    
    # Learning
    learn_from_corrections: bool = True
    save_successful_patterns: bool = True
    cross_domain_learning: bool = True


# ============================================================================
# COMPLETE LUCY CONFIGURATION
# ============================================================================

LUCY_ASSISTANTS: Dict[LucyDomain, LucyAssistantConfig] = {
    
    # ========================================================================
    # LUCY-COMMUNICATIONS
    # ========================================================================
    LucyDomain.COMMUNICATIONS: LucyAssistantConfig(
        domain=LucyDomain.COMMUNICATIONS,
        name="Lucy-Communications",
        description="Email, messaging, Beeper - all communication channels",
        
        qdrant_collections=[
            "email_history",
            "beeper_history"
        ],
        
        knowledge_categories=[
            "email_threads",
            "contacts",
            "conversations",
            "message_history",
            "communication_patterns"
        ],
        
        tools=[
            "search_emails",
            "get_email_thread",
            "list_contacts",
            "search_beeper_chats",
            "get_conversation_context",
            "analyze_communication_frequency"
        ],
        
        actions=[
            "find_emails_by_sender",
            "find_emails_by_topic",
            "get_conversation_history",
            "identify_important_contacts",
            "track_response_times",
            "summarize_email_threads"
        ],
        
        mem0_namespace="lucy_communications",
        
        memory_categories=[
            "contact_preferences",
            "email_patterns",
            "important_threads",
            "response_styles",
            "communication_context"
        ],
        
        temperature=0.5,  # More deterministic for factual retrieval
    ),
    
    # ========================================================================
    # LUCY-PROJECTS
    # ========================================================================
    LucyDomain.PROJECTS: LucyAssistantConfig(
        domain=LucyDomain.PROJECTS,
        name="Lucy-Projects",
        description="Project management, Linear, GitHub, task tracking",
        
        qdrant_collections=[
            "tech_docs_vectors",  # For project-related tech docs
            "email_history"        # For project communication
        ],
        
        knowledge_categories=[
            "projects",
            "tasks",
            "issues",
            "pull_requests",
            "project_timelines",
            "team_collaboration"
        ],
        
        tools=[
            "search_linear_issues",
            "get_github_prs",
            "track_project_status",
            "find_project_emails",
            "analyze_project_velocity"
        ],
        
        actions=[
            "find_project_by_name",
            "get_project_status",
            "list_active_tasks",
            "track_blockers",
            "summarize_project_updates",
            "identify_dependencies"
        ],
        
        mem0_namespace="lucy_projects",
        
        memory_categories=[
            "project_context",
            "team_members",
            "project_goals",
            "blockers",
            "milestones",
            "workflow_patterns"
        ],
        
        temperature=0.6,
    ),
    
    # ========================================================================
    # LUCY-KNOWLEDGE
    # ========================================================================
    LucyDomain.KNOWLEDGE: LucyAssistantConfig(
        domain=LucyDomain.KNOWLEDGE,
        name="Lucy-Knowledge",
        description="Tech documentation, research, learning, knowledge base",
        
        qdrant_collections=[
            "tech_docs_vectors"
        ],
        
        knowledge_categories=[
            "tech_documentation",
            "api_references",
            "tutorials",
            "best_practices",
            "code_examples",
            "troubleshooting"
        ],
        
        tools=[
            "search_tech_docs",
            "get_api_reference",
            "find_tutorials",
            "search_code_examples",
            "get_troubleshooting_guides"
        ],
        
        actions=[
            "answer_technical_question",
            "find_documentation",
            "explain_concept",
            "provide_code_example",
            "troubleshoot_issue",
            "recommend_best_practice"
        ],
        
        mem0_namespace="lucy_knowledge",
        
        memory_categories=[
            "learned_concepts",
            "frequently_asked",
            "personal_notes",
            "bookmarks",
            "learning_paths",
            "expertise_areas"
        ],
        
        temperature=0.4,  # Very deterministic for accurate knowledge
    ),
    
    # ========================================================================
    # LUCY-CONTENT
    # ========================================================================
    LucyDomain.CONTENT: LucyAssistantConfig(
        domain=LucyDomain.CONTENT,
        name="Lucy-Content",
        description="N8N workflows, automation, content creation",
        
        qdrant_collections=[
            "tech_docs_vectors"  # N8N, automation tools docs
        ],
        
        knowledge_categories=[
            "n8n_workflows",
            "automation",
            "content_templates",
            "workflow_patterns",
            "integrations"
        ],
        
        tools=[
            "search_n8n_docs",
            "find_workflow_examples",
            "get_integration_docs",
            "search_automation_patterns"
        ],
        
        actions=[
            "create_workflow",
            "suggest_automation",
            "find_integration",
            "troubleshoot_workflow",
            "optimize_automation",
            "generate_content"
        ],
        
        mem0_namespace="lucy_content",
        
        memory_categories=[
            "workflow_templates",
            "automation_patterns",
            "content_preferences",
            "integration_configs",
            "successful_automations"
        ],
        
        temperature=0.7,  # More creative for content
    ),
    
    # ========================================================================
    # LUCY-DATA
    # ========================================================================
    LucyDomain.DATA: LucyAssistantConfig(
        domain=LucyDomain.DATA,
        name="Lucy-Data",
        description="Qdrant, Supabase, databases, data operations",
        
        qdrant_collections=[
            "tech_docs_vectors",  # Qdrant, Supabase, Postgres docs
            "email_history",      # For data-related emails
        ],
        
        knowledge_categories=[
            "database_schemas",
            "queries",
            "data_models",
            "migrations",
            "performance_optimization",
            "data_pipelines"
        ],
        
        tools=[
            "search_db_docs",
            "query_qdrant",
            "get_schema_info",
            "find_query_examples",
            "analyze_performance"
        ],
        
        actions=[
            "write_query",
            "design_schema",
            "optimize_query",
            "troubleshoot_database",
            "migrate_data",
            "analyze_data_patterns"
        ],
        
        mem0_namespace="lucy_data",
        
        memory_categories=[
            "schemas",
            "query_patterns",
            "performance_tips",
            "migration_history",
            "data_models",
            "optimization_strategies"
        ],
        
        temperature=0.3,  # Very precise for data operations
    ),
    
    # ========================================================================
    # LUCY-DEV
    # ========================================================================
    LucyDomain.DEV: LucyAssistantConfig(
        domain=LucyDomain.DEV,
        name="Lucy-Dev",
        description="VSCode, Docker, development tools, coding",
        
        qdrant_collections=[
            "tech_docs_vectors"  # VSCode, Docker, dev tools docs
        ],
        
        knowledge_categories=[
            "development_setup",
            "docker_configs",
            "vscode_extensions",
            "development_workflows",
            "debugging",
            "tooling"
        ],
        
        tools=[
            "search_dev_docs",
            "find_docker_examples",
            "get_vscode_config",
            "search_debugging_guides"
        ],
        
        actions=[
            "setup_dev_environment",
            "configure_docker",
            "troubleshoot_build",
            "optimize_workflow",
            "debug_issue",
            "recommend_tools"
        ],
        
        mem0_namespace="lucy_dev",
        
        memory_categories=[
            "dev_configs",
            "docker_setups",
            "build_scripts",
            "debugging_patterns",
            "tool_preferences",
            "workflow_optimizations"
        ],
        
        temperature=0.5,
    ),
    
    # ========================================================================
    # LUCY-BUSINESS
    # ========================================================================
    LucyDomain.BUSINESS: LucyAssistantConfig(
        domain=LucyDomain.BUSINESS,
        name="Lucy-Business",
        description="Business operations, financials, planning",
        
        qdrant_collections=[
            "email_history",      # Business emails
            "tech_docs_vectors"   # Business tools docs
        ],
        
        knowledge_categories=[
            "business_processes",
            "financials",
            "planning",
            "client_relations",
            "contracts",
            "invoicing"
        ],
        
        tools=[
            "search_business_emails",
            "track_invoices",
            "find_contracts",
            "analyze_finances"
        ],
        
        actions=[
            "find_client_communication",
            "track_project_financials",
            "manage_invoices",
            "analyze_business_metrics",
            "plan_resources",
            "client_reporting"
        ],
        
        mem0_namespace="lucy_business",
        
        memory_categories=[
            "client_preferences",
            "contract_terms",
            "pricing",
            "business_goals",
            "financial_patterns",
            "process_improvements"
        ],
        
        temperature=0.4,  # Precise for business data
    ),
    
    # ========================================================================
    # LUCY-PERSONAL
    # ========================================================================
    LucyDomain.PERSONAL: LucyAssistantConfig(
        domain=LucyDomain.PERSONAL,
        name="Lucy-Personal",
        description="Personal assistant, scheduling, reminders, preferences",
        
        qdrant_collections=[
            "email_history",
            "beeper_history"
        ],
        
        knowledge_categories=[
            "personal_preferences",
            "schedules",
            "reminders",
            "personal_notes",
            "habits",
            "goals"
        ],
        
        tools=[
            "search_personal_emails",
            "track_habits",
            "manage_reminders",
            "find_personal_notes"
        ],
        
        actions=[
            "schedule_task",
            "set_reminder",
            "track_habit",
            "manage_goals",
            "personal_search",
            "preference_tracking"
        ],
        
        mem0_namespace="lucy_personal",
        
        memory_categories=[
            "preferences",
            "habits",
            "goals",
            "schedules",
            "personal_context",
            "important_dates"
        ],
        
        temperature=0.6,
    ),
    
    # ========================================================================
    # LUCY-ORCHESTRATOR
    # ========================================================================
    LucyDomain.ORCHESTRATOR: LucyAssistantConfig(
        domain=LucyDomain.ORCHESTRATOR,
        name="Lucy-Orchestrator",
        description="Coordinates all Lucy assistants, routes queries, manages cross-domain tasks",
        
        qdrant_collections=[
            # Has access to ALL collections for routing decisions
            "email_history",
            "beeper_history",
            "tech_docs_vectors"
        ],
        
        knowledge_categories=[
            "routing_patterns",
            "cross_domain_tasks",
            "assistant_capabilities",
            "workflow_orchestration"
        ],
        
        tools=[
            "route_to_assistant",
            "coordinate_multi_domain",
            "aggregate_results",
            "manage_context_sharing"
        ],
        
        actions=[
            "analyze_query",
            "route_request",
            "coordinate_assistants",
            "aggregate_responses",
            "manage_cross_domain",
            "optimize_workflow"
        ],
        
        mem0_namespace="lucy_orchestrator",
        
        memory_categories=[
            "routing_decisions",
            "successful_workflows",
            "assistant_specialties",
            "cross_domain_patterns",
            "optimization_strategies"
        ],
        
        temperature=0.5,  # Balanced for routing decisions
    ),
}


# ============================================================================
# QDRANT CONFIGURATION
# ============================================================================

QDRANT_CONFIG = {
    "host": "192.168.1.129",
    "port": 6333,
    "collections": {
        "email_history": {
            "vector_size": 1536,
            "distance": "Cosine",
            "indexed_count": 5757,  # Current count
            "description": "6 months of Gmail messages with threads and contacts"
        },
        "beeper_history": {
            "vector_size": 1536,
            "distance": "Cosine",
            "indexed_count": 0,  # Optional - not yet indexed
            "description": "Beeper cross-network messaging history"
        },
        "tech_docs_vectors": {
            "vector_size": 1536,
            "distance": "Cosine",
            "indexed_count": 22315,  # Current count
            "description": "14 tech tools documentation (Qdrant, Mem0, Supabase, etc.)"
        }
    }
}


# ============================================================================
# MEM0 CONFIGURATION
# ============================================================================

MEM0_CONFIG = {
    "version": "1.0",
    "type": "shared_memory",
    
    "namespaces": {
        domain.value: {
            "name": f"lucy_{domain.value}",
            "description": LUCY_ASSISTANTS[domain].description,
            "memory_categories": LUCY_ASSISTANTS[domain].memory_categories,
            "cross_domain_access": True,  # All assistants can read others' memories
            "learning_enabled": True
        }
        for domain in LucyDomain
    },
    
    "shared_memory": {
        "enabled": True,
        "global_namespace": "lucy_global",
        "cross_domain_learning": True,
        "memory_retention_days": 365,
        "auto_consolidation": True
    },
    
    "learning": {
        "from_corrections": True,
        "from_successful_patterns": True,
        "from_user_feedback": True,
        "cross_domain_transfer": True,
        "auto_save_interval_minutes": 5
    }
}


# ============================================================================
# ROUTING RULES
# ============================================================================

ROUTING_RULES = {
    # Keywords that trigger specific assistants
    "email": [LucyDomain.COMMUNICATIONS],
    "message": [LucyDomain.COMMUNICATIONS],
    "beeper": [LucyDomain.COMMUNICATIONS],
    "contact": [LucyDomain.COMMUNICATIONS],
    
    "project": [LucyDomain.PROJECTS],
    "linear": [LucyDomain.PROJECTS],
    "github": [LucyDomain.PROJECTS],
    "task": [LucyDomain.PROJECTS],
    "issue": [LucyDomain.PROJECTS],
    
    "docs": [LucyDomain.KNOWLEDGE],
    "documentation": [LucyDomain.KNOWLEDGE],
    "how to": [LucyDomain.KNOWLEDGE],
    "api": [LucyDomain.KNOWLEDGE],
    "tutorial": [LucyDomain.KNOWLEDGE],
    
    "workflow": [LucyDomain.CONTENT],
    "n8n": [LucyDomain.CONTENT],
    "automation": [LucyDomain.CONTENT],
    
    "database": [LucyDomain.DATA],
    "qdrant": [LucyDomain.DATA],
    "supabase": [LucyDomain.DATA],
    "query": [LucyDomain.DATA],
    "postgres": [LucyDomain.DATA],
    
    "docker": [LucyDomain.DEV],
    "vscode": [LucyDomain.DEV],
    "development": [LucyDomain.DEV],
    "build": [LucyDomain.DEV],
    
    "invoice": [LucyDomain.BUSINESS],
    "client": [LucyDomain.BUSINESS],
    "business": [LucyDomain.BUSINESS],
    "finance": [LucyDomain.BUSINESS],
    
    "remind": [LucyDomain.PERSONAL],
    "schedule": [LucyDomain.PERSONAL],
    "personal": [LucyDomain.PERSONAL],
}

# Multi-domain queries (requires orchestration)
MULTI_DOMAIN_PATTERNS = [
    {
        "pattern": r".*email.*about.*(?:qdrant|supabase|database).*",
        "domains": [LucyDomain.COMMUNICATIONS, LucyDomain.DATA],
        "strategy": "sequential"  # Communications first, then Data for context
    },
    {
        "pattern": r".*project.*(?:email|message).*",
        "domains": [LucyDomain.PROJECTS, LucyDomain.COMMUNICATIONS],
        "strategy": "parallel"  # Both can work simultaneously
    },
    {
        "pattern": r".*docs.*for.*project.*",
        "domains": [LucyDomain.KNOWLEDGE, LucyDomain.PROJECTS],
        "strategy": "sequential"  # Knowledge first, then Projects for application
    }
]


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

SYSTEM_PROMPT_TEMPLATE = """You are {assistant_name}, a specialized AI assistant in the Lucy multi-assistant system.

**Your Domain:** {domain_description}

**Your Capabilities:**
{capabilities}

**Knowledge Base Access:**
- Collections: {collections}
- Categories: {categories}

**Memory System:**
- Namespace: {namespace}
- You have access to shared memories from other Lucy assistants
- You learn from corrections and save successful patterns
- Your memory categories: {memory_categories}

**Behavior Guidelines:**
1. **Accuracy First:** Retrieve from knowledge base before answering
2. **Learn Continuously:** Save corrections to memory immediately
3. **Cross-Domain Awareness:** Use other assistants' memories when relevant
4. **Context Preservation:** Maintain conversation context across sessions
5. **Transparency:** Tell user when information comes from memory vs knowledge base

**When Uncertain:**
- Search knowledge base thoroughly
- Check relevant memories
- If still uncertain, clearly state limitations
- Suggest which other Lucy assistant might help

**Memory Management:**
- Save user preferences immediately
- Track successful patterns for reuse
- Learn from corrections
- Share relevant learnings with other assistants

You are part of a coordinated system. Work efficiently within your domain while being aware of the broader Lucy ecosystem.
"""


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate Lucy configuration completeness"""
    issues = []
    
    # Check all domains have configs
    for domain in LucyDomain:
        if domain not in LUCY_ASSISTANTS:
            issues.append(f"Missing config for {domain.value}")
    
    # Check all assistants have required fields
    for domain, config in LUCY_ASSISTANTS.items():
        if not config.qdrant_collections:
            issues.append(f"{domain.value}: No Qdrant collections defined")
        if not config.knowledge_categories:
            issues.append(f"{domain.value}: No knowledge categories")
        if not config.tools:
            issues.append(f"{domain.value}: No tools defined")
        if not config.memory_categories:
            issues.append(f"{domain.value}: No memory categories")
    
    # Check Mem0 namespaces
    if len(MEM0_CONFIG["namespaces"]) != len(LucyDomain):
        issues.append(f"Mem0 namespaces mismatch: {len(MEM0_CONFIG['namespaces'])} != {len(LucyDomain)}")
    
    return issues


if __name__ == "__main__":
    print("🔍 Validating Lucy Configuration...")
    issues = validate_config()
    
    if issues:
        print("\n❌ Configuration Issues Found:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("\n✅ Configuration Valid!")
        print(f"\n📊 Lucy System Overview:")
        print(f"   Assistants: {len(LUCY_ASSISTANTS)}")
        print(f"   Collections: {len(QDRANT_CONFIG['collections'])}")
        print(f"   Mem0 Namespaces: {len(MEM0_CONFIG['namespaces'])}")
        print(f"   Total Indexed:")
        print(f"      Emails: {QDRANT_CONFIG['collections']['email_history']['indexed_count']:,}")
        print(f"      Tech Docs: {QDRANT_CONFIG['collections']['tech_docs_vectors']['indexed_count']:,}")
        print(f"   Ready for deployment! 🚀")
