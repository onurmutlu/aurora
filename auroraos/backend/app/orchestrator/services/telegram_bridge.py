"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Telegram Bridge Service                ║
║   Handles real Telegram DMs and routes to orchestrator           ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime
from typing import Optional, Tuple
import hashlib

from sqlmodel import Session, select

from ..models import (
    Conversation,
    ConversationMessage,
    PerformerSlot,
    UserMapping,
    ConversationMode,
    ConversationOrigin,
)
from ..schemas import (
    TelegramInboundMessage,
    TelegramInboundResponse,
    RoutingMode,
)
from .agent import call_aurora_agent
from .routing_decision import orchestrator_decision
from .outbound import enqueue_outbound_message


class TelegramBridgeService:
    """
    Bridge between real Telegram DMs and AuroraOS orchestrator.
    
    Flow:
    1. Telegram worker sends DM to /orchestrator/telegram/inbound
    2. This service:
       - Maps Telegram user to internal user
       - Finds or creates conversation
       - Decides routing (AI/Human/Hybrid)
       - If AI: generates reply and queues outbound
       - If Human/Hybrid: queues for operator
    3. Returns response to Telegram worker
    """
    
    DEFAULT_PERFORMER_SLOT_ID = 1  # Betelle Fox #1
    
    def process_inbound(
        self,
        db: Session,
        message: TelegramInboundMessage,
    ) -> TelegramInboundResponse:
        """
        Process an inbound Telegram message.
        """
        # 1. Map Telegram user to internal user
        user_id, is_new_user = self._get_or_create_user(
            db,
            telegram_user_id=message.telegram_user_id,
            username=message.username,
            first_name=message.first_name,
        )
        
        # 2. Find or create conversation
        conversation, is_new_conv = self._get_or_create_conversation(
            db,
            user_id=user_id,
            external_user_id=f"tg_{message.telegram_user_id}",
        )
        
        # 3. Save incoming message
        self._save_message(
            db,
            conversation_id=conversation.id,
            text=message.message,
            sender="user",
        )
        
        # 4. Make routing decision
        routing_decision = orchestrator_decision.decide_route(
            conversation={
                "id": str(conversation.id),
                "performer": {"id": conversation.agent_id},
                "customer": {
                    "tier": self._get_user_tier(db, user_id),
                    "coins_spent": conversation.coins_spent,
                },
            },
            customer_risk_score=self._calculate_risk_score(conversation),
        )
        
        # 5. Update conversation mode based on routing
        conversation.mode = self._map_routing_to_mode(routing_decision.routing_mode)
        db.add(conversation)
        db.commit()
        
        # 6. Handle based on routing mode
        ai_reply = None
        queued_for_operator = False
        
        if routing_decision.routing_mode == RoutingMode.AI_ONLY:
            # Full AI response
            ai_reply = self._generate_ai_reply(
                db,
                conversation=conversation,
                message=message.message,
            )
            
            # Queue for outbound (Telegram worker will poll)
            enqueue_outbound_message(
                origin=ConversationOrigin.TELEGRAM,
                external_user_id=f"tg_{message.telegram_user_id}",
                text=ai_reply,
                conversation_id=conversation.id,
            )
            
        elif routing_decision.routing_mode == RoutingMode.HYBRID:
            # Generate AI draft for operator review
            ai_reply = self._generate_ai_reply(
                db,
                conversation=conversation,
                message=message.message,
                is_draft=True,
            )
            queued_for_operator = True
            
        else:  # HUMAN_ONLY
            queued_for_operator = True
        
        # 7. Try to match with FlirtMarket conversation
        fm_conv_id = self._find_flirtmarket_match(db, message.telegram_user_id)
        
        return TelegramInboundResponse(
            success=True,
            conversation_id=conversation.id,
            routing_mode=routing_decision.routing_mode,
            ai_reply=ai_reply,
            queued_for_operator=queued_for_operator,
            matched_flirtmarket_conversation=fm_conv_id,
        )
    
    def _get_or_create_user(
        self,
        db: Session,
        telegram_user_id: int,
        username: Optional[str],
        first_name: Optional[str],
    ) -> Tuple[int, bool]:
        """Get or create internal user from Telegram user."""
        external_id = f"tg_{telegram_user_id}"
        
        stmt = select(UserMapping).where(
            UserMapping.origin == ConversationOrigin.TELEGRAM,
            UserMapping.external_user_id == external_id,
        )
        mapping = db.exec(stmt).first()
        
        if mapping:
            # Update display name if changed
            display = username or first_name
            if display and mapping.display_name != display:
                mapping.display_name = display
                db.add(mapping)
                db.commit()
            return mapping.internal_user_id, False
        
        # Create new mapping
        max_stmt = select(UserMapping).order_by(UserMapping.internal_user_id.desc()).limit(1)
        last = db.exec(max_stmt).first()
        new_id = (last.internal_user_id + 1) if last else 1
        
        new_mapping = UserMapping(
            origin=ConversationOrigin.TELEGRAM,
            external_user_id=external_id,
            internal_user_id=new_id,
            display_name=username or first_name,
        )
        db.add(new_mapping)
        db.commit()
        
        return new_id, True
    
    def _get_or_create_conversation(
        self,
        db: Session,
        user_id: int,
        external_user_id: str,
    ) -> Tuple[Conversation, bool]:
        """Get or create conversation for this user."""
        stmt = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.origin == ConversationOrigin.TELEGRAM,
            Conversation.is_active == True,
        )
        conv = db.exec(stmt).first()
        
        if conv:
            conv.last_message_at = datetime.utcnow()
            conv.message_count += 1
            db.add(conv)
            db.commit()
            return conv, False
        
        # Get default performer slot
        slot = db.get(PerformerSlot, self.DEFAULT_PERFORMER_SLOT_ID)
        agent_id = slot.agent_id if slot else "betelle_fox_v1"
        
        conv = Conversation(
            user_id=user_id,
            external_user_id=external_user_id,
            performer_slot_id=self.DEFAULT_PERFORMER_SLOT_ID,
            agent_id=agent_id,
            origin=ConversationOrigin.TELEGRAM,
            mode=ConversationMode.AI_ONLY,
            last_message_at=datetime.utcnow(),
            message_count=1,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
        return conv, True
    
    def _save_message(
        self,
        db: Session,
        conversation_id: int,
        text: str,
        sender: str,
        is_draft: bool = False,
    ) -> ConversationMessage:
        """Save a message to the conversation."""
        msg = ConversationMessage(
            conversation_id=conversation_id,
            sender=sender,
            text=text,
            source="telegram",
            is_draft=is_draft,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    
    def _generate_ai_reply(
        self,
        db: Session,
        conversation: Conversation,
        message: str,
        is_draft: bool = False,
    ) -> str:
        """Generate AI reply using Aurora agent."""
        result = call_aurora_agent(
            session=db,
            agent_id=conversation.agent_id,
            conversation_id=conversation.id,
            message=message,
        )
        
        # Save the reply
        self._save_message(
            db,
            conversation_id=conversation.id,
            text=result.reply,
            sender="agent",
            is_draft=is_draft,
        )
        
        return result.reply
    
    def _get_user_tier(self, db: Session, user_id: int) -> str:
        """Get user's VIP tier."""
        stmt = select(UserMapping).where(UserMapping.internal_user_id == user_id)
        mapping = db.exec(stmt).first()
        return mapping.vip_tier if mapping else "none"
    
    def _calculate_risk_score(self, conversation: Conversation) -> float:
        """
        Calculate customer risk/value score (0.0-1.0).
        Higher = more valuable customer.
        """
        score = 0.0
        
        # Message count factor (more messages = more engaged)
        if conversation.message_count > 50:
            score += 0.3
        elif conversation.message_count > 20:
            score += 0.2
        elif conversation.message_count > 5:
            score += 0.1
        
        # Coins spent factor
        if conversation.coins_spent > 1000:
            score += 0.4
        elif conversation.coins_spent > 500:
            score += 0.3
        elif conversation.coins_spent > 100:
            score += 0.2
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _map_routing_to_mode(self, routing: RoutingMode) -> ConversationMode:
        """Map routing mode to conversation mode."""
        mapping = {
            RoutingMode.AI_ONLY: ConversationMode.AI_ONLY,
            RoutingMode.HUMAN_ONLY: ConversationMode.HUMAN_ONLY,
            RoutingMode.HYBRID: ConversationMode.HYBRID_GHOST,
            RoutingMode.AUTO: ConversationMode.AI_ONLY,
        }
        return mapping.get(routing, ConversationMode.AI_ONLY)
    
    def _find_flirtmarket_match(
        self,
        db: Session,
        telegram_user_id: int,
    ) -> Optional[str]:
        """
        Try to find a matching FlirtMarket conversation.
        
        This would use various signals:
        - Username matching
        - Phone number (if shared)
        - Custom linking via bot commands
        
        For now, returns None.
        """
        # TODO: Implement FlirtMarket ↔ Telegram linking
        return None


# Singleton instance
telegram_bridge = TelegramBridgeService()

