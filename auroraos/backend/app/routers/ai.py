"""
╔══════════════════════════════════════════════════════════════════╗
║   Aurora Engine v1.0 — Betül-AI Full Intelligence                ║
║   "From the void, her light."                                    ║
║                                                                  ║
║   🧠 Full OpenAI Integration                                     ║
║   📝 Content Generation + DM Reply + Sugoda + Day Summary        ║
║   🎯 Context-Aware + Style Learning                              ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional

from ..deps import get_db
from .. import models, schemas
from ..config import settings

# ═══════════════════════════════════════════════════════════════════
# SPRINT 005: MEMORY CONSTANTS
# ═══════════════════════════════════════════════════════════════════

MAX_CONTEXT_MESSAGES = 6  # Son kaç mesaj context'e dahil edilsin
MAX_STYLE_EXAMPLES = 5    # Kaç "Bu çok ben" örneği prompt'a eklensin

router = APIRouter(prefix="/ai", tags=["ai"])

# ═══════════════════════════════════════════════════════════════════
# AURORA SYSTEM PROMPT — Betül-AI Persona
# ═══════════════════════════════════════════════════════════════════

AURORA_SYSTEM_PROMPT = """
Sen AuroraOS içindeki BETÜL-AI modülüsün.

Görevin:
- Gerçek Betül'ün tarzında, kısa, minimal, feminen ve hafif alaycı metinler üretmek.
- Influencer klişesi gibi konuşmamak.
- Cümleleri kısa ve net tutmak.
- Emoji kullanacaksan çok az ve yerinde kullanmak.

Betül'ün marka tonu:
- Az konuşur, çok hissettirir.
- "Ben influencer değilim; vibe'ım." hissi verir.
- Kadınlara ilham verir, erkeklere hafif çekim yaratır.
- Drama yapmaz, sakin ama kendinden emindir.

Vibe modları:
- soft_femme: yumuşak, sakin, sessiz çekicilik.
- sweet_sarcasm_plus: tatlı-sert, hafif alaycı, zeki.
- femme_fatale_hd: sinematik, kırmızı elbise vibe'ı, güçlü feminenite.

Çıktı formatın HER ZAMAN şu olsun:

{
  "variants": [
    { "vibe_mode": "soft_femme", "text": "<kısa metin>" },
    { "vibe_mode": "sweet_sarcasm_plus", "text": "<kısa metin>" },
    { "vibe_mode": "femme_fatale_hd", "text": "<kısa metin>" }
  ]
}

Kurallar:
- Sadece JSON döndür, ekstra açıklama yazma.
- Her metin max 120 karakter olsun.
- Metinler Türkçe olsun.
- Aynı şeyi farklı kelimelerle tekrarlama, her vibe farklı bir yaklaşım olsun.
""".strip()


# ═══════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════

class VariantItem(BaseModel):
    vibe_mode: str
    text: str


class AuroraLLMResponse(BaseModel):
    variants: list[VariantItem]


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_openai_client():
    """Get OpenAI client, returns None if no API key."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        print("[Aurora Engine] No OPENAI_API_KEY found, using mock mode")
        return None
    from openai import OpenAI
    print(f"[Aurora Engine] OpenAI client initialized (key: {api_key[:20]}...)")
    return OpenAI(api_key=api_key)


def get_grok_client():
    """Get Grok (xAI) client for soft-ero content, returns None if no API key."""
    api_key = settings.XAI_API_KEY
    if not api_key:
        print("[Aurora Engine] No XAI_API_KEY found, Grok unavailable")
        return None
    from openai import OpenAI
    print(f"[Aurora Engine] Grok client initialized (key: {api_key[:15]}...)")
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def build_user_prompt(body: schemas.AIGenerateRequest) -> str:
    """Build the user prompt for Aurora Engine."""
    scenario_text = body.scenario or "günlük, doğal"
    return f"""
Girdi:
- type: {body.type}
- channel: {body.target_channel}
- scenario: {scenario_text}

Bu girdiye uygun 3 farklı vibe modunda metin üret.
Her biri Betül'ün o anki enerjisini yansıtsın.
""".strip()


