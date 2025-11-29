"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS State Module — Database Models                        ║
║   Government data: Citizens, Treasury, AI Operations             ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


# ═══════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════

class CitizenStatus(str, Enum):
    """Citizen verification status."""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"


class CitizenTier(str, Enum):
    """Citizen tier/rank."""
    BASIC = "BASIC"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    FOUNDER = "FOUNDER"


class AIOperationType(str, Enum):
    """Type of AI operation."""
    CALL = "CALL"           # AI phone call
    JUDGE = "JUDGE"         # Moderation judgment
    GENERATE = "GENERATE"   # Content generation
    ANALYZE = "ANALYZE"     # Data analysis
    REPLY = "REPLY"         # Auto-reply


class AIOperationStatus(str, Enum):
    """Status of AI operation."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TransactionType(str, Enum):
    """Treasury transaction type."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    REWARD = "REWARD"
    PENALTY = "PENALTY"
    FEE = "FEE"


class FlagType(str, Enum):
    """Content flag type."""
    SPAM = "SPAM"
    ABUSE = "ABUSE"
    NSFW = "NSFW"
    FRAUD = "FRAUD"
    HARASSMENT = "HARASSMENT"
    OTHER = "OTHER"


# ═══════════════════════════════════════════════════════════════════
# CITIZEN — User/Member model
# ═══════════════════════════════════════════════════════════════════

class Citizen(SQLModel, table=True):
    """
    A citizen of the AuroraOS nation.
    Represents a user/member in the system.
    """
    __tablename__ = "citizens"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    citizen_id: str = Field(unique=True, index=True)  # "CZ-12345"
    
    # Identity
    display_name: str = Field(index=True)
    email: Optional[str] = Field(default=None, index=True)
    phone: Optional[str] = None
    telegram_id: Optional[str] = Field(default=None, index=True)
    
    # Status
    status: CitizenStatus = Field(default=CitizenStatus.PENDING)
    tier: CitizenTier = Field(default=CitizenTier.BASIC)
    is_online: bool = Field(default=False)
    
    # Economy
    balance: float = Field(default=0.0)
    total_earned: float = Field(default=0.0)
    total_spent: float = Field(default=0.0)
    
    # Activity
    last_seen: Optional[datetime] = None
    login_count: int = Field(default=0)
    message_count: int = Field(default=0)
    
    # Metadata
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    banned_at: Optional[datetime] = None
    ban_reason: Optional[str] = None
    
    # Relations
    flags: List["ContentFlag"] = Relationship(back_populates="citizen")
    transactions: List["TreasuryTransaction"] = Relationship(back_populates="citizen")


# ═══════════════════════════════════════════════════════════════════
# TREASURY — Economic transactions
# ═══════════════════════════════════════════════════════════════════

class TreasuryTransaction(SQLModel, table=True):
    """A financial transaction in the treasury."""
    __tablename__ = "treasury_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)  # "TX-20231129-001"
    
    # Type and amount
    type: TransactionType
    amount: float
    currency: str = Field(default="NCR")  # Nova Credit
    
    # Parties
    citizen_id: Optional[int] = Field(default=None, foreign_key="citizens.id")
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    
    # Details
    description: str
    reference: Optional[str] = None  # External reference
    
    # Status
    status: str = Field(default="COMPLETED")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # Relations
    citizen: Optional[Citizen] = Relationship(back_populates="transactions")


class TreasurySnapshot(SQLModel, table=True):
    """Daily treasury snapshot for historical data."""
    __tablename__ = "treasury_snapshots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(index=True)
    
    # Reserves
    total_reserve: float
    liquid_reserve: float
    locked_reserve: float
    
    # Metrics
    gdp_24h: float  # Total transaction volume
    gdp_growth: float  # Percentage change
    inflation_rate: float
    
    # Activity
    transaction_count: int
    active_citizens: int
    new_citizens: int
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════
# AI OPERATIONS — AI activity logs
# ═══════════════════════════════════════════════════════════════════

class AIOperation(SQLModel, table=True):
    """Log of AI operations (calls, judgments, etc.)."""
    __tablename__ = "ai_operations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    operation_id: str = Field(unique=True, index=True)  # "OP-20231129-001"
    
    # Operation details
    type: AIOperationType
    status: AIOperationStatus = Field(default=AIOperationStatus.PENDING)
    
    # Target
    target: str  # Phone number, user ID, etc.
    target_type: str = Field(default="unknown")  # "phone", "user", "content"
    
    # Execution
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Results
    result: Optional[str] = None
    sentiment: Optional[str] = None  # "POSITIVE", "NEUTRAL", "NEGATIVE"
    confidence: Optional[float] = None  # 0.0 - 1.0
    
    # AI details
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # System or operator ID


# ═══════════════════════════════════════════════════════════════════
# CONTENT FLAGS — Moderation queue
# ═══════════════════════════════════════════════════════════════════

class ContentFlag(SQLModel, table=True):
    """Flagged content for moderation."""
    __tablename__ = "content_flags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    flag_id: str = Field(unique=True, index=True)  # "FL-20231129-001"
    
    # Flag details
    type: FlagType
    severity: int = Field(default=1)  # 1-5
    
    # Content
    content_type: str  # "message", "profile", "image"
    content_id: str
    content_preview: Optional[str] = None
    
    # Reporter
    citizen_id: Optional[int] = Field(default=None, foreign_key="citizens.id")
    reporter_type: str = Field(default="user")  # "user", "ai", "system"
    
    # Resolution
    status: str = Field(default="PENDING")  # PENDING, REVIEWING, RESOLVED, DISMISSED
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relations
    citizen: Optional[Citizen] = Relationship(back_populates="flags")


# ═══════════════════════════════════════════════════════════════════
# THREAT LEVEL — System security status
# ═══════════════════════════════════════════════════════════════════

class ThreatLog(SQLModel, table=True):
    """Security threat logs."""
    __tablename__ = "threat_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Threat details
    level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    type: str  # "cyber_attack", "fraud", "abuse", "system"
    
    # Description
    title: str
    description: str
    source_ip: Optional[str] = None
    
    # Status
    status: str = Field(default="ACTIVE")  # ACTIVE, MITIGATED, RESOLVED
    mitigated_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

