"""
Lucy Error Learning System - NIKDY NEOPAKOVAT STEJNOU CHYBU

Každá chyba se uloží do Mem0 + Supabase s:
- Co se stalo (popis chyby)
- Proč se to stalo (root cause)
- Jak to opravit (solution)
- Jak zabránit opakování (prevention)

Před každou akcí Lucy checkuje: "Dělala jsem tohle už? Jak to dopadlo?"
"""

import json
from datetime import datetime
from typing import Dict, Optional
import hashlib

class ErrorLearningSystem:
    """
    Systém pro učení z chyb - ŽÁDNÁ CHYBA DVAKRÁT
    """
    
    def __init__(self, supabase_client, mem0_client):
        self.supabase = supabase_client
        self.mem0 = mem0_client
        self.error_collection = "lucy_errors"
    
    def record_error(
        self,
        error_type: str,
        what_happened: str,
        why_happened: str,
        how_to_fix: str,
        how_to_prevent: str,
        context: Dict,
        severity: str = "medium"
    ) -> str:
        """
        Zaznamenat chybu - TRVALE
        
        Args:
            error_type: Typ chyby (misunderstood_request, wrong_deployment, etc.)
            what_happened: Co se stalo
            why_happened: Proč se to stalo (root cause)
            how_to_fix: Jak to opravit
            how_to_prevent: Jak zabránit opakování
            context: Kontext (user request, system state, etc.)
            severity: critical/high/medium/low
        """
        
        # Unique ID z typu a kontextu
        error_id = hashlib.md5(
            f"{error_type}:{what_happened}".encode()
        ).hexdigest()
        
        error_record = {
            "error_id": error_id,
            "error_type": error_type,
            "what_happened": what_happened,
            "why_happened": why_happened,
            "how_to_fix": how_to_fix,
            "how_to_prevent": how_to_prevent,
            "context": json.dumps(context),
            "severity": severity,
            "occurred_at": datetime.now().isoformat(),
            "occurrence_count": 1,
            "last_occurred": datetime.now().isoformat()
        }
        
        # Save to Supabase (hot buffer)
        existing = self.supabase.table(self.error_collection)\
            .select("*")\
            .eq("error_id", error_id)\
            .execute()
        
        if existing.data:
            # Update occurrence count
            count = existing.data[0]['occurrence_count'] + 1
            self.supabase.table(self.error_collection)\
                .update({
                    "occurrence_count": count,
                    "last_occurred": datetime.now().isoformat()
                })\
                .eq("error_id", error_id)\
                .execute()
            
            print(f"⚠️ ERROR REPEATED {count}x: {error_type}")
            print(f"   This should NOT happen! Review prevention strategy.")
        else:
            # New error
            self.supabase.table(self.error_collection)\
                .insert(error_record)\
                .execute()
        
        # Save to Mem0 (long-term learning)
        self.mem0.add(
            messages=[{
                "role": "system",
                "content": f"ERROR LEARNED: {error_type}\n"
                          f"What: {what_happened}\n"
                          f"Why: {why_happened}\n"
                          f"Fix: {how_to_fix}\n"
                          f"Prevention: {how_to_prevent}"
            }],
            user_id="lucy_system",
            metadata={
                "type": "error_learning",
                "error_id": error_id,
                "severity": severity
            }
        )
        
        return error_id
    
    def check_before_action(
        self,
        action_type: str,
        action_context: Dict
    ) -> Optional[Dict]:
        """
        Před akcí: Zkontroluj jestli jsme to už někdy pokazili
        
        Returns:
            Dict s warningem pokud podobná akce vedla k chybě, None jinak
        """
        
        # Search Mem0 for similar errors
        similar_errors = self.mem0.search(
            query=f"{action_type} {json.dumps(action_context)}",
            user_id="lucy_system",
            filters={"type": "error_learning"}
        )
        
        if similar_errors:
            return {
                "warning": True,
                "message": "Similar action caused error before!",
                "previous_errors": similar_errors,
                "recommendation": "Review error prevention strategy before proceeding"
            }
        
        return None
    
    def get_error_stats(self) -> Dict:
        """Stats o chybách - co se opakuje?"""
        
        result = self.supabase.table(self.error_collection)\
            .select("*")\
            .order("occurrence_count", desc=True)\
            .execute()
        
        repeated_errors = [
            e for e in result.data 
            if e['occurrence_count'] > 1
        ]
        
        return {
            "total_errors": len(result.data),
            "repeated_errors": len(repeated_errors),
            "most_repeated": repeated_errors[:5] if repeated_errors else [],
            "critical_unresolved": [
                e for e in result.data
                if e['severity'] == 'critical' and e['occurrence_count'] > 0
            ]
        }


