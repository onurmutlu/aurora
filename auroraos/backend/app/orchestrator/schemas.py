"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Pydantic Schemas                       ║
║   Request/Response DTOs for the orchestrator API                 ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from .models import ConversationOrigin, ConversationMode, ConversationPriority


# ═══════════════════════════════════════════════════════════════════
# INCOMING MESSAGE — From FlirtMarket / Telegram / Web
# ═══════════════════════════════════════════════════════════════════

class IncomingMeta(BaseModel):
    """Metadata about the user from the originating platform."""
    coins_spent_total: int = 0
    vip_tier: str = "none"  # none, silver, gold, platinum
    session_duration: Optional[int] = None  # seconds
    last_purchase: Optional[datetime] = None


class IncomingMessageDTO(BaseModel):
    """Payload when a user sends a message from any platform."""
    origin: ConversationOrigin
    external_user_id: str  # "fm_123", "tg_999", "web_abc"
    performer_slot_id: int
    text: str
    meta: Optional[IncomingMeta] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "FLIRTMARKET",
                "external_user_id": "fm_12345",
                "performer_slot_id": 1,
                "text": "Merhaba, nasılsın?",
                "meta": {
                    "coins_spent_total": 150,
                    "vip_tier": "silver"
                }
            }
        }


class IncomingMessageResponse(BaseModel):
    """Response after processing an incoming message."""
    conversation_id: int
    mode: ConversationMode
    reply: Optional[str] = None  # If AI_ONLY, contains the reply
    queued_for_operator: bool = False
    priority: ConversationPriority


# ═══════════════════════════════════════════════════════════════════
# OPERATOR CONSOLE — List/View/Reply
# ═══════════════════════════════════════════════════════════════════

class ConversationListItem(BaseModel):
    """Summary of a conversation for operator list view."""
    id: int
    external_user_id: str
    performer_slot_label: str
    agent_id: str
    mode: ConversationMode
    priority: ConversationPriority
    origin: ConversationOrigin
    message_count: int
    coins_spent: int
    last_message_at: Optional[datetime]
    last_message_preview: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    """A single message in conversation history."""
    id: int
    sender: str  # "user" | "agent" | "operator"
    text: str
    source: str
    is_draft: bool
    edited_by_operator: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Full conversation with messages for operator view."""
    id: int
    external_user_id: str
    performer_slot_id: int
    performer_slot_label: str
    agent_id: str
    mode: ConversationMode
    priority: ConversationPriority
    origin: ConversationOrigin
    message_count: int
    coins_spent: int
    is_active: bool
    created_at: datetime
    messages: List[MessageOut]
    
    class Config:
        from_attributes = True


class OperatorReplyRequest(BaseModel):
    """Operator sends a reply or approves/edits a draft."""
    text: str
    send_as: str = "operator"  # "operator" | "agent_style"
    edit_draft_id: Optional[int] = None  # If editing an existing draft
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Tabii ki, seninle konuşmak çok güzel 💋",
                "send_as": "agent_style"
            }
        }


class OperatorReplyResponse(BaseModel):
    """Response after operator sends a reply."""
    message_id: int
    sent: bool
    queued_for_outbound: bool


# ═══════════════════════════════════════════════════════════════════
# PERFORMER SLOT — CRUD
# ═══════════════════════════════════════════════════════════════════

class PerformerSlotCreate(BaseModel):
    """Create a new performer slot."""
    label: str
    agent_id: str
    provider: str = "grok"
    model: str = "grok-3-latest"
    system_prompt: Optional[str] = None
    temperature: float = 0.8
    max_tokens: int = 200


class PerformerSlotOut(BaseModel):
    """Performer slot output."""
    id: int
    label: str
    agent_id: str
    provider: str
    model: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════
# OPERATOR — CRUD
# ═══════════════════════════════════════════════════════════════════

class OperatorCreate(BaseModel):
    """Create a new operator."""
    name: str
    external_id: Optional[str] = None
    max_concurrent_chats: int = 10


class OperatorOut(BaseModel):
    """Operator output."""
    id: int
    name: str
    external_id: Optional[str]
    is_online: bool
    max_concurrent_chats: int
    active_chat_count: int = 0
    
    class Config:
        from_attributes = True


class OperatorStatusUpdate(BaseModel):
    """Update operator online status."""
    is_online: bool


# ═══════════════════════════════════════════════════════════════════
# ROUTING DECISION — FlirtMarket integration
# ═══════════════════════════════════════════════════════════════════

from enum import Enum


class PerformerType(str, Enum):
    """Type of performer handling the conversation."""
    AI = "AI"
    HUMAN = "HUMAN"
    HYBRID = "HYBRID"


class RoutingMode(str, Enum):
    """How messages should be routed."""
    AUTO = "AUTO"           # System decides
    HUMAN_ONLY = "HUMAN_ONLY"
    AI_ONLY = "AI_ONLY"
    HYBRID = "HYBRID"       # AI drafts, human approves


class PerformerProfile(BaseModel):
    """Performer profile for routing decisions."""
    id: str
    display_name: str
    type: PerformerType
    is_test: bool = False
    agency_id: Optional[str] = None
    ai_profile_id: Optional[str] = None
    telegram_handle: Optional[str] = None


class RouteRequest(BaseModel):
    """Request from FlirtMarket for routing decision."""
    conversation: dict
    customer_risk_score: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {
                    "id": "conv_123",
                    "performer": {"id": "perf_1", "name": "Betelle"},
                    "customer": {"id": "cust_456", "tier": "gold"}
                },
                "customer_risk_score": 0.8
            }
        }


class RouteDecision(BaseModel):
    """Routing decision returned to FlirtMarket."""
    conversation_id: str
    target_performer_id: str
    routing_mode: RoutingMode
    reason: str
    priority: str = "NORMAL"
    suggested_agent_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════
# TELEGRAM INBOUND — Real DM integration
# ═══════════════════════════════════════════════════════════════════

class TelegramInboundMessage(BaseModel):
    """Incoming message from Telegram worker."""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    message: str
    message_id: Optional[int] = None
    chat_id: Optional[int] = None
    is_reply: bool = False
    reply_to_message_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "username": "cool_user",
                "first_name": "Ahmet",
                "message": "Merhaba, nasılsın?",
                "message_id": 999
            }
        }


class TelegramInboundResponse(BaseModel):
    """Response after processing Telegram inbound message."""
    success: bool
    conversation_id: Optional[int] = None
    routing_mode: RoutingMode
    ai_reply: Optional[str] = None
    queued_for_operator: bool = False
    matched_flirtmarket_conversation: Optional[str] = None

