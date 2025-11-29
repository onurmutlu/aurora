"""
╔══════════════════════════════════════════════════════════════════╗
║   Sprint 005: Aurora Memory — DM Conversation Logging            ║
║   "She remembers every conversation."                            ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional

from ..deps import get_db
from .. import models


router = APIRouter(prefix="/dm", tags=["dm"])


# ═══════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════

class DMLogPayload(BaseModel):
    """Payload for logging a DM message."""
    channel: str  # telegram / sugoda / instagram
    external_user_id: str  # karşı tarafın ID'si
    direction: str  # incoming / outgoing
    text: str
    vibe_mode: Optional[str] = None  # outgoing ise hangi vibe seçildi


class DMContextRequest(BaseModel):
    """Request for getting DM conversation context."""
    channel: str
    external_user_id: str
    limit: int = 10


# ═══════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.post("/log")
def log_dm(payload: DMLogPayload, db: Session = Depends(get_db)):
    """
    Log a DM message for context-aware replies.
    
    Bot calls this for both incoming and outgoing messages.
    This builds the conversation history that Aurora uses
    to generate more contextual replies.
    """
    msg = models.DMMessage(
        channel=payload.channel,
        external_user_id=payload.external_user_id,
        direction=payload.direction,
        text=payload.text,
        vibe_mode=payload.vibe_mode,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    return {
        "ok": True,
        "id": msg.id,
        "direction": msg.direction,
    }


@router.post("/context")
def get_context(body: DMContextRequest, db: Session = Depends(get_db)):
    """
    Get conversation context for a specific user.
    
    Returns the last N messages between Betül and this user,
    which Aurora uses to generate context-aware replies.
    """
    stmt = (
        select(models.DMMessage)
        .where(
            models.DMMessage.channel == body.channel,
            models.DMMessage.external_user_id == body.external_user_id,
        )
        .order_by(models.DMMessage.created_at.desc())
        .limit(body.limit)
    )
    
    messages = list(reversed(db.exec(stmt).all()))
    
    return {
        "channel": body.channel,
        "external_user_id": body.external_user_id,
        "message_count": len(messages),
        "messages": [
            {
                "direction": m.direction,
                "text": m.text,
                "vibe_mode": m.vibe_mode,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


@router.get("/stats")
def dm_stats(db: Session = Depends(get_db)):
    """
    Get DM memory statistics.
    """
    total = db.exec(select(models.DMMessage)).all()
    incoming = [m for m in total if m.direction == "incoming"]
    outgoing = [m for m in total if m.direction == "outgoing"]
    
    # Unique conversations
    unique_users = set((m.channel, m.external_user_id) for m in total)
    
    return {
        "total_messages": len(total),
        "incoming": len(incoming),
        "outgoing": len(outgoing),
        "unique_conversations": len(unique_users),
    }