# Example usage pro tuhle konkrétní chybu:
def record_gcp_deployment_mistake():
    """
    Zaznamenat chybu: Nasadil full Lucy na GCP místo thin client
    """
    
    error_system = ErrorLearningSystem(supabase, mem0)
    
    error_system.record_error(
        error_type="misunderstood_deployment_architecture",
        
        what_happened=(
            "User asked for GCP deployment. I created full Lucy deployment on GCP "
            "instead of thin client that connects to NAS + Supabase. "
            "User explicitly said 'dej jenom kostry, ktery si budou sahat na NAS' "
            "but I ignored that and created full deployment with data on GCP."
        ),
        
        why_happened=(
            "I didn't carefully read the full user request. "
            "Focused on 'GCP deployment' keyword and jumped to conclusion. "
            "Didn't parse critical details: 'kostry', 'sahat na NAS', 'bezpecny pripojeni'. "
            "Pattern matching on 'GCP' triggered standard deployment instead of custom architecture."
        ),
        
        how_to_fix=(
            "1. Create thin GCP Cloud Run client (stateless)\n"
            "2. VPN/Cloud VPN to NAS (192.168.1.129)\n"
            "3. Supabase for HOT buffer (operational memory)\n"
            "4. NAS for cold storage (infinite main memory)\n"
            "5. All heavy processing on NAS, GCP just proxies requests"
        ),
        
        how_to_prevent=(
            "BEFORE any deployment task:\n"
            "1. Read ENTIRE user request (not just keywords)\n"
            "2. Extract architecture requirements explicitly\n"
            "3. Confirm understanding: 'You want X architecture with Y components, correct?'\n"
            "4. Check for custom requirements (thin client, specific storage, etc.)\n"
            "5. If unsure, ASK - don't assume standard solution\n"
            "\n"
            "SPECIFIC SIGNALS to watch for:\n"
            "- 'kostra' = thin client, not full app\n"
            "- 'sahat na X' = connect to X, don't duplicate\n"
            "- 'bezpecny pripojeni' = VPN/secure tunnel required\n"
            "- 'buffer' = temporary/hot storage\n"
            "- 'hlavni pamet na X' = X is primary storage\n"
            "\n"
            "ERROR LEARNING CHECK:\n"
            "Before executing, call check_before_action() to see if similar mistake was made before"
        ),
        
        context={
            "user_request": "you installing her on the GCP as we agreed?",
            "previous_context": "v PG je zprovoznenej CloudRun... na GPC dej jenom kostry, ktery si budou sahat na NAS",
            "my_action": "Created full deployment with Dockerfile, docker-compose, terraform for full Lucy on GCP",
            "correct_action": "Should have created thin Cloud Run client connecting to NAS via VPN + Supabase buffer"
        },
        
        severity="high"
    )
    
    print("\n✅ Error recorded to learning system")
    print("   This mistake will NEVER happen again")
    print("   Prevention strategy saved to Mem0")


# Před KAŽDOU akcí Lucy teď udělá:
def before_deployment_action(user_request: str, planned_action: Dict):
    """Check before executing deployment"""
    
    error_system = ErrorLearningSystem(supabase, mem0)
    
    warning = error_system.check_before_action(
        action_type="deployment",
        action_context={
            "user_request": user_request,
            "planned_action": planned_action
        }
    )
    
    if warning:
        print(f"\n⚠️  WARNING: {warning['message']}")
        print(f"   Previous errors found: {len(warning['previous_errors'])}")
        print(f"   Recommendation: {warning['recommendation']}")
        print("\n   Waiting for user confirmation...")
        return False  # Don't proceed automatically
    
    return True  # Safe to proceed
