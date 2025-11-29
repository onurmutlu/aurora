"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Routing Service                        ║
║   Decides: AI_ONLY vs HUMAN_ONLY vs HYBRID_GHOST                 ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass
from typing import Optional

from ..models import ConversationMode, ConversationPriority


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    mode: ConversationMode
    operator_id: Optional[int]
    priority: ConversationPriority


def decide_routing(
    coins_spent_total: int,
    vip_tier: str,
    operator_online: bool,
    current_mode: ConversationMode,
    message_count: int = 0,
) -> RoutingDecision:
    """
    Decide how to route a conversation.
    
    Rules (v1 - simple):
    1. VIP (gold/platinum) or big spender (>500 coins) → HYBRID if operator online
    2. Medium spender (50-500 coins) → AI_ONLY but HIGH priority
    3. Low spender (<50 coins) → AI_ONLY, NORMAL priority
    4. If already HUMAN_ONLY, stay HUMAN_ONLY
    
    Future enhancements:
    - Time of day (operator availability)
    - Conversation sentiment
    - User complaint history
    - Operator load balancing
    """
    
    # If currently HUMAN_ONLY, operator keeps control
    if current_mode == ConversationMode.HUMAN_ONLY:
        return RoutingDecision(
            mode=ConversationMode.HUMAN_ONLY,
            operator_id=1,  # TODO: actual operator assignment
            priority=ConversationPriority.VIP,
        )
    
    # VIP users or big spenders
    if vip_tier in ("gold", "platinum") or coins_spent_total > 500:
        if operator_online:
            return RoutingDecision(
                mode=ConversationMode.HYBRID_GHOST,
                operator_id=1,  # TODO: load balance
                priority=ConversationPriority.VIP,
            )
        else:
            return RoutingDecision(
                mode=ConversationMode.AI_ONLY,
                operator_id=None,
                priority=ConversationPriority.VIP,
            )
    
    # Medium spenders - AI handles but flagged for attention
    if coins_spent_total >= 50:
        return RoutingDecision(
            mode=ConversationMode.AI_ONLY,
            operator_id=None,
            priority=ConversationPriority.HIGH,
        )
    
    # Low spenders - full AI
    return RoutingDecision(
        mode=ConversationMode.AI_ONLY,
        operator_id=None,
        priority=ConversationPriority.NORMAL,
    )


def should_escalate_to_human(
    message_text: str,
    sentiment_score: float = 0.0,
    complaint_keywords: list[str] = None,
) -> bool:
    """
    Check if message should trigger human escalation.
    
    Triggers:
    - Angry/upset sentiment
    - Complaint keywords
    - Payment issues mentioned
    - "Talk to real person" requests
    """
    complaint_keywords = complaint_keywords or [
        "gerçek kişi",
        "real person",
        "şikayet",
        "complaint",
        "para iade",
        "refund",
        "dolandırıcı",
        "scam",
        "bot musun",
        "are you a bot",
    ]
    
    text_lower = message_text.lower()
    
    for keyword in complaint_keywords:
        if keyword in text_lower:
            return True
    
    # Negative sentiment threshold
    if sentiment_score < -0.5:
        return True
    
    return False

