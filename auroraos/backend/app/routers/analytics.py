"""
╔══════════════════════════════════════════════════════════════════╗
║   Aurora Analytics — Betül Decision Insights                     ║
║   "Her decisions shape the intelligence."                        ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import Optional

from ..deps import get_db
from .. import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    """
    Get Betül's decision analytics summary.
    
    Returns:
    - decision_counts: approve/reject/edit counts
    - vibe_decision_counts: decisions per vibe mode
    - strong_feedback: "Bu çok ben" / "Bu asla ben değil" counts
    - rating_distribution: rating breakdown
    """
    
    # Decision counts (approve, reject, edit, reschedule)
    decision_counts = db.exec(
        select(models.Decision.decision, func.count(models.Decision.id))
        .group_by(models.Decision.decision)
    ).all()
    
    # Vibe mode + decision breakdown
    vibe_decision_counts = db.exec(
        select(
            models.Decision.vibe_mode_before,
            models.Decision.decision,
            func.count(models.Decision.id),
        )
        .group_by(models.Decision.vibe_mode_before, models.Decision.decision)
    ).all()
    
    # Strong feedback signals
    strong_counts = db.exec(
        select(models.Decision.feedback_type, func.count(models.Decision.id))
        .where(models.Decision.feedback_type.in_(["strong_positive", "strong_negative"]))
        .group_by(models.Decision.feedback_type)
    ).all()
    
    # Rating distribution
    rating_counts = db.exec(
        select(models.Decision.rating, func.count(models.Decision.id))
        .where(models.Decision.rating.isnot(None))
        .group_by(models.Decision.rating)
    ).all()
    
    # Total decisions
    total_decisions = db.exec(
        select(func.count(models.Decision.id))
    ).one()
    
    # Total content items
    total_content = db.exec(
        select(func.count(models.ContentItem.id))
    ).one()
    
    return {
        "total_decisions": total_decisions,
        "total_content": total_content,
        "decision_counts": [
            {"decision": d, "count": c} for d, c in decision_counts
        ],
        "vibe_decision_counts": [
            {"vibe_mode": vm, "decision": d, "count": c}
            for vm, d, c in vibe_decision_counts
        ],
        "strong_feedback": [
            {"feedback_type": f, "count": c} for f, c in strong_counts
        ],
        "rating_distribution": [
            {"rating": r, "count": c} for r, c in rating_counts if r
        ],
    }


@router.get("/vibe-performance")
def vibe_performance(db: Session = Depends(get_db)):
    """
    Get performance metrics per vibe mode.
    Shows which vibe modes Betül prefers.
    """
    
    # Approval rate per vibe mode
    vibe_stats = {}
    
    vibe_modes = ["soft_femme", "sweet_sarcasm_plus", "femme_fatale_hd"]
    
    for vibe in vibe_modes:
        approvals = db.exec(
            select(func.count(models.Decision.id))
            .where(
                models.Decision.vibe_mode_before == vibe,
                models.Decision.decision == "approve"
            )
        ).one()
        
        rejections = db.exec(
            select(func.count(models.Decision.id))
            .where(
                models.Decision.vibe_mode_before == vibe,
                models.Decision.decision == "reject"
            )
        ).one()
        
        strong_pos = db.exec(
            select(func.count(models.Decision.id))
            .where(
                models.Decision.vibe_mode_before == vibe,
                models.Decision.feedback_type == "strong_positive"
            )
        ).one()
        
        strong_neg = db.exec(
            select(func.count(models.Decision.id))
            .where(
                models.Decision.vibe_mode_before == vibe,
                models.Decision.feedback_type == "strong_negative"
            )
        ).one()
        
        total = approvals + rejections
        approval_rate = (approvals / total * 100) if total > 0 else 0
        
        vibe_stats[vibe] = {
            "approvals": approvals,
            "rejections": rejections,
            "total": total,
            "approval_rate": round(approval_rate, 1),
            "strong_positive": strong_pos,
            "strong_negative": strong_neg,
        }
    
    return {
        "vibe_performance": vibe_stats,
        "best_vibe": max(vibe_stats.items(), key=lambda x: x[1]["approval_rate"])[0] if any(v["total"] > 0 for v in vibe_stats.values()) else None,
    }


@router.get("/recent")
def recent_decisions(db: Session = Depends(get_db), limit: int = 10):
    """
    Get recent decisions for activity feed.
    """
    
    decisions = db.exec(
        select(models.Decision)
        .order_by(models.Decision.created_at.desc())
        .limit(limit)
    ).all()
    
    return {
        "recent": [
            {
                "id": d.id,
                "decision": d.decision,
                "feedback_type": d.feedback_type,
                "rating": d.rating,
                "vibe_mode": d.vibe_mode_before,
                "text_preview": (d.old_text or "")[:50] + "..." if d.old_text and len(d.old_text) > 50 else d.old_text,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in decisions
        ]
    }

