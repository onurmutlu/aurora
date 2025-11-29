# backend/app/schemas.py
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ContentVariantBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vibe_mode: str
    text: str
    meta: Optional[str] = None


class ContentItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    target_channel: str
    status: str
    scheduled_at: Optional[datetime]
    created_by: str
    created_at: datetime
    selected_variant_id: Optional[int]


class ContentItemWithVariants(ContentItemBase):
    variants: List[ContentVariantBase]


class DecisionCreate(BaseModel):
    decision: str  # approve / reject / edit / reschedule
    feedback_type: Optional[str] = None
    rating: Optional[int] = None
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    vibe_mode_before: Optional[str] = None
    vibe_mode_after: Optional[str] = None


class VibeUpdate(BaseModel):
    current_mode: str
    energy_level: int = 50
    note: Optional[str] = None


class AIGenerateRequest(BaseModel):
    type: str = "post"
    target_channel: str = "instagram"
    count: int = 1
    scenario: Optional[str] = None  # red_dress, street, gym vs.


# ═══════════════════════════════════════════════════════════════════
# Sprint 004: DM Reply & Sugoda Script
# ═══════════════════════════════════════════════════════════════════

class ReplyRequest(BaseModel):
    """DM reply suggestion request."""
    channel: str = "telegram"  # telegram / sugoda / instagram_dm
    incoming_text: str
    context: Optional[str] = None  # first_message, late_night, flirty, etc.


class SugodaScriptRequest(BaseModel):
    """Sugoda live stream script request."""
    theme: str  # "gece yayını, slow, lo-fi"
    length: str = "short"  # short / medium


# ═══════════════════════════════════════════════════════════════════
# Sprint 006: AuroraOS Story Mode / Timeline
# ═══════════════════════════════════════════════════════════════════

class DayEventCreate(BaseModel):
    """Create a new day event."""
    date: Optional[date] = None  # None = today
    tag: str  # walk, starbucks, sugoda, dm, work, low_energy
    description: str
    energy: Optional[int] = None  # 0-100
    mood: Optional[str] = None    # calm, anxious, sigma, tired, happy


class DayEventOut(BaseModel):
    """Day event output."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    time: datetime
    tag: str
    description: str
    energy: Optional[int]
    mood: Optional[str]


class DayTimeline(BaseModel):
    """Full timeline for a single day."""
    date: date
    title: Optional[str]
    note: Optional[str]
    events: List[DayEventOut]


class DaySummaryRequest(BaseModel):
    """Request for AI-generated day summary."""
    date: Optional[date] = None  # None = today


class DaySummaryResponse(BaseModel):
    """AI-generated day summary response."""
    vibe_summary: str
    what_happened: str
    evening_suggestion: str
    energy_advice: str

