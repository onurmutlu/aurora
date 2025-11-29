"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Core Models                            ║
║   "The brain that routes conversations"                          ║
║                                                                  ║
║   Operators + PerformerSlots + Conversations + Messages          ║
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

class ConversationMode(str, Enum):
    """How the conversation is handled."""
    AI_ONLY = "AI_ONLY"           # Full autonomous AI
    HUMAN_ONLY = "HUMAN_ONLY"     # Operator takes over completely
    HYBRID_GHOST = "HYBRID_GHOST" # AI drafts, operator approves/edits


class ConversationPriority(str, Enum):
    """Priority level for operator attention."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    VIP = "VIP"


class ConversationOrigin(str, Enum):
    """Where the conversation originated."""
    FLIRTMARKET = "FLIRTMARKET"
    TELEGRAM = "TELEGRAM"
    WEB = "WEB"
    ONLYVIPS = "ONLYVIPS"


# ═══════════════════════════════════════════════════════════════════
# OPERATOR — Human operator (Betül, etc.)
# ═══════════════════════════════════════════════════════════════════

class Operator(SQLModel, table=True):
    """Human operator who can take over or ghost-write conversations."""
    __tablename__ = "operators"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    external_id: Optional[str] = Field(default=None, index=True, unique=True)
    max_concurrent_chats: int = Field(default=10)
    is_online: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="operator")


# ═══════════════════════════════════════════════════════════════════
# PERFORMER SLOT — AI persona slot (Betelle Fox #1, etc.)
# ═══════════════════════════════════════════════════════════════════

class PerformerSlot(SQLModel, table=True):
    """A slot for an AI performer persona."""
    __tablename__ = "performer_slots"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = Field(index=True)  # "Betelle Fox #1", "Lara Main"
    agent_id: str = Field(index=True)  # "betelle_fox_v1" (Aurora Agent ID)
    human_performer_id: Optional[int] = Field(default=None, index=True)
    is_active: bool = Field(default=True)
    
    # Agent config
    provider: str = Field(default="grok")  # "grok" | "openai"
    model: str = Field(default="grok-3-latest")
    system_prompt: Optional[str] = None
    temperature: float = Field(default=0.8)
    max_tokens: int = Field(default=200)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="performer_slot")


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION — Active chat session
# ═══════════════════════════════════════════════════════════════════

class Conversation(SQLModel, table=True):
    """An active conversation between a user and performer."""
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Participants
    user_id: int = Field(index=True)  # Internal Aurora user ID
    external_user_id: str = Field(index=True)  # "fm_123", "tg_456"
    performer_slot_id: int = Field(foreign_key="performer_slots.id", index=True)
    agent_id: str = Field(index=True)
    operator_id: Optional[int] = Field(default=None, foreign_key="operators.id", index=True)
    
    # State
    mode: ConversationMode = Field(default=ConversationMode.AI_ONLY)
    priority: ConversationPriority = Field(default=ConversationPriority.NORMAL)
    origin: ConversationOrigin = Field(default=ConversationOrigin.FLIRTMARKET)
    
    # Metrics
    message_count: int = Field(default=0)
    coins_spent: int = Field(default=0)
    
    # Status
    is_active: bool = Field(default=True)
    last_message_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    performer_slot: Optional[PerformerSlot] = Relationship(back_populates="conversations")
    operator: Optional[Operator] = Relationship(back_populates="conversations")
    messages: List["ConversationMessage"] = Relationship(back_populates="conversation")


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION MESSAGE — Individual message
# ═══════════════════════════════════════════════════════════════════

class ConversationMessage(SQLModel, table=True):
    """A single message in a conversation."""
    __tablename__ = "conversation_messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    
    # Content
    sender: str = Field(index=True)  # "user" | "agent" | "operator"
    text: str
    source: str  # "flirtmarket" | "telegram" | "web"
    
    # For hybrid mode - operator can edit agent drafts
    is_draft: bool = Field(default=False)
    original_text: Optional[str] = None  # Agent's original before edit
    edited_by_operator: bool = Field(default=False)
    
    # Metadata
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# ═══════════════════════════════════════════════════════════════════
# USER MAPPING — External user ID to internal
# ═══════════════════════════════════════════════════════════════════

class UserMapping(SQLModel, table=True):
    """Maps external user IDs (fm_123, tg_456) to internal Aurora user IDs."""
    __tablename__ = "user_mappings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    origin: ConversationOrigin = Field(index=True)
    external_user_id: str = Field(index=True)
    internal_user_id: int = Field(index=True)
    
    # User info cache
    display_name: Optional[str] = None
    vip_tier: str = Field(default="none")  # none, silver, gold, platinum
    total_coins_spent: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

