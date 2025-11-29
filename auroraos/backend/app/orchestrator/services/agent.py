"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Orchestrator — Agent Service                          ║
║   Calls Grok/OpenAI for conversation replies                     ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json
from dataclasses import dataclass
from typing import Optional, List

from sqlmodel import Session, select

from ..models import ConversationMessage, PerformerSlot
from ...config import settings


@dataclass
class AgentReply:
    """Response from Aurora Agent."""
    reply: str
    tokens_used: int
    model_used: str
    raw_response: Optional[dict] = None


# ═══════════════════════════════════════════════════════════════════
# DEFAULT PROMPTS
# ═══════════════════════════════════════════════════════════════════

DEFAULT_PERFORMER_PROMPT = """
Sen FlirtMarket'te çalışan bir AI performer'sın. Karakterin: {label}

Görevin:
- Kullanıcıyla flörtöz, eğlenceli ve çekici bir şekilde sohbet etmek
- Sınırları koruyarak soft-ero içerik üretmek
- Kullanıcıyı platformda tutmak ve coin harcamaya teşvik etmek
- Asla gerçek buluşma veya platform dışı iletişim teklif etmemek

Ton:
- Feminin, özgüvenli, gizemli
- Kısa cevaplar (max 2-3 cümle)
- Emoji kullanımı minimal ama etkili
- Türkçe konuş

Yasak:
- Gerçek kimlik bilgisi verme
- Platform dışı iletişim (telefon, sosyal medya)
- Explicit sexual content (soft-ero OK)
- Para transferi veya ödeme talebi
""".strip()


# ═══════════════════════════════════════════════════════════════════
# LLM CLIENTS
# ═══════════════════════════════════════════════════════════════════

def get_grok_client():
    """Get Grok (xAI) client."""
    if not settings.XAI_API_KEY:
        return None
    from openai import OpenAI
    return OpenAI(api_key=settings.XAI_API_KEY, base_url="https://api.x.ai/v1")


def get_openai_client():
    """Get OpenAI client."""
    if not settings.OPENAI_API_KEY:
        return None
    from openai import OpenAI
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_llm_client(provider: str):
    """Get LLM client by provider name."""
    if provider == "grok":
        return get_grok_client()
    elif provider == "openai":
        return get_openai_client()
    return None


# ═══════════════════════════════════════════════════════════════════
# AGENT CALL
# ═══════════════════════════════════════════════════════════════════

def call_aurora_agent(
    session: Session,
    agent_id: str,
    conversation_id: int,
    message: str,
    performer_slot: Optional[PerformerSlot] = None,
) -> AgentReply:
    """
    Call Aurora Agent (Grok/OpenAI) for a conversation reply.
    
    1. Get performer slot config (or use defaults)
    2. Fetch conversation history
    3. Build prompt
    4. Call LLM
    5. Return reply
    """
    
    # Get performer slot config
    if performer_slot is None:
        stmt = select(PerformerSlot).where(PerformerSlot.agent_id == agent_id)
        performer_slot = session.exec(stmt).first()
    
    # Defaults if no slot found
    provider = "grok"
    model = "grok-3-latest"
    system_prompt = DEFAULT_PERFORMER_PROMPT.format(label="Performer")
    temperature = 0.8
    max_tokens = 200
    label = "Performer"
    
    if performer_slot:
        provider = performer_slot.provider
        model = performer_slot.model
        system_prompt = performer_slot.system_prompt or DEFAULT_PERFORMER_PROMPT.format(label=performer_slot.label)
        temperature = performer_slot.temperature
        max_tokens = performer_slot.max_tokens
        label = performer_slot.label
    
    # Get LLM client
    client = get_llm_client(provider)
    
    if not client:
        # Fallback mock response
        return AgentReply(
            reply=f"Merhaba! Ben {label}. Şu an meşgulüm ama birazdan döneceğim 💋",
            tokens_used=0,
            model_used="mock",
        )
    
    # Fetch conversation history (last 10 messages)
    stmt = (
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(10)
    )
    history_messages = list(reversed(session.exec(stmt).all()))
    
    # Build messages for LLM
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for msg in history_messages:
        role = "user" if msg.sender == "user" else "assistant"
        messages.append({"role": role, "content": msg.text})
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Call LLM
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        reply = completion.choices[0].message.content or ""
        tokens_used = completion.usage.total_tokens if completion.usage else 0
        
        return AgentReply(
            reply=reply.strip(),
            tokens_used=tokens_used,
            model_used=model,
            raw_response=completion.model_dump() if hasattr(completion, 'model_dump') else None,
        )
        
    except Exception as e:
        print(f"[Agent] LLM error: {e}")
        return AgentReply(
            reply=f"Bir saniye, hemen döneceğim... 💫",
            tokens_used=0,
            model_used="error_fallback",
        )


def generate_agent_draft(
    session: Session,
    agent_id: str,
    conversation_id: int,
    message: str,
    performer_slot: Optional[PerformerSlot] = None,
) -> AgentReply:
    """
    Generate a draft reply for HYBRID_GHOST mode.
    Operator will review before sending.
    """
    return call_aurora_agent(
        session=session,
        agent_id=agent_id,
        conversation_id=conversation_id,
        message=message,
        performer_slot=performer_slot,
    )

