"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS State Module — Pydantic Schemas                       ║
║   Request/Response DTOs for State API                            ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from .models import (
    CitizenStatus,
    CitizenTier,
    AIOperationType,
    AIOperationStatus,
    TransactionType,
    FlagType,
)


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD STATS — Main overview
# ═══════════════════════════════════════════════════════════════════

class CitizenStats(BaseModel):
    """Citizen population statistics."""
    total: int
    verified: int
    pending: int
    online: int
    banned: int
    new_today: int
    
    # By tier
    basic_count: int
    silver_count: int
    gold_count: int
    platinum_count: int
    founder_count: int


class TreasuryStats(BaseModel):
    """Treasury financial statistics."""
    reserve: str  # Formatted string "4,500,000 NCR"
    reserve_raw: float
    gdp_24h: str  # "+12%"
    gdp_raw: float
    inflation: str  # "-2.4%"
    inflation_raw: float
    liquidity: str  # "High", "Medium", "Low"
    
    # Additional metrics
    transactions_24h: int
    volume_24h: float
    avg_transaction: float


class ThreatStatus(BaseModel):
    """Current threat level status."""
    level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    active_threats: int
    mitigated_24h: int
    last_incident: Optional[datetime]
    details: str


class DashboardStats(BaseModel):
    """Complete dashboard statistics."""
    citizens: CitizenStats
    treasury: TreasuryStats
    threat: ThreatStatus
    ai_operations_24h: int
    flagged_content: int


# ═══════════════════════════════════════════════════════════════════
# CITIZEN API
# ═══════════════════════════════════════════════════════════════════

class CitizenCreate(BaseModel):
    """Create a new citizen."""
    display_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    tier: CitizenTier = CitizenTier.BASIC


class CitizenUpdate(BaseModel):
    """Update citizen details."""
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: Optional[CitizenTier] = None
    status: Optional[CitizenStatus] = None


class CitizenOut(BaseModel):
    """Citizen output for API."""
    id: int
    citizen_id: str
    display_name: str
    email: Optional[str]
    telegram_id: Optional[str]
    status: CitizenStatus
    tier: CitizenTier
    is_online: bool
    balance: float
    total_earned: float
    total_spent: float
    message_count: int
    joined_at: datetime
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True


class CitizenListItem(BaseModel):
    """Citizen item for list view."""
    id: int
    citizen_id: str
    display_name: str
    status: CitizenStatus
    tier: CitizenTier
    is_online: bool
    balance: float
    joined_at: datetime
    
    class Config:
        from_attributes = True


class CitizenBanRequest(BaseModel):
    """Ban a citizen."""
    reason: str
    duration_days: Optional[int] = None  # None = permanent


# ═══════════════════════════════════════════════════════════════════
# TREASURY API
# ═══════════════════════════════════════════════════════════════════

class TransactionCreate(BaseModel):
    """Create a treasury transaction."""
    type: TransactionType
    amount: float
    citizen_id: Optional[int] = None
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    description: str
    reference: Optional[str] = None


class TransactionOut(BaseModel):
    """Transaction output for API."""
    id: int
    transaction_id: str
    type: TransactionType
    amount: float
    currency: str
    citizen_id: Optional[int]
    description: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TreasuryHistory(BaseModel):
    """Historical treasury data."""
    date: datetime
    total_reserve: float
    gdp_24h: float
    gdp_growth: float
    transaction_count: int
    active_citizens: int


# ═══════════════════════════════════════════════════════════════════
# AI OPERATIONS API
# ═══════════════════════════════════════════════════════════════════

class AIOperationCreate(BaseModel):
    """Create a new AI operation."""
    type: AIOperationType
    target: str
    target_type: str = "unknown"


class AIOperationOut(BaseModel):
    """AI operation output for API."""
    id: int
    operation_id: str
    type: AIOperationType
    status: AIOperationStatus
    target: str
    target_type: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    result: Optional[str]
    sentiment: Optional[str]
    confidence: Optional[float]
    model_used: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIOperationUpdate(BaseModel):
    """Update AI operation status."""
    status: AIOperationStatus
    result: Optional[str] = None
    sentiment: Optional[str] = None
    confidence: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════
# MODERATION API
# ═══════════════════════════════════════════════════════════════════

class ContentFlagCreate(BaseModel):
    """Flag content for moderation."""
    type: FlagType
    severity: int = 1
    content_type: str
    content_id: str
    content_preview: Optional[str] = None
    citizen_id: Optional[int] = None
    reporter_type: str = "user"


class ContentFlagOut(BaseModel):
    """Content flag output for API."""
    id: int
    flag_id: str
    type: FlagType
    severity: int
    content_type: str
    content_id: str
    content_preview: Optional[str]
    status: str
    resolution: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContentFlagResolve(BaseModel):
    """Resolve a content flag."""
    status: str  # "RESOLVED", "DISMISSED"
    resolution: str

