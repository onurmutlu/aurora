"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — API Router                             ║
║   Main entry point for all orchestrator endpoints                ║
║                                                                  ║
║   Endpoints:                                                     ║
║   - POST /incoming-message  (FlirtMarket/Telegram → Aurora)      ║
║   - GET  /conversations     (Operator Console - list)            ║
║   - GET  /conversations/:id (Operator Console - detail)          ║
║   - POST /conversations/:id/reply (Operator sends reply)         ║
║   - GET  /outbound/poll     (Platform polls for replies)         ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from ..deps import get_db
from .models import (
    Conversation,
    ConversationMessage,
    PerformerSlot,
    Operator,
    ConversationMode,
    ConversationPriority,
    ConversationOrigin,
)
from .schemas import (
    IncomingMessageDTO,
    IncomingMessageResponse,
    ConversationListItem,
    ConversationDetail,
    MessageOut,
    OperatorReplyRequest,
    OperatorReplyResponse,
    PerformerSlotCreate,
    PerformerSlotOut,
    OperatorCreate,
    OperatorOut,
    OperatorStatusUpdate,
)
from .services.routing import decide_routing
from .services.agent import call_aurora_agent, generate_agent_draft
from .services.user_mapping import map_external_user_to_internal, update_user_stats
from .services.outbound import enqueue_outbound_message, get_outbound_for_polling, confirm_outbound_delivered


router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# INCOMING MESSAGE — Main orchestrator entry point
# ═══════════════════════════════════════════════════════════════════

@router.post("/incoming-message", response_model=IncomingMessageResponse)
def incoming_message(
    payload: IncomingMessageDTO,
    db: Session = Depends(get_db),
):
    """
    🚀 Main orchestrator endpoint.
    
    FlirtMarket, Telegram, Web → all post here.
    
    Flow:
    1. Map external user to internal ID
    2. Find or create conversation
    3. Save incoming message
    4. Decide routing (AI_ONLY / HYBRID / HUMAN)
    5. If AI_ONLY: call agent, save reply, queue outbound
    6. If HYBRID: create draft for operator
    7. If HUMAN: just queue for operator
    """
    origin = payload.origin
    ext_user = payload.external_user_id
    slot_id = payload.performer_slot_id
    text = payload.text
    meta = payload.meta
    
    # 1) External → Internal user mapping
    user_id = map_external_user_to_internal(db, origin, ext_user)
    
    # Update user stats if provided
    if meta:
        update_user_stats(
            db, origin, ext_user,
            coins_spent=meta.coins_spent_total,
            vip_tier=meta.vip_tier,
        )
    
    # 2) Find or create conversation
    stmt = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.performer_slot_id == slot_id,
        Conversation.is_active == True,
    )
    convo = db.exec(stmt).first()
    
    if not convo:
        # Get performer slot
        slot = db.get(PerformerSlot, slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="PerformerSlot not found")
        
        convo = Conversation(
            user_id=user_id,
            external_user_id=ext_user,
            performer_slot_id=slot_id,
            agent_id=slot.agent_id,
            origin=origin,
        )
        db.add(convo)
        db.commit()
        db.refresh(convo)
    
    # 3) Save incoming message
    msg = ConversationMessage(
        conversation_id=convo.id,
        sender="user",
        text=text,
        source=origin.value.lower(),
    )
    db.add(msg)
    
    # Update conversation stats
    convo.message_count += 1
    convo.last_message_at = datetime.utcnow()
    if meta and meta.coins_spent_total:
        convo.coins_spent = meta.coins_spent_total
    
    db.add(convo)
    db.commit()
    
    # 4) Routing decision
    routing = decide_routing(
        coins_spent_total=meta.coins_spent_total if meta else 0,
        vip_tier=meta.vip_tier if meta else "none",
        operator_online=convo.operator_id is not None,
        current_mode=convo.mode,
        message_count=convo.message_count,
    )
    
    # Update conversation if routing changed
    if routing.mode != convo.mode or routing.priority != convo.priority:
        convo.mode = routing.mode
        convo.priority = routing.priority
        if routing.operator_id:
            convo.operator_id = routing.operator_id
        db.add(convo)
        db.commit()
        db.refresh(convo)
    
    # 5) Handle based on mode
    reply_text = None
    queued = False
    
    if convo.mode == ConversationMode.AI_ONLY:
        # Full AI response
        result = call_aurora_agent(
            session=db,
            agent_id=convo.agent_id,
            conversation_id=convo.id,
            message=text,
        )
        reply_text = result.reply
        
        # Save reply
        reply_msg = ConversationMessage(
            conversation_id=convo.id,
            sender="agent",
            text=reply_text,
            source=origin.value.lower(),
            tokens_used=result.tokens_used,
            model_used=result.model_used,
        )
        db.add(reply_msg)
        convo.message_count += 1
        db.add(convo)
        db.commit()
        db.refresh(reply_msg)
        
        # Queue for outbound delivery
        enqueue_outbound_message(
            origin=origin,
            external_user_id=ext_user,
            text=reply_text,
            conversation_id=convo.id,
            message_id=reply_msg.id,
        )
        
    elif convo.mode == ConversationMode.HYBRID_GHOST:
        # Generate draft for operator
        result = generate_agent_draft(
            session=db,
            agent_id=convo.agent_id,
            conversation_id=convo.id,
            message=text,
        )
        
        # Save as draft
        draft_msg = ConversationMessage(
            conversation_id=convo.id,
            sender="agent",
            text=result.reply,
            source=origin.value.lower(),
            is_draft=True,
            tokens_used=result.tokens_used,
            model_used=result.model_used,
        )
        db.add(draft_msg)
        db.commit()
        
        queued = True
        
    else:  # HUMAN_ONLY
        queued = True
    
    return IncomingMessageResponse(
        conversation_id=convo.id,
        mode=convo.mode,
        reply=reply_text,
        queued_for_operator=queued,
        priority=convo.priority,
    )


