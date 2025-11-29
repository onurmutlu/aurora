"""
╔══════════════════════════════════════════════════════════════════╗
║   Sprint 006: AuroraOS Story Mode / Timeline                     ║
║   "What did I do today? What should I do tonight?"               ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime, date as date_type
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional

from ..deps import get_db
from .. import models, schemas


router = APIRouter(prefix="/day", tags=["day"])


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def get_or_create_day(db: Session, d: date_type) -> models.DayLog:
    """Get existing day log or create a new one."""
    stmt = select(models.DayLog).where(models.DayLog.log_date == d)
    day = db.exec(stmt).first()
    if day:
        return day
    
    day = models.DayLog(log_date=d)
    db.add(day)
    db.commit()
    db.refresh(day)
    return day


def get_day_events(db: Session, day_id: int) -> list[models.DayEvent]:
    """Get all events for a day, ordered by time."""
    stmt = (
        select(models.DayEvent)
        .where(models.DayEvent.day_id == day_id)
        .order_by(models.DayEvent.time)
    )
    return list(db.exec(stmt).all())


# ═══════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.post("/event", response_model=schemas.DayTimeline)
def add_event(
    payload: schemas.DayEventCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new event to today's (or specified date's) timeline.
    
    Example tags:
    - walk, gym, yoga (exercise)
    - starbucks, coffee, lunch (social/food)
    - sugoda, dm, work (activities)
    - low_energy, tired, anxious (states)
    - happy, sigma, calm (moods)
    """
    d = payload.date or datetime.utcnow().date()
    day = get_or_create_day(db, d)
    
    # Create event
    ev = models.DayEvent(
        day_id=day.id,
        tag=payload.tag.lower().strip(),
        description=payload.description,
        energy=payload.energy,
        mood=payload.mood.lower().strip() if payload.mood else None,
        time=datetime.utcnow(),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    
    # Return updated timeline
    events = get_day_events(db, day.id)
    return schemas.DayTimeline(
        date=day.log_date,
        title=day.title,
        note=day.note,
        events=events,
    )


@router.get("/timeline", response_model=schemas.DayTimeline)
def get_today_timeline(db: Session = Depends(get_db)):
    """Get today's timeline."""
    d = datetime.utcnow().date()
    
    stmt = select(models.DayLog).where(models.DayLog.log_date == d)
    day = db.exec(stmt).first()
    
    if not day:
        # Return empty timeline for today
        return schemas.DayTimeline(
            date=d,
            title=None,
            note=None,
            events=[],
        )
    
    events = get_day_events(db, day.id)
    return schemas.DayTimeline(
        date=day.log_date,
        title=day.title,
        note=day.note,
        events=events,
    )


@router.get("/timeline/{d}", response_model=schemas.DayTimeline)
def get_timeline_by_date(
    d: date_type,
    db: Session = Depends(get_db),
):
    """Get timeline for a specific date."""
    stmt = select(models.DayLog).where(models.DayLog.log_date == d)
    day = db.exec(stmt).first()
    
    if not day:
        raise HTTPException(status_code=404, detail=f"No day log for {d}")
    
    events = get_day_events(db, day.id)
    return schemas.DayTimeline(
        date=day.log_date,
        title=day.title,
        note=day.note,
        events=events,
    )


@router.patch("/title")
def update_day_title(
    title: str,
    note: Optional[str] = None,
    d: Optional[date_type] = None,
    db: Session = Depends(get_db),
):
    """
    Update today's (or specified date's) title and note.
    
    Example titles:
    - "Kutsal Cuma"
    - "Sugoda gecesi"
    - "Gym day 💪"
    """
    target_date = d or datetime.utcnow().date()
    day = get_or_create_day(db, target_date)
    
    day.title = title
    if note is not None:
        day.note = note
    
    db.add(day)
    db.commit()
    db.refresh(day)
    
    return {
        "ok": True,
        "date": day.log_date.isoformat(),
        "title": day.title,
        "note": day.note,
    }


@router.get("/stats")
def day_stats(db: Session = Depends(get_db)):
    """Get Story Mode statistics."""
    days = list(db.exec(select(models.DayLog)).all())
    events = list(db.exec(select(models.DayEvent)).all())
    
    # Tag frequency
    tag_counts: dict[str, int] = {}
    for ev in events:
        tag_counts[ev.tag] = tag_counts.get(ev.tag, 0) + 1
    
    # Top tags
    top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:5]
    
    return {
        "total_days": len(days),
        "total_events": len(events),
        "top_tags": [{"tag": t, "count": c} for t, c in top_tags],
    }

