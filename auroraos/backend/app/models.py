# backend/app/models.py
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from typing import List


class ContentVariant(SQLModel, table=True):
    __tablename__ = "content_variants"

    id: Optional[int] = Field(default=None, primary_key=True)
    content_item_id: int = Field(foreign_key="content_items.id", index=True)
    vibe_mode: str = Field(index=True)  # soft_femme, sweet_sarcasm_plus, ...
    text: str
    meta: Optional[str] = None  # JSON string: reel_script, tags vs.

    content_item: Optional["ContentItem"] = Relationship(
        back_populates="variants",
        sa_relationship_kwargs={"foreign_keys": "[ContentVariant.content_item_id]"}
    )


class ContentItem(SQLModel, table=True):
    __tablename__ = "content_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(index=True)  # post, story, dm_reply, sugoda_script
    target_channel: str = Field(index=True)  # telegram_bot, instagram, tiktok, sugoda
    status: str = Field(default="pending_decision", index=True)
    scheduled_at: Optional[datetime] = Field(default=None, index=True)
    created_by: str = Field(default="AI")  # AI / BETUL / BARON
    created_at: datetime = Field(default_factory=datetime.utcnow)

    selected_variant_id: Optional[int] = Field(default=None, foreign_key="content_variants.id")

    variants: List["ContentVariant"] = Relationship(
        back_populates="content_item",
        sa_relationship_kwargs={"foreign_keys": "[ContentVariant.content_item_id]"}
    )
    decisions: List["Decision"] = Relationship(back_populates="content_item")


class Decision(SQLModel, table=True):
    __tablename__ = "decisions"

    id: Optional[int] = Field(default=None, primary_key=True)
    content_item_id: int = Field(foreign_key="content_items.id", index=True)
    user: str = Field(default="BETUL")  # şimdilik string
    decision: str  # approve / reject / edit / reschedule
    feedback_type: Optional[str] = None  # style / tone / vibe / safety / other
    rating: Optional[int] = None  # 1-5
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    vibe_mode_before: Optional[str] = None
    vibe_mode_after: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    content_item: Optional[ContentItem] = Relationship(back_populates="decisions")


class VibeState(SQLModel, table=True):
    __tablename__ = "vibe_states"

    id: Optional[int] = Field(default=None, primary_key=True)
    user: str = Field(default="BETUL", index=True)
    current_mode: str = Field(index=True)  # soft_femme, business_girl, ...
    energy_level: int = Field(default=50)
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════
# Sprint 005: Aurora Memory — DM Message Log
# ═══════════════════════════════════════════════════════════════════

class DMMessage(SQLModel, table=True):
    """
    DM conversation memory for context-aware replies.
    Stores both incoming and outgoing messages.
    """
    __tablename__ = "dm_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    channel: str = Field(index=True)  # telegram / sugoda / instagram
    external_user_id: str = Field(index=True)  # karşı tarafın ID'si
    direction: str = Field(index=True)  # incoming / outgoing
    text: str
    vibe_mode: Optional[str] = None  # outgoing ise hangi vibe seçildi
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════
# Sprint 006: AuroraOS Story Mode / Timeline
# ═══════════════════════════════════════════════════════════════════

class DayLog(SQLModel, table=True):
    """
    Daily log — represents one day in Betül's timeline.
    Contains multiple events throughout the day.
    """
    __tablename__ = "day_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    log_date: date = Field(index=True, unique=True)
    title: Optional[str] = None  # "Kutsal Cuma", "Sugoda gecesi" vs.
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    events: List["DayEvent"] = Relationship(back_populates="day")


class DayEvent(SQLModel, table=True):
    """
    Individual event within a day.
    Tags: walk, starbucks, sugoda, dm, work, gym, low_energy, etc.
    """
    __tablename__ = "day_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    day_id: int = Field(foreign_key="day_logs.id", index=True)
    time: datetime = Field(default_factory=datetime.utcnow)
    tag: str = Field(index=True)  # walk, starbucks, sugoda, dm, work, low_energy
    description: str
    energy: Optional[int] = None  # 0–100
    mood: Optional[str] = None    # calm, anxious, sigma, tired, happy, etc.

    day: Optional[DayLog] = Relationship(back_populates="events")