# ═══════════════════════════════════════════════════════════════════
# OPERATOR CONSOLE — List Conversations
# ═══════════════════════════════════════════════════════════════════

@router.get("/conversations", response_model=List[ConversationListItem])
def list_conversations(
    operator_id: Optional[int] = None,
    mode: Optional[ConversationMode] = None,
    priority: Optional[ConversationPriority] = None,
    origin: Optional[ConversationOrigin] = None,
    active_only: bool = True,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    📋 List conversations for operator console.
    
    Filters:
    - operator_id: Show only assigned to this operator
    - mode: HYBRID_GHOST, HUMAN_ONLY, etc.
    - priority: VIP, HIGH, etc.
    - origin: FLIRTMARKET, TELEGRAM, etc.
    """
    stmt = select(Conversation)
    
    if operator_id:
        stmt = stmt.where(Conversation.operator_id == operator_id)
    if mode:
        stmt = stmt.where(Conversation.mode == mode)
    if priority:
        stmt = stmt.where(Conversation.priority == priority)
    if origin:
        stmt = stmt.where(Conversation.origin == origin)
    if active_only:
        stmt = stmt.where(Conversation.is_active == True)
    
    stmt = stmt.order_by(Conversation.last_message_at.desc()).offset(offset).limit(limit)
    
    conversations = db.exec(stmt).all()
    
    result = []
    for convo in conversations:
        # Get last message preview
        last_msg_stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == convo.id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(1)
        )
        last_msg = db.exec(last_msg_stmt).first()
        
        # Get performer slot label
        slot = db.get(PerformerSlot, convo.performer_slot_id)
        
        result.append(ConversationListItem(
            id=convo.id,
            external_user_id=convo.external_user_id,
            performer_slot_label=slot.label if slot else "Unknown",
            agent_id=convo.agent_id,
            mode=convo.mode,
            priority=convo.priority,
            origin=convo.origin,
            message_count=convo.message_count,
            coins_spent=convo.coins_spent,
            last_message_at=convo.last_message_at,
            last_message_preview=last_msg.text[:100] if last_msg else None,
            is_active=convo.is_active,
        ))
    
    return result


# ═══════════════════════════════════════════════════════════════════
# OPERATOR CONSOLE — Get Conversation Detail
# ═══════════════════════════════════════════════════════════════════

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """
    💬 Get full conversation with messages.
    """
    convo = db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    stmt = (
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.asc())
    )
    messages = db.exec(stmt).all()
    
    # Get performer slot
    slot = db.get(PerformerSlot, convo.performer_slot_id)
    
    return ConversationDetail(
        id=convo.id,
        external_user_id=convo.external_user_id,
        performer_slot_id=convo.performer_slot_id,
        performer_slot_label=slot.label if slot else "Unknown",
        agent_id=convo.agent_id,
        mode=convo.mode,
        priority=convo.priority,
        origin=convo.origin,
        message_count=convo.message_count,
        coins_spent=convo.coins_spent,
        is_active=convo.is_active,
        created_at=convo.created_at,
        messages=[
            MessageOut(
                id=m.id,
                sender=m.sender,
                text=m.text,
                source=m.source,
                is_draft=m.is_draft,
                edited_by_operator=m.edited_by_operator,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# OPERATOR CONSOLE — Send Reply
# ═══════════════════════════════════════════════════════════════════

@router.post("/conversations/{conversation_id}/reply", response_model=OperatorReplyResponse)
def operator_reply(
    conversation_id: int,
    payload: OperatorReplyRequest,
    db: Session = Depends(get_db),
):
    """
    ✍️ Operator sends a reply or approves/edits a draft.
    """
    convo = db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # If editing a draft, update it
    if payload.edit_draft_id:
        draft = db.get(ConversationMessage, payload.edit_draft_id)
        if draft and draft.is_draft:
            draft.original_text = draft.text
            draft.text = payload.text
            draft.edited_by_operator = True
            draft.is_draft = False
            draft.sender = "operator" if payload.send_as == "operator" else "agent"
            db.add(draft)
            db.commit()
            db.refresh(draft)
            
            # Queue for outbound
            enqueue_outbound_message(
                origin=convo.origin,
                external_user_id=convo.external_user_id,
                text=payload.text,
                conversation_id=convo.id,
                message_id=draft.id,
            )
            
            return OperatorReplyResponse(
                message_id=draft.id,
                sent=True,
                queued_for_outbound=True,
            )
    
    # Create new message
    sender = "operator" if payload.send_as == "operator" else "agent"
    
    msg = ConversationMessage(
        conversation_id=conversation_id,
        sender=sender,
        text=payload.text,
        source="operator_console",
        edited_by_operator=True if sender == "agent" else False,
    )
    db.add(msg)
    
    # Update conversation
    convo.message_count += 1
    convo.last_message_at = datetime.utcnow()
    db.add(convo)
    
    db.commit()
    db.refresh(msg)
    
    # Queue for outbound
    enqueue_outbound_message(
        origin=convo.origin,
        external_user_id=convo.external_user_id,
        text=payload.text,
        conversation_id=convo.id,
        message_id=msg.id,
    )
    
    return OperatorReplyResponse(
        message_id=msg.id,
        sent=True,
        queued_for_outbound=True,
    )


# ═══════════════════════════════════════════════════════════════════
# OUTBOUND POLLING — For FlirtMarket / Telegram to fetch replies
# ═══════════════════════════════════════════════════════════════════

@router.get("/outbound/poll")
def poll_outbound(
    origin: ConversationOrigin,
    limit: int = Query(default=10, le=50),
):
    """
    📤 Platform polls for pending outbound messages.
    
    FlirtMarket/Telegram calls this to get AI/operator replies.
    """
    messages = get_outbound_for_polling(origin, limit)
    return {"messages": messages, "count": len(messages)}


@router.post("/outbound/confirm")
def confirm_delivery(
    origin: ConversationOrigin,
    external_user_id: str,
    message_id: int,
):
    """
    ✅ Platform confirms message was delivered.
    """
    success = confirm_outbound_delivered(origin, external_user_id, message_id)
    return {"confirmed": success}


# ═══════════════════════════════════════════════════════════════════
# PERFORMER SLOTS — CRUD
# ═══════════════════════════════════════════════════════════════════

@router.post("/performer-slots", response_model=PerformerSlotOut)
def create_performer_slot(
    payload: PerformerSlotCreate,
    db: Session = Depends(get_db),
):
    """Create a new performer slot."""
    slot = PerformerSlot(**payload.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/performer-slots", response_model=List[PerformerSlotOut])
def list_performer_slots(
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """List all performer slots."""
    stmt = select(PerformerSlot)
    if active_only:
        stmt = stmt.where(PerformerSlot.is_active == True)
    return db.exec(stmt).all()


# ═══════════════════════════════════════════════════════════════════
# OPERATORS — CRUD
# ═══════════════════════════════════════════════════════════════════

@router.post("/operators", response_model=OperatorOut)
def create_operator(
    payload: OperatorCreate,
    db: Session = Depends(get_db),
):
    """Create a new operator."""
    op = Operator(**payload.model_dump())
    db.add(op)
    db.commit()
    db.refresh(op)
    return OperatorOut(
        id=op.id,
        name=op.name,
        external_id=op.external_id,
        is_online=op.is_online,
        max_concurrent_chats=op.max_concurrent_chats,
        active_chat_count=0,
    )


@router.get("/operators", response_model=List[OperatorOut])
def list_operators(db: Session = Depends(get_db)):
    """List all operators."""
    ops = db.exec(select(Operator)).all()
    
    result = []
    for op in ops:
        # Count active conversations
        count_stmt = select(func.count(Conversation.id)).where(
            Conversation.operator_id == op.id,
            Conversation.is_active == True,
        )
        active_count = db.exec(count_stmt).one()
        
        result.append(OperatorOut(
            id=op.id,
            name=op.name,
            external_id=op.external_id,
            is_online=op.is_online,
            max_concurrent_chats=op.max_concurrent_chats,
            active_chat_count=active_count,
        ))
    
    return result


@router.patch("/operators/{operator_id}/status")
def update_operator_status(
    operator_id: int,
    payload: OperatorStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update operator online status."""
    op = db.get(Operator, operator_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    op.is_online = payload.is_online
    db.add(op)
    db.commit()
    
    return {"id": operator_id, "is_online": op.is_online}


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION MODE CHANGE
# ═══════════════════════════════════════════════════════════════════

class ConversationModeUpdate(BaseModel):
    mode: ConversationMode


from pydantic import BaseModel


@router.patch("/conversations/{conversation_id}/mode")
def update_conversation_mode(
    conversation_id: int,
    payload: ConversationModeUpdate,
    db: Session = Depends(get_db),
):
    """
    🔄 Change conversation mode (AI_ONLY / HYBRID_GHOST / HUMAN_ONLY).
    """
    convo = db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    old_mode = convo.mode
    convo.mode = payload.mode
    convo.updated_at = datetime.utcnow()
    
    db.add(convo)
    db.commit()
    
    return {
        "success": True,
        "conversation_id": conversation_id,
        "old_mode": old_mode.value,
        "new_mode": payload.mode.value,
    }

