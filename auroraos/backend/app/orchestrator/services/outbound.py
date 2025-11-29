"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Outbound Message Service               ║
║   Queues and sends replies back to originating platforms         ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
from typing import Optional
from dataclasses import dataclass

from ..models import ConversationOrigin


@dataclass
class OutboundMessage:
    """A message to be sent to an external platform."""
    origin: ConversationOrigin
    external_user_id: str
    text: str
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════
# OUTBOUND QUEUE (In-memory for now, Redis in production)
# ═══════════════════════════════════════════════════════════════════

_outbound_queue: list[OutboundMessage] = []


def enqueue_outbound_message(
    origin: ConversationOrigin,
    external_user_id: str,
    text: str,
    conversation_id: int = None,
    message_id: int = None,
) -> bool:
    """
    Queue a message for delivery to the originating platform.
    
    In production, this would:
    1. Push to Redis/RabbitMQ queue
    2. Worker process picks up and delivers
    3. Handles retries, rate limiting, etc.
    
    For now: just add to in-memory list.
    """
    msg = OutboundMessage(
        origin=origin,
        external_user_id=external_user_id,
        text=text,
        conversation_id=conversation_id,
        message_id=message_id,
    )
    
    _outbound_queue.append(msg)
    print(f"[Outbound] Queued message to {origin.value}:{external_user_id}")
    
    return True


def get_pending_outbound(origin: ConversationOrigin = None) -> list[OutboundMessage]:
    """Get pending outbound messages, optionally filtered by origin."""
    if origin:
        return [m for m in _outbound_queue if m.origin == origin]
    return _outbound_queue.copy()


def pop_outbound_message(origin: ConversationOrigin, external_user_id: str) -> Optional[OutboundMessage]:
    """Pop the next message for a specific user."""
    global _outbound_queue
    
    for i, msg in enumerate(_outbound_queue):
        if msg.origin == origin and msg.external_user_id == external_user_id:
            return _outbound_queue.pop(i)
    
    return None


def clear_outbound_queue() -> int:
    """Clear all pending messages (for testing)."""
    global _outbound_queue
    count = len(_outbound_queue)
    _outbound_queue = []
    return count


# ═══════════════════════════════════════════════════════════════════
# DELIVERY HANDLERS (Platform-specific)
# ═══════════════════════════════════════════════════════════════════

async def deliver_to_flirtmarket(msg: OutboundMessage) -> bool:
    """
    Deliver message to FlirtMarket.
    
    FlirtMarket will poll `/orchestrator/outbound/flirtmarket`
    or we push via webhook.
    """
    # TODO: Implement FlirtMarket webhook/API call
    print(f"[Outbound] Would deliver to FlirtMarket: {msg.external_user_id}")
    return True


async def deliver_to_telegram(msg: OutboundMessage) -> bool:
    """
    Deliver message to Telegram user.
    
    Uses the Telegram bot to send DM.
    """
    # TODO: Implement Telegram bot sendMessage
    print(f"[Outbound] Would deliver to Telegram: {msg.external_user_id}")
    return True


async def deliver_message(msg: OutboundMessage) -> bool:
    """Route delivery to appropriate platform handler."""
    if msg.origin == ConversationOrigin.FLIRTMARKET:
        return await deliver_to_flirtmarket(msg)
    elif msg.origin == ConversationOrigin.TELEGRAM:
        return await deliver_to_telegram(msg)
    else:
        print(f"[Outbound] Unknown origin: {msg.origin}")
        return False


# ═══════════════════════════════════════════════════════════════════
# POLLING ENDPOINT SUPPORT
# ═══════════════════════════════════════════════════════════════════

def get_outbound_for_polling(
    origin: ConversationOrigin,
    limit: int = 10,
) -> list[dict]:
    """
    Get pending messages for a platform to poll.
    
    FlirtMarket calls:
    GET /orchestrator/outbound/poll?origin=FLIRTMARKET
    
    Returns list of messages, marks them as in-flight.
    """
    pending = [m for m in _outbound_queue if m.origin == origin][:limit]
    
    return [
        {
            "external_user_id": m.external_user_id,
            "text": m.text,
            "conversation_id": m.conversation_id,
            "message_id": m.message_id,
        }
        for m in pending
    ]


def confirm_outbound_delivered(
    origin: ConversationOrigin,
    external_user_id: str,
    message_id: int,
) -> bool:
    """Mark a message as successfully delivered."""
    global _outbound_queue
    
    for i, msg in enumerate(_outbound_queue):
        if (
            msg.origin == origin
            and msg.external_user_id == external_user_id
            and msg.message_id == message_id
        ):
            _outbound_queue.pop(i)
            print(f"[Outbound] Confirmed delivery: {origin.value}:{external_user_id}:{message_id}")
            return True
    
    return False

