# backend/app/routers/content.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from ..deps import get_db
from .. import models, schemas

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/pending", response_model=List[schemas.ContentItemWithVariants])
def get_pending_content(db: Session = Depends(get_db)):
    stmt = (
        select(models.ContentItem)
        .where(models.ContentItem.status == "pending_decision")
        .order_by(models.ContentItem.created_at.desc())
    )
    items = db.exec(stmt).all()
    return items


@router.get("/approved", response_model=List[schemas.ContentItemWithVariants])
def get_approved_content(db: Session = Depends(get_db), limit: int = 20):
    """
    Get approved content items (Content Wall).
    These are the contents Betül approved for use.
    """
    stmt = (
        select(models.ContentItem)
        .where(models.ContentItem.status == "approved")
        .order_by(models.ContentItem.created_at.desc())
        .limit(limit)
    )
    items = db.exec(stmt).all()
    return items


@router.get("/wall")
def get_content_wall(db: Session = Depends(get_db), limit: int = 20):
    """
    Get content wall with selected variant text for each approved item.
    Returns ready-to-use content for Instagram/Sugoda.
    """
    stmt = (
        select(models.ContentItem)
        .where(models.ContentItem.status == "approved")
        .order_by(models.ContentItem.created_at.desc())
        .limit(limit)
    )
    items = db.exec(stmt).all()
    
    wall = []
    for item in items:
        # Find the variant that was selected/approved
        # Check decisions to find which variant text was used
        decision_stmt = (
            select(models.Decision)
            .where(models.Decision.content_item_id == item.id)
            .where(models.Decision.decision == "approve")
            .order_by(models.Decision.created_at.desc())
        )
        decision = db.exec(decision_stmt).first()
        
        selected_text = None
        selected_vibe = None
        
        if decision and decision.new_text:
            selected_text = decision.new_text
            selected_vibe = decision.vibe_mode_after
        elif item.variants:
            # Fallback to first variant
            selected_text = item.variants[0].text
            selected_vibe = item.variants[0].vibe_mode
        
        if selected_text:
            wall.append({
                "id": item.id,
                "type": item.type,
                "target_channel": item.target_channel,
                "text": selected_text,
                "vibe_mode": selected_vibe,
                "created_at": item.created_at.isoformat(),
            })
    
    return {"items": wall, "count": len(wall)}


@router.post("/{content_id}/decision")
def decide_content(
    content_id: int,
    payload: schemas.DecisionCreate,
    db: Session = Depends(get_db),
):
    content = db.get(models.ContentItem, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    decision = models.Decision(
        content_item_id=content.id,
        user="BETUL",  # şimdilik hard-coded, sonra auth bağlarız
        decision=payload.decision,
        feedback_type=payload.feedback_type,
        rating=payload.rating,
        old_text=payload.old_text,
        new_text=payload.new_text,
        vibe_mode_before=payload.vibe_mode_before,
        vibe_mode_after=payload.vibe_mode_after,
    )
    db.add(decision)

    # basic state changes
    if payload.decision == "approve":
        content.status = "approved"
    elif payload.decision == "reject":
        content.status = "rejected"
    elif payload.decision == "edit":
        content.status = "approved"
    elif payload.decision == "reschedule":
        content.status = "scheduled"

    db.add(content)
    db.commit()
    db.refresh(content)

    # burda ileride aurora-engine'e feedback event'i atarız (queue vs.)

    return {"ok": True, "content_id": content.id, "new_status": content.status}

