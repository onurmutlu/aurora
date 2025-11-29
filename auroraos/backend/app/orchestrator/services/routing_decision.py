"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Routing Decision Service               ║
║   Smart routing for FlirtMarket conversations                    ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional

from ..schemas import RouteDecision, RoutingMode


class OrchestratorDecisionService:
    """
    Central routing brain for AuroraOS.
    
    Decides how to route conversations based on:
    - Customer value (coins spent, VIP tier)
    - Risk score
    - Time of day
    - Performer availability
    - Conversation history
    """
    
    # Time ranges for different routing strategies
    NIGHT_HOURS = (2, 6)  # 02:00 - 06:00 → AI heavy
    
    # Thresholds
    HIGH_VALUE_RISK_SCORE = 0.7
    MEDIUM_VALUE_RISK_SCORE = 0.4
    HIGH_SPENDER_COINS = 500
    VIP_TIERS = ("gold", "platinum")
    
    def decide_route(
        self,
        *,
        conversation: dict,
        customer_risk_score: float = 0.0,
    ) -> RouteDecision:
        """
        Main routing decision logic.
        
        Args:
            conversation: FlirtMarket conversation object
            customer_risk_score: 0.0-1.0 score (higher = more valuable)
        
        Returns:
            RouteDecision with mode and reason
        """
        conv_id = conversation.get("id", "unknown")
        performer = conversation.get("performer", {})
        customer = conversation.get("customer", {})
        
        performer_id = performer.get("id", "default")
        customer_tier = customer.get("tier", "none")
        coins_spent = customer.get("coins_spent", 0)
        
        # Get current hour for time-based routing
        current_hour = datetime.now().hour
        is_night = self.NIGHT_HOURS[0] <= current_hour <= self.NIGHT_HOURS[1]
        
        # Decision logic
        mode, reason, priority = self._evaluate_routing(
            customer_risk_score=customer_risk_score,
            customer_tier=customer_tier,
            coins_spent=coins_spent,
            is_night=is_night,
            performer=performer,
        )
        
        return RouteDecision(
            conversation_id=conv_id,
            target_performer_id=performer_id,
            routing_mode=mode,
            reason=reason,
            priority=priority,
            suggested_agent_id=self._get_suggested_agent(performer),
        )
    
    def _evaluate_routing(
        self,
        customer_risk_score: float,
        customer_tier: str,
        coins_spent: int,
        is_night: bool,
        performer: dict,
    ) -> tuple[RoutingMode, str, str]:
        """
        Evaluate routing based on multiple factors.
        
        Returns: (mode, reason, priority)
        """
        
        # Rule 1: High value customers → Human involvement
        if customer_risk_score >= self.HIGH_VALUE_RISK_SCORE:
            return (
                RoutingMode.HUMAN_ONLY,
                f"High value customer (risk_score={customer_risk_score:.2f})",
                "VIP",
            )
        
        # Rule 2: VIP tier customers → Hybrid (AI draft, human approve)
        if customer_tier in self.VIP_TIERS:
            return (
                RoutingMode.HYBRID,
                f"VIP tier customer ({customer_tier})",
                "VIP",
            )
        
        # Rule 3: High spenders → Hybrid
        if coins_spent >= self.HIGH_SPENDER_COINS:
            return (
                RoutingMode.HYBRID,
                f"High spender ({coins_spent} coins)",
                "HIGH",
            )
        
        # Rule 4: Night hours → AI only (operators sleeping)
        if is_night:
            return (
                RoutingMode.AI_ONLY,
                "Night hours, AI handling",
                "NORMAL",
            )
        
        # Rule 5: Medium value → Hybrid
        if customer_risk_score >= self.MEDIUM_VALUE_RISK_SCORE:
            return (
                RoutingMode.HYBRID,
                f"Medium value customer (risk_score={customer_risk_score:.2f})",
                "HIGH",
            )
        
        # Default: AI handles with hybrid fallback
        return (
            RoutingMode.HYBRID,
            "Default hybrid routing",
            "NORMAL",
        )
    
    def _get_suggested_agent(self, performer: dict) -> Optional[str]:
        """Get the suggested AI agent ID for this performer."""
        # Map performer to agent
        performer_id = performer.get("id", "")
        
        # Default mapping
        agent_mapping = {
            "betelle": "betelle_fox_v1",
            "lara": "lara_main_v1",
        }
        
        for key, agent_id in agent_mapping.items():
            if key in performer_id.lower():
                return agent_id
        
        return "betelle_fox_v1"  # Default agent


# Singleton instance
orchestrator_decision = OrchestratorDecisionService()