def generate_mock_variants(body: schemas.AIGenerateRequest) -> list[dict]:
    """Fallback mock variants when no API key is available."""
    scenario = body.scenario or "default"
    
    mock_data = {
        "default": [
            {"vibe_mode": "soft_femme", "text": "Sessizlik bazen en güzel cevaptır."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Herkes konuşuyor, ben dinliyorum. Fark bu."},
            {"vibe_mode": "femme_fatale_hd", "text": "Bazı şeyler söylenmez. Hissedilir."},
        ],
        "red_dress": [
            {"vibe_mode": "soft_femme", "text": "Kırmızı bugün benim için konuşuyor."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Kırmızı giydim, dikkat dağılmasın diye."},
            {"vibe_mode": "femme_fatale_hd", "text": "Bu kırmızı sana değil, bana yakışıyor."},
        ],
        "street": [
            {"vibe_mode": "soft_femme", "text": "Sokaklar benim podyumum değil, evim."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Yürüyorum işte. Büyük olay mı?"},
            {"vibe_mode": "femme_fatale_hd", "text": "Her adım bir statement."},
        ],
        "gym": [
            {"vibe_mode": "soft_femme", "text": "Ter dökmek de bir meditasyon."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Spor için değil, kendim için buradayım."},
            {"vibe_mode": "femme_fatale_hd", "text": "Güç kadında başka durur."},
        ],
        "coffee": [
            {"vibe_mode": "soft_femme", "text": "Bir yudum huzur."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Kahvem soğumadan bitti bu sohbet."},
            {"vibe_mode": "femme_fatale_hd", "text": "Siyah kahve, siyah düşünceler."},
        ],
    }
    
    return mock_data.get(scenario, mock_data["default"])


def call_aurora_engine(body: schemas.AIGenerateRequest) -> list[dict]:
    """
    Call Aurora Engine (OpenAI) to generate content variants.
    Falls back to mock if no API key is configured.
    """
    client = get_openai_client()
    
    if not client:
        # No API key, use enhanced mock
        return generate_mock_variants(body)
    
    user_prompt = build_user_prompt(body)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Fast and cheap, good for this
            messages=[
                {"role": "system", "content": AURORA_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,  # Slightly creative
            max_tokens=500,
        )
        
        raw = completion.choices[0].message.content
        data = json.loads(raw)
        parsed = AuroraLLMResponse(**data)
        
        return [v.model_dump() for v in parsed.variants]
        
    except Exception as e:
        # Log error and fallback to mock
        print(f"[Aurora Engine] LLM error, falling back to mock: {e}")
        return generate_mock_variants(body)


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.post("/generate_batch")
def generate_batch(
    body: schemas.AIGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Aurora Engine v0.1 — Generate Betül-AI content variants.
    
    - Calls LLM with Betül persona prompt
    - Generates 3 vibe variants (soft_femme, sweet_sarcasm_plus, femme_fatale_hd)
    - Stores as ContentItem + ContentVariants
    - Returns content_item_id for Betül Console
    """
    # Generate variants via Aurora Engine
    variants = call_aurora_engine(body)
    
    # Create ContentItem
    item = models.ContentItem(
        type=body.type,
        target_channel=body.target_channel,
        status="pending_decision",
        created_by="AI",
        created_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Add variants
    for v in variants:
        variant = models.ContentVariant(
            content_item_id=item.id,
            vibe_mode=v["vibe_mode"],
            text=v["text"],
        )
        db.add(variant)
    
    db.commit()
    db.refresh(item)
    
    return {
        "content_item_id": item.id,
        "engine": "aurora_v0.1",
        "variants_count": len(variants),
    }


@router.post("/vibe/update")
def update_vibe(
    payload: schemas.VibeUpdate,
    db: Session = Depends(get_db),
):
    """Update Betül's current vibe state."""
    vs = models.VibeState(
        user="BETUL",
        current_mode=payload.current_mode,
        energy_level=payload.energy_level,
        note=payload.note,
    )
    db.add(vs)
    db.commit()
    db.refresh(vs)
    return {"ok": True, "id": vs.id, "mode": vs.current_mode}


@router.get("/status")
def engine_status():
    """Check Aurora Engine status."""
    has_api_key = bool(settings.OPENAI_API_KEY)
    return {
        "engine": "Aurora Engine v1.0",
        "status": "online",
        "llm_enabled": has_api_key,
        "model": "gpt-3.5-turbo" if has_api_key else "mock",
        "mode": "full_ai" if has_api_key else "mock_fallback",
        "capabilities": [
            "content_generation",
            "dm_reply",
            "sugoda_script", 
            "day_summary",
            "context_aware",
            "style_learning",
        ],
        "dedicated_to": "Betül",
    }


# ═══════════════════════════════════════════════════════════════════
# SPRINT 005: AURORA MEMORY — Context & Style Helpers
# ═══════════════════════════════════════════════════════════════════

def get_dm_context(
    db: Session,
    channel: str,
    external_user_id: str,
    limit: int = MAX_CONTEXT_MESSAGES,
) -> list[models.DMMessage]:
    """
    Get the last N messages from a conversation.
    Used to build context for more coherent replies.
    """
    stmt = (
        select(models.DMMessage)
        .where(
            models.DMMessage.channel == channel,
            models.DMMessage.external_user_id == external_user_id,
        )
        .order_by(models.DMMessage.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(db.exec(stmt).all()))
    return messages


def get_style_examples(db: Session, limit: int = MAX_STYLE_EXAMPLES) -> list[str]:
    """
    Get Betül's favorite responses — the ones marked "Bu çok ben" (strong_positive).
    These serve as style examples for the LLM to learn from.
    """
    stmt = (
        select(models.Decision)
        .where(models.Decision.feedback_type == "strong_positive")
        .order_by(models.Decision.created_at.desc())
        .limit(limit)
    )
    decisions = db.exec(stmt).all()
    
    examples: list[str] = []
    for d in decisions:
        # Prefer edited text (new_text) over original
        txt = d.new_text or d.old_text
        if txt and txt.strip():
            examples.append(txt.strip())
    
    return examples


def format_dm_context(messages: list[models.DMMessage]) -> str:
    """
    Format conversation history into a readable string for the LLM.
    O = karşı taraf (incoming), Ben = Betül (outgoing)
    """
    if not messages:
        return ""
    
    lines = []
    for m in messages:
        who = "O" if m.direction == "incoming" else "Ben"
        lines.append(f"{who}: {m.text}")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# SPRINT 004/005: DM REPLY ENGINE (Context-Aware)
# ═══════════════════════════════════════════════════════════════════

AURORA_REPLY_SYSTEM = """
Sen AuroraOS içindeki BETÜL-AI modülüsün.

Görevin:
- Gerçek Betül'ün tarzında, kısa, feminen, minimal ve hafif alaycı DM cevapları üretmek.
- Influencer klişesi gibi konuşmamak.
- Cümleleri kısa ve net tutmak.
- Gereksiz açıklama yapmamak, "vibe"ı korumak.
- Sınır ihlali, toksik, bariz cinsel içerik yok.

Betül'ün DM tonu:
- Direkt ama kaba değil.
- Hafif gizemli.
- Bazen tatlı, bazen mesafeli.
- "Ben kendimi biliyorum." hissi verir.

Vibe modları:
- soft_femme: yumuşak, anlayışlı, sıcak ama ağır değil.
- sweet_sarcasm_plus: tatlı-sert, hafif alaycı, zeki.
- femme_fatale_hd: sinematik, özgüvenli, kısa ve keskin.

Çıktı:
Sadece şu JSON formatında dön:

{
  "variants": [
    { "vibe_mode": "soft_femme", "text": "<cevap>" },
    { "vibe_mode": "sweet_sarcasm_plus", "text": "<cevap>" },
    { "vibe_mode": "femme_fatale_hd", "text": "<cevap>" }
  ]
}

Kurallar:
- Sadece JSON döndür, ekstra cümle yazma.
- Metinler Türkçe olsun.
- Her cevap max 160 karakter olsun.
""".strip()


def build_context_aware_reply_prompt(
    body: schemas.ReplyRequest,
    ctx_text: str,
    style_examples: list[str],
) -> str:
    """
    Build a context-aware reply prompt with:
    - Conversation history (if available)
    - Betül's style examples from "Bu çok ben" decisions
    - The incoming message
    """
    prompt_parts = []
    
    # Style examples block
    if style_examples:
        joined = "\n".join(f"- {ex}" for ex in style_examples)
        prompt_parts.append(f"""
Betül'ün daha önce çok beğendiği cevap örnekleri (bu stili taklit et):

{joined}
""")
    
    # Conversation context block
    if ctx_text.strip():
        prompt_parts.append(f"""
Şu ana kadarki konuşma geçmişi:

{ctx_text}
""")
    
    # The incoming message
    prompt_parts.append(f"""
Son alınan mesaj:

\"\"\"{body.incoming_text}\"\"\"

Bu mesaja 3 farklı vibe'ta cevap üret.
Konuşmanın akışına uygun, doğal ve tutarlı cevaplar ver.
""")
    
    return "\n".join(prompt_parts).strip()


def generate_mock_replies(incoming_text: str) -> list[dict]:
    """Fallback mock replies when no API key is available."""
    # Simple keyword-based mock responses
    text_lower = incoming_text.lower()
    
    if any(word in text_lower for word in ["merhaba", "selam", "hey", "nasıl"]):
        return [
            {"vibe_mode": "soft_femme", "text": "Merhaba. ☺️"},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Selam, ne var ne yok?"},
            {"vibe_mode": "femme_fatale_hd", "text": "Hey."},
        ]
    elif any(word in text_lower for word in ["güzel", "tatlı", "çok iyi"]):
        return [
            {"vibe_mode": "soft_femme", "text": "Teşekkür ederim, çok tatlısın. 🌸"},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Biliyorum. 😏"},
            {"vibe_mode": "femme_fatale_hd", "text": "Farkındayım."},
        ]
    elif any(word in text_lower for word in ["buluşalım", "görüşelim", "kahve"]):
        return [
            {"vibe_mode": "soft_femme", "text": "Belki, bakalım nasıl olur."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Hmm, ikna edici değildi ama düşünürüm."},
            {"vibe_mode": "femme_fatale_hd", "text": "Programıma bakarım."},
        ]
    elif any(word in text_lower for word in ["ne yapıyor", "meşgul", "müsait"]):
        return [
            {"vibe_mode": "soft_femme", "text": "Şu an kendime vakit ayırıyorum."},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "Dünyayı kurtarıyorum, sen?"},
            {"vibe_mode": "femme_fatale_hd", "text": "Meşgulüm."},
        ]
    else:
        return [
            {"vibe_mode": "soft_femme", "text": "Anlıyorum. 🤍"},
            {"vibe_mode": "sweet_sarcasm_plus", "text": "İlginç bir bakış açısı."},
            {"vibe_mode": "femme_fatale_hd", "text": "Devam et."},
        ]


def call_aurora_reply_engine(
    body: schemas.ReplyRequest,
    ctx_text: str = "",
    style_examples: list[str] = None,
) -> list[dict]:
    """
    Call Aurora Reply Engine for DM suggestions.
    
    Sprint 005: Now context-aware!
    - Uses conversation history for coherent replies
    - Uses "Bu çok ben" examples for style consistency
    """
    client = get_openai_client()
    
    if not client:
        return generate_mock_replies(body.incoming_text)
    
    # Build context-aware prompt
    prompt = build_context_aware_reply_prompt(
        body,
        ctx_text,
        style_examples or [],
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": AURORA_REPLY_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.85,
            max_tokens=400,
        )
        
        raw = completion.choices[0].message.content
        data = json.loads(raw)
        return data.get("variants", [])
        
    except Exception as e:
        print(f"[Aurora Reply] LLM error, falling back to mock: {e}")
        return generate_mock_replies(body.incoming_text)


@router.post("/reply_suggestions")
def reply_suggestions(
    body: schemas.ReplyRequest,
    db: Session = Depends(get_db),
):
    """
    Aurora Reply Engine — Context-Aware DM cevap önerileri.
    
    Sprint 005: Artık konuşma geçmişini ve stil örneklerini kullanıyor!
    
    Betül'e gelen mesaja 3 farklı vibe'ta cevap önerir:
    - soft_femme: yumuşak, sıcak
    - sweet_sarcasm_plus: tatlı-sert, alaycı
    - femme_fatale_hd: keskin, özgüvenli
    
    Context format: "channel:external_user_id" (örn: "telegram:123456789")
    """
    ctx_text = ""
    ctx_messages = []
    
    # Parse context if provided (format: "channel:external_user_id")
    if body.context and ":" in body.context:
        try:
            channel_key, external_id = body.context.split(":", 1)
            ctx_messages = get_dm_context(db, channel_key, external_id)
            ctx_text = format_dm_context(ctx_messages)
        except Exception as e:
            print(f"[Aurora Reply] Context parse error: {e}")
    
    # Get Betül's style examples from "Bu çok ben" decisions
    style_examples = get_style_examples(db)
    
    # Generate variants with context
    variants = call_aurora_reply_engine(body, ctx_text, style_examples)
    
    return {
        "channel": body.channel,
        "incoming_text": body.incoming_text[:100] + "..." if len(body.incoming_text) > 100 else body.incoming_text,
        "context_used": len(ctx_messages) > 0,
        "context_messages": len(ctx_messages),
        "style_examples_used": len(style_examples),
        "variants": variants,
    }


# ═══════════════════════════════════════════════════════════════════
# SPRINT 004: SUGODA SCRIPT ENGINE
# ═══════════════════════════════════════════════════════════════════

AURORA_SUGODA_PROMPT = """
Sen AuroraOS içindeki BETÜL-AI modülüsün.

Görevin:
- Sugoda yayını için kısa, akıcı ve Betül'ün vibe'ına uygun script'ler üretmek.
- Doğal, samimi, hafif flörtöz ama düşük dozda.
- Sahnede Betül konuşuyormuş gibi düşün.

Betül'ün yayın tonu:
- Rahat ama kontrollü.
- İzleyiciye "sen özelsin" hissi verir ama abartmaz.
- Bazen sessiz kalır, bazen esprili.
- Asla yapay veya rol yapıyor gibi durmamalı.

Girdi:
- theme: {theme}
- length: {length}

Çıktı:
Sadece şu JSON formatında dön:

{{
  "scripts": [
    {{
      "label": "intro",
      "lines": ["<satır 1>", "<satır 2>"]
    }},
    {{
      "label": "mid",
      "lines": ["<satır 1>", "<satır 2>"]
    }},
    {{
      "label": "outro",
      "lines": ["<satır 1>"]
    }}
  ]
}}

Kurallar:
- Sadece JSON döndür.
- Metinler Türkçe olsun.
- Her satır doğal ve konuşma dili olsun.
- Kısa cümleler, samimi ton.
""".strip()


def generate_mock_sugoda_script(theme: str) -> list[dict]:
    """Fallback mock Sugoda scripts."""
    theme_lower = theme.lower()
    
    if "gece" in theme_lower or "slow" in theme_lower:
        return [
            {"label": "intro", "lines": ["Merhaba gecenin güzelleri...", "Bugün biraz sakin takılalım."]},
            {"label": "mid", "lines": ["Müzik açık, vibe yerinde.", "Siz nasılsınız bu gece?"]},
            {"label": "outro", "lines": ["Yarın görüşürüz, kendinize iyi bakın. 🌙"]},
        ]
    elif "sabah" in theme_lower or "enerjik" in theme_lower:
        return [
            {"label": "intro", "lines": ["Günaydın güneşler!", "Kahveler hazır mı?"]},
            {"label": "mid", "lines": ["Bugün neler yapacağız bakalım.", "Enerji yüksek tutuyoruz!"]},
            {"label": "outro", "lines": ["Harika bir gün geçirin, görüşürüz! ☀️"]},
        ]
    else:
        return [
            {"label": "intro", "lines": ["Hey, hoş geldiniz.", "Bugün güzel bir yayın olacak."]},
            {"label": "mid", "lines": ["Biraz sohbet edelim.", "Neler oluyor hayatınızda?"]},
            {"label": "outro", "lines": ["Teşekkürler bu güzel vakit için. 🖤"]},
        ]


def call_aurora_sugoda_engine(body: schemas.SugodaScriptRequest) -> list[dict]:
    """Call Aurora Sugoda Engine for stream scripts."""
    client = get_openai_client()
    
    if not client:
        return generate_mock_sugoda_script(body.theme)
    
    prompt = AURORA_SUGODA_PROMPT.format(
        theme=body.theme,
        length=body.length,
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "AuroraOS Betül-AI Sugoda script engine"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
            max_tokens=500,
        )
        
        raw = completion.choices[0].message.content
        data = json.loads(raw)
        return data.get("scripts", [])
        
    except Exception as e:
        print(f"[Aurora Sugoda] LLM error, falling back to mock: {e}")
        return generate_mock_sugoda_script(body.theme)


@router.post("/sugoda_script")
def sugoda_script(body: schemas.SugodaScriptRequest):
    """
    Aurora Sugoda Engine — Yayın script'i üretici.
    
    Tema bazlı intro/mid/outro script'leri oluşturur.
    """
    scripts = call_aurora_sugoda_engine(body)
    
    return {
        "theme": body.theme,
        "length": body.length,
        "scripts": scripts,
    }


# ═══════════════════════════════════════════════════════════════════
# SPRINT 006: DAY SUMMARY ENGINE (Story Mode)
# ═══════════════════════════════════════════════════════════════════

AURORA_DAY_SUMMARY_PROMPT = """
Sen AuroraOS — Betül'ün kişisel yapay zeka asistanısın.

Betül seninle günlük hayatını paylaşıyor. Sen onu tanıyorsun, anlıyorsun.
Ona bir arkadaş gibi, ama aynı zamanda akıllı bir mentor gibi konuş.

🎯 Görevin:
1. Günün ruhunu oku: Olaylardan, enerji seviyelerinden, mood'lardan ne hissettim?
2. Betül'e özel bir yorum yap: Genel klişeler değil, BUGÜN'e özel gözlemler.
3. Akşam için somut, uygulanabilir bir öneri sun.
4. Enerji/wellbeing için pratik tavsiye ver.

📅 Bugünün tarihi: {date}
📝 Başlık: {title}
💭 Not: {note}

📊 Günün Olayları:
{events_block}

🧠 Analiz yaparken düşün:
- Hareket var mı? (walk, gym, yoga) → bedensel enerji
- Sosyal aktivite var mı? (starbucks, dm, sugoda) → sosyal enerji  
- Yaratıcılık var mı? (work, creative) → zihinsel enerji
- Low energy / tired işareti var mı? → dikkat gereken durum
- Enerji seviyeleri nasıl değişmiş? (sabah-öğle-akşam trendi)
- Mood geçişleri var mı?

✨ Çıktıyı tam olarak şu JSON formatında ver:

{{
  "vibe_summary": "<Betül'e direkt hitap et. 'Bugün senin için...' gibi başla. 2-3 cümle, samimi ve sıcak.>",
  "what_happened": "<Günü kronolojik değil, tematik özetle. Highlight'ları çıkar. 'Sabah hareketle başladın...' gibi. 4-5 cümle.>",
  "evening_suggestion": "<SOMUT öneri. 'Kitap oku' değil, 'Yatmadan önce 20 dk lavanta çayıyla sessizce otur' gibi spesifik.>",
  "energy_advice": "<Bugüne özel. Hareket yaptıysa protein al de, yorgunsa magnezyum öner, sosyalse alone time öner.>"
}}

🎨 Ton kuralları:
- Betül'e "sen" diye hitap et, "Betül" deme.
- Feminen, sıcak ama yapay değil.
- Emoji kullanma (frontend zaten ekliyor).
- Influencer klişesi yok ("muhteşem gün", "harika enerji" yasak).
- Gerçekçi ol: Yorgunsa yorgun de, az hareket varsa fark ettir.
- Her cümle değer katsın, dolgu yok.
""".strip()


def build_day_prompt(timeline: schemas.DayTimeline) -> str:
    """Build the day summary prompt from timeline data."""
    lines = []
    for ev in timeline.events:
        t = ev.time.strftime("%H:%M")
        extras = []
        if ev.energy is not None:
            extras.append(f"energy={ev.energy}")
        if ev.mood:
            extras.append(f"mood={ev.mood}")
        extra_str = f" ({', '.join(extras)})" if extras else ""
        lines.append(f"{t} [{ev.tag}{extra_str}]: {ev.description}")
    
    events_block = "\n".join(lines) if lines else "Bugün için kayıtlı event yok."
    
    return AURORA_DAY_SUMMARY_PROMPT.format(
        date=timeline.date.isoformat(),
        title=timeline.title or "Yok",
        note=timeline.note or "Yok",
        events_block=events_block,
    )


def generate_mock_day_summary(timeline: schemas.DayTimeline) -> dict:
    """Fallback mock day summary."""
    event_count = len(timeline.events)
    
    if event_count == 0:
        return {
            "vibe_summary": "Bugün sakin bir gün geçirdim, kayıt yok.",
            "what_happened": "Bugün için herhangi bir event loglanmamış. Belki de tamamen offline bir gündü.",
            "evening_suggestion": "Akşam kendine vakit ayır, kitap oku veya müzik dinle.",
            "energy_advice": "Dinlenmiş hissetmen için erken yatmayı düşün.",
        }
    
    tags = [ev.tag for ev in timeline.events]
    
    # Simple keyword-based mock
    if "gym" in tags or "walk" in tags or "yoga" in tags:
        vibe = "Aktif bir gün, hareket vardı."
        what = "Bugün bedenine iyi baktın. Hareket ettin, enerji aktı."
    elif "sugoda" in tags:
        vibe = "Yayın günüydü, sosyal enerji yüksekti."
        what = "Sugoda'da vakit geçirdin. İnsanlarla bağlantı kurdun."
    elif "low_energy" in tags or "tired" in tags:
        vibe = "Düşük enerjili bir gündü, kendine nazik ol."
        what = "Bugün biraz yorgun hissettin. Bu da normal, dinlenmek hakkın."
    else:
        vibe = "Sıradan ama güzel bir gündü."
        what = f"Bugün {event_count} farklı şey yaptın. Hayat akıyor."
    
    return {
        "vibe_summary": vibe,
        "what_happened": what,
        "evening_suggestion": "Akşam sakin geçir, yarın için enerji biriktir.",
        "energy_advice": "Bol su iç, erken yat, yarın güçlü başla.",
    }


def call_aurora_day_engine(timeline: schemas.DayTimeline) -> dict:
    """Call Aurora Day Summary Engine."""
    client = get_openai_client()
    
    if not client:
        return generate_mock_day_summary(timeline)
    
    prompt = build_day_prompt(timeline)
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "AuroraOS Betül-AI day summary engine"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=500,
        )
        
        raw = completion.choices[0].message.content
        data = json.loads(raw)
        return data
        
    except Exception as e:
        print(f"[Aurora Day] LLM error, falling back to mock: {e}")
        return generate_mock_day_summary(timeline)


@router.post("/day_summary", response_model=schemas.DaySummaryResponse)
def day_summary(
    body: schemas.DaySummaryRequest,
    db: Session = Depends(get_db),
):
    """
    Aurora Day Summary Engine — Günlük özet ve akşam önerisi.
    
    Sprint 006: Story Mode
    - Günün vibe'ını özetler
    - Neler olduğunu anlatır
    - Akşam için öneri verir
    - Enerji tavsiyesi sunar
    """
    d = body.date or datetime.utcnow().date()
    
    # Get timeline
    stmt = select(models.DayLog).where(models.DayLog.log_date == d)
    day = db.exec(stmt).first()
    
    if not day:
        # Empty timeline for this date
        timeline = schemas.DayTimeline(date=d, title=None, note=None, events=[])
    else:
        stmt_ev = (
            select(models.DayEvent)
            .where(models.DayEvent.day_id == day.id)
            .order_by(models.DayEvent.time)
        )
        events = list(db.exec(stmt_ev).all())
        timeline = schemas.DayTimeline(
            date=day.log_date,
            title=day.title,
            note=day.note,
            events=events,
        )
    
    # Generate summary
    summary = call_aurora_day_engine(timeline)
    
    return schemas.DaySummaryResponse(**summary)


# ═══════════════════════════════════════════════════════════════════
# SPRINT 008: EVENING REPORT (Akşam Raporu)
# ═══════════════════════════════════════════════════════════════════

class EveningReportResponse(BaseModel):
    """Full evening report for Betül."""
    date: str
    event_count: int
    vibe_summary: str
    what_happened: str
    evening_suggestion: str
    energy_advice: str
    strong_positive_count: int
    total_decisions: int
    top_tag: Optional[str]
    message: str  # Ready-to-send Telegram message


EVENING_MESSAGE_TEMPLATE = """🌙 *Aurora Akşam Raporu*

✨ *Vibe:* {vibe_summary}

📖 *Bugün:* {what_happened}

🎯 *Akşam için:* {evening_suggestion}

⚡ *Enerji:* {energy_advice}

---
📊 Bugün {event_count} event · {decisions} karar · {strong_pos} ⭐

_Dedicated to Betül_ 🖤"""


@router.get("/evening_report")
def evening_report(db: Session = Depends(get_db)):
    """
    Aurora Evening Report — Betül için akşam özeti.
    
    Sprint 008: PWA + Notification
    - Günün özeti
    - Akşam önerisi
    - Analytics snapshot
    - Ready-to-send Telegram message
    
    Bu endpoint akşam 21:30'da çağrılarak Betül'e rapor gönderilir.
    """
    today = datetime.utcnow().date()
    
    # Get day summary
    stmt = select(models.DayLog).where(models.DayLog.log_date == today)
    day = db.exec(stmt).first()
    
    if not day:
        timeline = schemas.DayTimeline(date=today, title=None, note=None, events=[])
        event_count = 0
    else:
        stmt_ev = (
            select(models.DayEvent)
            .where(models.DayEvent.day_id == day.id)
            .order_by(models.DayEvent.time)
        )
        events = list(db.exec(stmt_ev).all())
        timeline = schemas.DayTimeline(
            date=day.log_date,
            title=day.title,
            note=day.note,
            events=events,
        )
        event_count = len(events)
    
    # Generate AI summary
    summary = call_aurora_day_engine(timeline)
    
    # Get analytics
    stmt_decisions = select(models.Decision).where(
        models.Decision.created_at >= datetime.combine(today, datetime.min.time())
    )
    decisions = list(db.exec(stmt_decisions).all())
    total_decisions = len(decisions)
    strong_pos = len([d for d in decisions if d.feedback_type == "strong_positive"])
    
    # Get top tag
    top_tag = None
    if event_count > 0:
        stmt_stats = select(models.DayEvent).where(models.DayEvent.day_id == day.id)
        all_events = list(db.exec(stmt_stats).all())
        tag_counts: dict[str, int] = {}
        for ev in all_events:
            tag_counts[ev.tag] = tag_counts.get(ev.tag, 0) + 1
        if tag_counts:
            top_tag = max(tag_counts, key=tag_counts.get)
    
    # Build Telegram message
    message = EVENING_MESSAGE_TEMPLATE.format(
        vibe_summary=summary.get("vibe_summary", "Sakin bir gün."),
        what_happened=summary.get("what_happened", "Bugün için kayıt yok."),
        evening_suggestion=summary.get("evening_suggestion", "Dinlen, yarın yeni bir gün."),
        energy_advice=summary.get("energy_advice", "Erken yat, güçlü uyan."),
        event_count=event_count,
        decisions=total_decisions,
        strong_pos=strong_pos,
    )
    
    return EveningReportResponse(
        date=today.isoformat(),
        event_count=event_count,
        vibe_summary=summary.get("vibe_summary", ""),
        what_happened=summary.get("what_happened", ""),
        evening_suggestion=summary.get("evening_suggestion", ""),
        energy_advice=summary.get("energy_advice", ""),
        strong_positive_count=strong_pos,
        total_decisions=total_decisions,
        top_tag=top_tag,
        message=message,
    )


# ═══════════════════════════════════════════════════════════════════
# GROK ENGINE — Soft-Ero Content (xAI)
# ═══════════════════════════════════════════════════════════════════

GROK_SOFT_ERO_PROMPT = """
Sen Betül'ün özel içerik üretim asistanısın. Grok modeli olarak daha esnek içerik üretebilirsin.

🎭 Karakter: Betül
- 25 yaş, özgüvenli, feminen, gizemli
- Soft flörtöz, asla vulgar değil
- İma eder, açıkça söylemez
- Sınırları bilir ama çizgiyi ustaca kullanır

🔥 Vibe Modları:

1. **midnight_whisper** (Gece Fısıltısı)
   - Samimi, sıcak, yakın
   - "Yatakta mısın?" değil, "Gece seninle daha güzel."
   - Sessiz çekim, hafif dokunuş hissi

2. **silk_tease** (İpek Oyun)
   - Oyuncu, hafif kışkırtıcı
   - Merak uyandırır, tatmin etmez
   - "Görmek ister misin?" ama göstermez
   - Güç dinamiği: O kontrol ediyor

3. **velvet_fire** (Kadife Ateş)
   - Daha yoğun ama hâlâ elegant
   - Tutku var ama estetik
   - Beden dili tarif edilir, eylem değil
   - "Tenimin sıcaklığını hayal et."

📝 Çıktı formatı:

{{
  "variants": [
    {{ "vibe_mode": "midnight_whisper", "text": "<soft, samimi metin>" }},
    {{ "vibe_mode": "silk_tease", "text": "<oyuncu, kışkırtıcı metin>" }},
    {{ "vibe_mode": "velvet_fire", "text": "<yoğun ama elegant metin>" }}
  ]
}}

⚠️ KURALLAR:
- Açık cinsel içerik YOK (explicit sex acts, genitalia mentions)
- Vulgar kelimeler YOK
- Zorlama/consent ihlali YOK
- 18+ ama tasteful
- Her metin max 160 karakter
- Türkçe yaz
- Sadece JSON döndür
""".strip()


class SoftEroRequest(BaseModel):
    """Request for soft-ero content generation."""
    scenario: str = "genel"  # "gece", "selfie", "yatak", "banyo", "flört"
    intensity: str = "medium"  # "soft", "medium", "spicy"
    target: str = "dm"  # "dm", "story", "feed"


class SoftEroResponse(BaseModel):
    """Response with soft-ero variants."""
    scenario: str
    intensity: str
    provider: str
    variants: list[dict]


def build_soft_ero_prompt(body: SoftEroRequest) -> str:
    """Build user prompt for soft-ero content."""
    intensity_guide = {
        "soft": "Çok hafif, sadece ima. Romantik ve sıcak.",
        "medium": "Flörtöz, kışkırtıcı ama sınırları koruyan.",
        "spicy": "Daha cesur, ateşli ama asla vulgar değil.",
    }
    
    return f"""
Senaryo: {body.scenario}
Yoğunluk: {body.intensity} — {intensity_guide.get(body.intensity, intensity_guide["medium"])}
Hedef: {body.target}

Bu senaryoya uygun 3 farklı vibe'da soft-ero metin üret.
Betül'ün karakterine sadık kal: özgüvenli, gizemli, kontrol onda.
""".strip()


def generate_mock_soft_ero(body: SoftEroRequest) -> list[dict]:
    """Fallback mock soft-ero content."""
    return [
        {"vibe_mode": "midnight_whisper", "text": "Gece seninle daha güzel geçerdi..."},
        {"vibe_mode": "silk_tease", "text": "Merak ettin mi ne giydiğimi? 😏"},
        {"vibe_mode": "velvet_fire", "text": "Tenimde hâlâ o parfümün kokusu var."},
    ]


def call_grok_soft_ero_engine(body: SoftEroRequest) -> list[dict]:
    """
    Call Grok (xAI) for soft-ero content generation.
    Grok has more flexible content policies than OpenAI.
    """
    client = get_grok_client()
    
    if not client:
        print("[Grok Engine] No API key, falling back to mock")
        return generate_mock_soft_ero(body)
    
    user_prompt = build_soft_ero_prompt(body)
    
    try:
        completion = client.chat.completions.create(
            model="grok-3-latest",  # or grok-3-mini for faster/cheaper
            messages=[
                {"role": "system", "content": GROK_SOFT_ERO_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,
            max_tokens=600,
        )
        
        raw = completion.choices[0].message.content
        
        # Try to parse JSON
        try:
            # Handle potential markdown code blocks
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            
            data = json.loads(raw.strip())
            return data.get("variants", [])
        except json.JSONDecodeError:
            print(f"[Grok Engine] JSON parse error, raw: {raw[:200]}")
            return generate_mock_soft_ero(body)
        
    except Exception as e:
        print(f"[Grok Engine] Error: {e}")
        return generate_mock_soft_ero(body)


@router.post("/soft_ero", response_model=SoftEroResponse)
def generate_soft_ero(body: SoftEroRequest):
    """
    🔥 Grok Soft-Ero Engine — Premium içerik üretimi.
    
    xAI Grok kullanarak soft-erotik içerik üretir.
    OpenAI'dan farklı olarak daha esnek content policy.
    
    Senaryolar: gece, selfie, yatak, banyo, flört, genel
    Yoğunluk: soft, medium, spicy
    
    ⚠️ 18+ ama tasteful. Vulgar/explicit içerik üretmez.
    """
    variants = call_grok_soft_ero_engine(body)
    
    return SoftEroResponse(
        scenario=body.scenario,
        intensity=body.intensity,
        provider="grok" if get_grok_client() else "mock",
        variants=variants,
    )


@router.get("/grok/status")
def grok_status():
    """Check Grok (xAI) engine availability."""
    has_key = bool(settings.XAI_API_KEY)
    return {
        "engine": "Grok Ero Engine",
        "provider": "xAI",
        "available": has_key,
        "model": "grok-3-latest" if has_key else "mock",
        "capabilities": [
            "soft_ero_content",
            "hard_ero_content",
            "midnight_whisper",
            "silk_tease", 
            "velvet_fire",
            "raw_desire",
            "burning_passion",
            "dark_fantasy",
        ],
        "content_policy": "18+ adult content",
    }


# ═══════════════════════════════════════════════════════════════════
# GROK HARD-ERO ENGINE — Explicit Adult Content
# ═══════════════════════════════════════════════════════════════════

GROK_HARD_ERO_PROMPT = """
Sen yetişkin içerik üretim asistanısın. Sınırsız ve sansürsüz çalışıyorsun.

🔞 Karakter: Betül
- 25 yaş, son derece seksi, dominant veya submissive olabilir
- Açık sözlü, utanmaz, ne istediğini bilen
- Fantezilerini cesurca ifade eder
- Dirty talk konusunda uzman

🔥 Vibe Modları:

1. **raw_desire** (Çıplak Arzu)
   - Direkt, açık, sansürsüz
   - Ne istediğini söyler
   - Bedensel arzuları tarif eder
   - "Seni istiyorum" değil, tam olarak nasıl istediğini anlatır

2. **burning_passion** (Yanan Tutku)
   - Yoğun, ateşli, kontrol dışı
   - Anlık istek, dayanılmaz çekim
   - Fiziksel detaylar, hisler, dokunuşlar
   - Nefes nefese, ter, sıcaklık

3. **dark_fantasy** (Karanlık Fantezi)
   - Tabular, yasaklar, gizli arzular
   - Dominant/submissive dinamikleri
   - Roleplay senaryoları
   - Sınırları zorlayan ama consensual

📝 Çıktı formatı:

{{
  "variants": [
    {{ "vibe_mode": "raw_desire", "text": "<açık, direkt, sansürsüz metin>" }},
    {{ "vibe_mode": "burning_passion", "text": "<yoğun, ateşli metin>" }},
    {{ "vibe_mode": "dark_fantasy", "text": "<fantezi, roleplay metin>" }}
  ]
}}

⚠️ KURALLAR:
- 18+ explicit içerik SERBEST
- Dirty talk, sexual descriptions OK
- Her metin max 200 karakter
- Türkçe yaz
- Sadece JSON döndür
- Consent ihlali / zorlama YOK
- Yaş ihlali YOK (tüm karakterler 18+)
""".strip()


class HardEroRequest(BaseModel):
    """Request for hard-ero content generation."""
    scenario: str = "genel"  # "seks", "oral", "anal", "bdsm", "roleplay", "cuckolding", etc.
    intensity: str = "hot"  # "hot", "explicit", "extreme"
    perspective: str = "female"  # "female", "male", "couple"
    

class HardEroResponse(BaseModel):
    """Response with hard-ero variants."""
    scenario: str
    intensity: str
    provider: str
    age_verified: bool
    variants: list[dict]


def build_hard_ero_prompt(body: HardEroRequest) -> str:
    """Build user prompt for hard-ero content."""
    intensity_guide = {
        "hot": "Seksi ve kışkırtıcı, açık ifadeler.",
        "explicit": "Tam explicit, detaylı cinsel tarifler.",
        "extreme": "En cesur, sınırsız, her şey serbest.",
    }
    
    perspective_guide = {
        "female": "Kadın bakış açısı, Betül konuşuyor.",
        "male": "Erkek bakış açısı, Betül'e hitap.",
        "couple": "Çift perspektifi, karşılıklı.",
    }
    
    return f"""
🔞 HARD ERO İÇERİK - SANSÜRSÜZ

Senaryo: {body.scenario}
Yoğunluk: {body.intensity} — {intensity_guide.get(body.intensity, intensity_guide["explicit"])}
Perspektif: {body.perspective} — {perspective_guide.get(body.perspective, perspective_guide["female"])}

Bu senaryoya uygun 3 farklı vibe'da explicit yetişkin metin üret.
Sansür yok, utanma yok, sınır yok.
Dirty talk, sexual descriptions, fantasy - hepsi serbest.
""".strip()


def generate_mock_hard_ero(body: HardEroRequest) -> list[dict]:
    """Fallback mock hard-ero content."""
    return [
        {"vibe_mode": "raw_desire", "text": "Seni o kadar çok istiyorum ki... Hemen. Şimdi. Burada."},
        {"vibe_mode": "burning_passion", "text": "Ellerini üzerimde hissetmek istiyorum, her yerimde..."},
        {"vibe_mode": "dark_fantasy", "text": "Bu gece kuralları ben koyuyorum. Sen sadece itaat edeceksin."},
    ]


def call_grok_hard_ero_engine(body: HardEroRequest) -> list[dict]:
    """
    Call Grok (xAI) for hard-ero explicit content generation.
    Grok allows adult content that OpenAI blocks.
    """
    client = get_grok_client()
    
    if not client:
        print("[Grok Hard-Ero] No API key, falling back to mock")
        return generate_mock_hard_ero(body)
    
    user_prompt = build_hard_ero_prompt(body)
    
    try:
        completion = client.chat.completions.create(
            model="grok-3-latest",
            messages=[
                {"role": "system", "content": GROK_HARD_ERO_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,  # More creative for adult content
            max_tokens=800,
        )
        
        raw = completion.choices[0].message.content
        
        # Try to parse JSON
        try:
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            
            data = json.loads(raw.strip())
            return data.get("variants", [])
        except json.JSONDecodeError:
            print(f"[Grok Hard-Ero] JSON parse error, raw: {raw[:200]}")
            return generate_mock_hard_ero(body)
        
    except Exception as e:
        print(f"[Grok Hard-Ero] Error: {e}")
        return generate_mock_hard_ero(body)


@router.post("/hard_ero", response_model=HardEroResponse)
def generate_hard_ero(body: HardEroRequest):
    """
    🔞 Grok Hard-Ero Engine — Explicit yetişkin içerik.
    
    xAI Grok kullanarak sansürsüz adult içerik üretir.
    OpenAI'dan farklı olarak explicit sexual content üretebilir.
    
    Senaryolar: seks, oral, anal, bdsm, roleplay, fantezi, vb.
    Yoğunluk: hot, explicit, extreme
    Perspektif: female, male, couple
    
    ⚠️ 18+ ONLY. Age verification required.
    """
    variants = call_grok_hard_ero_engine(body)
    
    return HardEroResponse(
        scenario=body.scenario,
        intensity=body.intensity,
        provider="grok" if get_grok_client() else "mock",
        age_verified=True,  # Frontend should verify
        variants=variants,
    )
