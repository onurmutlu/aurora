"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — User Mapping Service                   ║
║   Maps external user IDs to internal Aurora user IDs             ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from sqlmodel import Session, select

from ..models import UserMapping, ConversationOrigin


def map_external_user_to_internal(
    session: Session,
    origin: ConversationOrigin,
    external_user_id: str,
) -> int:
    """
    Get or create internal user ID for an external user.
    
    External IDs look like:
    - FlirtMarket: "fm_12345"
    - Telegram: "tg_987654321"
    - Web: "web_abc123"
    
    Returns internal Aurora user ID (auto-incremented).
    """
    
    # Try to find existing mapping
    stmt = select(UserMapping).where(
        UserMapping.origin == origin,
        UserMapping.external_user_id == external_user_id,
    )
    mapping = session.exec(stmt).first()
    
    if mapping:
        return mapping.internal_user_id
    
    # Create new mapping
    # Internal user ID is just auto-increment from the mapping table
    # In production, this might link to a proper User table
    
    # Get max internal_user_id
    max_stmt = select(UserMapping).order_by(UserMapping.internal_user_id.desc()).limit(1)
    last_mapping = session.exec(max_stmt).first()
    new_internal_id = (last_mapping.internal_user_id + 1) if last_mapping else 1
    
    new_mapping = UserMapping(
        origin=origin,
        external_user_id=external_user_id,
        internal_user_id=new_internal_id,
    )
    
    session.add(new_mapping)
    session.commit()
    session.refresh(new_mapping)
    
    return new_mapping.internal_user_id


def update_user_stats(
    session: Session,
    origin: ConversationOrigin,
    external_user_id: str,
    coins_spent: int = 0,
    vip_tier: str = None,
    display_name: str = None,
) -> None:
    """Update cached user stats in the mapping."""
    
    stmt = select(UserMapping).where(
        UserMapping.origin == origin,
        UserMapping.external_user_id == external_user_id,
    )
    mapping = session.exec(stmt).first()
    
    if not mapping:
        return
    
    if coins_spent > 0:
        mapping.total_coins_spent += coins_spent
    
    if vip_tier:
        mapping.vip_tier = vip_tier
    
    if display_name:
        mapping.display_name = display_name
    
    session.add(mapping)
    session.commit()


def get_user_info(
    session: Session,
    origin: ConversationOrigin,
    external_user_id: str,
) -> dict:
    """Get cached user info from mapping."""
    
    stmt = select(UserMapping).where(
        UserMapping.origin == origin,
        UserMapping.external_user_id == external_user_id,
    )
    mapping = session.exec(stmt).first()
    
    if not mapping:
        return {
            "internal_user_id": None,
            "display_name": None,
            "vip_tier": "none",
            "total_coins_spent": 0,
        }
    
    return {
        "internal_user_id": mapping.internal_user_id,
        "display_name": mapping.display_name,
        "vip_tier": mapping.vip_tier,
        "total_coins_spent": mapping.total_coins_spent,
    }

