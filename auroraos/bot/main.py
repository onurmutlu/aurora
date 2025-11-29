"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Telegram Bot — v1.0                                   ║
║   "Your aura is the system."                                     ║
║                                                                  ║
║   Commands:                                                      ║
║   /start, /console → Open Betül Console WebApp                  ║
║   /generate [scenario] → Create content via Aurora Engine       ║
║   /reply → Context-aware DM reply suggestions                    ║
║   /sugoda [theme] → Generate stream script                       ║
║   /log [tag] [desc] → Log daily event                            ║
║   /timeline → Show today's events                                ║
║   /day → AI-powered day summary                                  ║
║   /evening → Full evening report 🌙                              ║
║   /status → System health + analytics snapshot                   ║
║                                                                  ║
║   Sprint 008: PWA + Evening Report                               ║
║   - Full AI-powered evening summary                              ║
║   - Ready-to-send Telegram message                               ║
║   - Analytics snapshot included                                  ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:5173")
AURORA_API_BASE = os.getenv("AURORA_API_BASE", "http://localhost:8001/v1")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please add it to .env file.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ═══════════════════════════════════════════════════════════════════
# Reply Cache (simple in-memory store for reply variants + metadata)
# Sprint 005: Now stores external_user_id for outgoing message logging
# ═══════════════════════════════════════════════════════════════════

class ReplyContext:
    """Cached reply context for callback handling."""
    def __init__(self, variants: list[str], external_user_id: str = "unknown"):
        self.variants = variants
        self.external_user_id = external_user_id


REPLY_CACHE: dict[int, ReplyContext] = {}


# ═══════════════════════════════════════════════════════════════════
# HTTP Client Helpers
# ═══════════════════════════════════════════════════════════════════

async def aurora_post(path: str, json_body: dict) -> dict:
    """POST request to Aurora backend."""
    url = f"{AURORA_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_body) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"Aurora POST failed: {resp.status}")
            try:
                return await resp.json()
            except Exception:
                return {"raw": text}


async def aurora_get(path: str) -> dict:
    """GET request to Aurora backend."""
    url = f"{AURORA_API_BASE.rstrip('/')}/{path.lstrip('/')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"Aurora GET failed: {resp.status}")
            try:
                return await resp.json()
            except Exception:
                return {"raw": text}


# ═══════════════════════════════════════════════════════════════════
# Keyboard Builders
# ═══════════════════════════════════════════════════════════════════

def build_console_keyboard() -> InlineKeyboardMarkup:
    """Build WebApp button for Betül Console."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌑 AuroraOS — Betül Console",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


def build_scenario_keyboard() -> InlineKeyboardMarkup:
    """Quick scenario buttons for content generation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👗 red_dress", callback_data="gen:red_dress"),
                InlineKeyboardButton(text="🚶 street", callback_data="gen:street"),
            ],
            [
                InlineKeyboardButton(text="💪 gym", callback_data="gen:gym"),
                InlineKeyboardButton(text="☕ coffee", callback_data="gen:coffee"),
            ],
            [
                InlineKeyboardButton(
                    text="🌑 Console'u Aç",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ],
        ]
    )


# ═══════════════════════════════════════════════════════════════════
# /start & /console → WebApp
# ═══════════════════════════════════════════════════════════════════

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Welcome message with Betül Console WebApp button."""
    await message.answer(
        "🖤 *Merhaba Betül.*\n\n"
        "Aurora senin enerjinden öğreniyor.\n"
        "Kararların onu şekillendiriyor.\n\n"
        "_Your aura is the system._",
        parse_mode="Markdown",
        reply_markup=build_console_keyboard(),
    )


@dp.message(Command("console"))
async def cmd_console(message: Message):
    """Shortcut to open Betül Console."""
    await message.answer(
        "🌑 *Betül Console*\n\n"
        "Inbox'ta seni bekleyen içerikler var.\n"
        "Karar ver, Aurora öğrensin.",
        parse_mode="Markdown",
        reply_markup=build_console_keyboard(),
    )


# ═══════════════════════════════════════════════════════════════════
# /generate [scenario] → Aurora Engine
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("generate"))
async def cmd_generate(message: Message):
    """Generate content via Aurora Engine."""
    parts = message.text.split(" ", 1)
    scenario = parts[1].strip() if len(parts) > 1 else "default"
    
    working_msg = await message.answer(
        f"🧠 *Aurora Engine çalışıyor...*\n\n"
        f"• scenario: `{scenario}`",
        parse_mode="Markdown",
    )
    
    try:
        payload = {
            "type": "post",
            "target_channel": "instagram",
            "count": 1,
            "scenario": scenario,
        }
        data = await aurora_post("/ai/generate_batch", payload)
        content_id = data.get("content_item_id")
        variants_count = data.get("variants_count", 3)
        
        await working_msg.edit_text(
            f"✨ *Yeni içerik üretildi!*\n\n"
            f"• content\\_id: `{content_id}`\n"
            f"• variants: `{variants_count}` adet\n\n"
            f"Betül Console'da *Inbox* kısmında görebilirsin.",
            parse_mode="Markdown",
            reply_markup=build_console_keyboard(),
        )
    except Exception as e:
        await working_msg.edit_text(
            f"❌ *Aurora Engine hata verdi*\n\n`{e}`",
            parse_mode="Markdown",
        )


@dp.message(Command("quick"))
async def cmd_quick(message: Message):
    """Show quick scenario buttons."""
    await message.answer(
        "🎯 *Hızlı Senaryo Seç*\n\n"
        "Bir senaryoya tıkla, Aurora içerik üretsin.",
        parse_mode="Markdown",
        reply_markup=build_scenario_keyboard(),
    )


@dp.callback_query(F.data.startswith("gen:"))
async def callback_generate(callback: CallbackQuery):
    """Handle quick generate buttons."""
    scenario = callback.data.replace("gen:", "")
    
    await callback.answer(f"🧠 {scenario} üretiliyor...")
    
    try:
        payload = {
            "type": "post",
            "target_channel": "instagram",
            "count": 1,
            "scenario": scenario,
        }
        data = await aurora_post("/ai/generate_batch", payload)
        content_id = data.get("content_item_id")
        
        await callback.message.answer(
            f"✨ *{scenario}* içeriği hazır!\n\n"
            f"• content\\_id: `{content_id}`\n\n"
            f"Console'dan onaylayabilirsin.",
            parse_mode="Markdown",
            reply_markup=build_console_keyboard(),
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ Hata: `{e}`",
            parse_mode="Markdown",
        )


# ═══════════════════════════════════════════════════════════════════
# SPRINT 004: /reply → DM Reply Suggestions
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("reply"))
async def cmd_reply(message: Message):
    """
    DM Reply Suggestions (Sprint 005: Context-Aware).
    
    Usage:
    1. Reply to a message with /reply
    2. Bot will generate 3 vibe-based response suggestions
    3. Pick one and copy-paste it
    
    Sprint 005 Updates:
    - Detects external_user_id from the replied message
    - Logs incoming messages for context
    - Passes conversation history to Aurora for better replies
    """
    global REPLY_CACHE
    
    # Check if replying to a message
    if not message.reply_to_message:
        await message.answer(
            "💬 *DM Reply*\n\n"
            "Cevap vermek istediğin mesaja reply at, sonra `/reply` yaz.\n\n"
            "_Aurora artık konuşmanın bütününü hatırlıyor!_ 🧠",
            parse_mode="Markdown",
        )
        return
    
    # Get the incoming message text
    target = message.reply_to_message
    incoming_text = target.text or target.caption or ""
    
    if not incoming_text.strip():
        await message.answer("Bu mesajda metin bulamadım. Sadece text/caption destekliyorum.")
        return
    
    # ═══════════════════════════════════════════════════════════════════
    # Sprint 005: Detect external user ID
    # ═══════════════════════════════════════════════════════════════════
    target_user = target.from_user
    if target_user and not target_user.is_bot:
        external_user_id = str(target_user.id)
    else:
        # Fallback: use a hash of the text if we can't identify the user
        external_user_id = "unknown"
    
    # Show "thinking" message
    thinking_msg = await message.answer(
        "🧠 *Aurora düşünüyor...*\n\n"
        f"_\"{incoming_text[:50]}{'...' if len(incoming_text) > 50 else ''}\"_\n\n"
        f"_Konuşma geçmişi kontrol ediliyor..._",
        parse_mode="Markdown",
    )
    
    # ═══════════════════════════════════════════════════════════════════
    # Sprint 005: Log incoming message for context
    # ═══════════════════════════════════════════════════════════════════
    try:
        await aurora_post("/dm/log", {
            "channel": "telegram",
            "external_user_id": external_user_id,
            "direction": "incoming",
            "text": incoming_text,
        })
    except Exception as e:
        # Log hata verirse bile reply engine'i bozma
        print(f"[Bot] DM log error (incoming): {e}")
    
    try:
        # ═══════════════════════════════════════════════════════════════════
        # Sprint 005: Call Aurora Reply Engine with context
        # ═══════════════════════════════════════════════════════════════════
        payload = {
            "channel": "telegram",
            "incoming_text": incoming_text,
            # Context format: "channel:external_user_id"
            "context": f"telegram:{external_user_id}",
        }
        data = await aurora_post("/ai/reply_suggestions", payload)
        variants = data.get("variants", [])
        
        if not variants:
            await thinking_msg.edit_text("Cevap üretemedim. Tekrar dene.")
            return
        
        # ═══════════════════════════════════════════════════════════════════
        # Sprint 005: Store variants with external_user_id in cache
        # ═══════════════════════════════════════════════════════════════════
        REPLY_CACHE[thinking_msg.message_id] = ReplyContext(
            variants=[v.get("text", "") for v in variants],
            external_user_id=external_user_id,
        )
        
        # Build response with buttons
        context_used = data.get("context_used", False)
        context_count = data.get("context_messages", 0)
        style_count = data.get("style_examples_used", 0)
        
        lines = ["✨ *Betül için 3 cevap önerisi:*\n"]
        
        # Show context info if available
        if context_used or style_count > 0:
            context_info = []
            if context_count > 0:
                context_info.append(f"📜 {context_count} mesaj")
            if style_count > 0:
                context_info.append(f"💫 {style_count} stil örneği")
            lines.append(f"_Context: {', '.join(context_info)} kullanıldı_\n")
        
        kb = InlineKeyboardBuilder()
        
        for idx, v in enumerate(variants):
            vibe = v.get("vibe_mode", "unknown")
            text = v.get("text", "")
            
            # Add to message
            if vibe == "soft_femme":
                emoji = "🩷"
                label = "Soft"
            elif vibe == "sweet_sarcasm_plus":
                emoji = "😏"
                label = "Sarcastic"
            else:
                emoji = "🖤"
                label = "Femme"
            
            lines.append(f"{emoji} *{vibe}:*")
            lines.append(f"`{text}`\n")
            
            # Add button
            kb.button(
                text=f"{emoji} {label}",
                callback_data=f"reply:{thinking_msg.message_id}:{idx}",
            )
        
        kb.adjust(3)
        
        lines.append("_Birini seç, Aurora onu hatırlayacak._")
        
        await thinking_msg.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=kb.as_markup(),
        )
        
    except Exception as e:
        await thinking_msg.edit_text(
            f"❌ *Aurora Reply hata verdi*\n\n`{e}`",
            parse_mode="Markdown",
        )


@dp.callback_query(F.data.startswith("reply:"))
async def callback_reply_choice(callback: CallbackQuery):
    """
    Handle reply choice buttons.
    
    Sprint 005: Now logs the chosen reply as outgoing message.
    """
    global REPLY_CACHE
    
    try:
        parts = callback.data.split(":")
        msg_id = int(parts[1])
        idx = int(parts[2])
    except (ValueError, IndexError):
        await callback.answer("Hata oluştu.")
        return
    
    # Get cached context
    if msg_id not in REPLY_CACHE:
        await callback.answer("Süre dolmuş, tekrar /reply dene.")
        return
    
    ctx = REPLY_CACHE[msg_id]
    if idx < 0 or idx >= len(ctx.variants):
        await callback.answer("Hata.")
        return
    
    chosen = ctx.variants[idx]
    
    # Determine which vibe was selected
    vibe_modes = ["soft_femme", "sweet_sarcasm_plus", "femme_fatale_hd"]
    selected_vibe = vibe_modes[idx] if idx < len(vibe_modes) else None
    
    await callback.answer("Seçildi ✅")
    
    # ═══════════════════════════════════════════════════════════════════
    # Sprint 005: Log the chosen reply as outgoing message
    # ═══════════════════════════════════════════════════════════════════
    try:
        await aurora_post("/dm/log", {
            "channel": "telegram",
            "external_user_id": ctx.external_user_id,
            "direction": "outgoing",
            "text": chosen,
            "vibe_mode": selected_vibe,
        })
    except Exception as e:
        # Log hata verirse bile devam et
        print(f"[Bot] DM log error (outgoing): {e}")
    
    # Send the chosen reply as a separate message for easy copying
    await callback.message.answer(
        f"📝 *Kopyala ve gönder:*\n\n`{chosen}`\n\n"
        f"_Bu cevap Aurora'nın hafızasına kaydedildi._ 🧠",
        parse_mode="Markdown",
    )
    
    # Clean up cache
    del REPLY_CACHE[msg_id]


# ═══════════════════════════════════════════════════════════════════
# SPRINT 004: /sugoda → Stream Script Generator
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("sugoda"))
async def cmd_sugoda(message: Message):
    """
    Sugoda Stream Script Generator.
    
    Usage:
    /sugoda gece slow
    /sugoda sabah enerjik
    /sugoda chill lo-fi
    """
    parts = message.text.split(" ", 1)
    
    if len(parts) == 1:
        await message.answer(
            "🎙 *Sugoda Script Generator*\n\n"
            "Kullanım:\n"
            "`/sugoda gece slow`\n"
            "`/sugoda sabah enerjik`\n"
            "`/sugoda chill lo-fi`\n\n"
            "_Tema yaz, Aurora sana yayın script'i hazırlasın._",
            parse_mode="Markdown",
        )
        return
    
    theme = parts[1].strip()
    
    working_msg = await message.answer(
        f"🎙 *Sugoda script üretiliyor...*\n\n"
        f"• tema: `{theme}`",
        parse_mode="Markdown",
    )
    
    try:
        payload = {"theme": theme, "length": "short"}
        data = await aurora_post("/ai/sugoda_script", payload)
        scripts = data.get("scripts", [])
        
        if not scripts:
            await working_msg.edit_text("Script üretemedim. Tekrar dene.")
            return
        
        lines = [f"✨ *Sugoda Script — {theme}*\n"]
        
        for block in scripts:
            label = block.get("label", "")
            block_lines = block.get("lines", [])
            
            if label == "intro":
                emoji = "🎬"
            elif label == "mid":
                emoji = "💬"
            else:
                emoji = "👋"
            
            lines.append(f"\n{emoji} *{label.upper()}:*")
            for line in block_lines:
                lines.append(f"• _{line}_")
        
        lines.append("\n🖤 _Yayında başarılar!_")
        
        await working_msg.edit_text(
            "\n".join(lines),
            parse_mode="Markdown",
        )
        
    except Exception as e:
        await working_msg.edit_text(
            f"❌ *Sugoda script hata verdi*\n\n`{e}`",
            parse_mode="Markdown",
        )


# ═══════════════════════════════════════════════════════════════════
# /status → Health + Analytics
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Show AuroraOS system status and analytics."""
    
    try:
        health = await aurora_get("/")
    except Exception as e:
        await message.answer(
            f"❌ *Backend ulaşılamıyor*\n\n`{e}`",
            parse_mode="Markdown",
        )
        return
    
    try:
        engine = await aurora_get("/ai/status")
    except Exception:
        engine = None
    
    try:
        analytics = await aurora_get("/analytics/summary")
    except Exception:
        analytics = None
    
    lines = [
        "🖤 *AuroraOS Status*",
        "",
        f"• backend: `{health.get('status', 'unknown')}`",
        f"• project: `{health.get('project', 'AuroraOS')}`",
    ]
    
    if engine:
        lines.append(f"• engine: `{engine.get('status', 'unknown')}`")
        lines.append(f"• model: `{engine.get('model', 'unknown')}`")
        llm_status = "✅ aktif" if engine.get("llm_enabled") else "⚠️ mock"
        lines.append(f"• llm: {llm_status}")
    
    if analytics:
        total = analytics.get("total_decisions", 0)
        content = analytics.get("total_content", 0)
        strong_pos = next(
            (x["count"] for x in analytics.get("strong_feedback", []) 
             if x["feedback_type"] == "strong_positive"),
            0,
        )
        strong_neg = next(
            (x["count"] for x in analytics.get("strong_feedback", []) 
             if x["feedback_type"] == "strong_negative"),
            0,
        )
        
        lines.append("")
        lines.append("📊 *Analytics*")
        lines.append(f"• toplam içerik: `{content}`")
        lines.append(f"• toplam karar: `{total}`")
        lines.append(f"• ⭐ bu çok ben: `{strong_pos}`")
        lines.append(f"• 🚫 asla ben değil: `{strong_neg}`")
    
    lines.append("")
    lines.append("_Dedicated to Betül_ ✨")
    
    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=build_console_keyboard(),
    )


# ═══════════════════════════════════════════════════════════════════
# SPRINT 006: /log & /day → Story Mode
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("log"))
async def cmd_log(message: Message):
    """
    Log a daily event.
    
    Usage:
    /log walk sabah yürüyüş 30 dk
    /log starbucks gizemle sohbet, vibe iyiydi
    /log sugoda gece yayını, biraz yorgun ama keyifli
    /log low_energy bugün enerjim düşük
    """
    parts = message.text.split(" ", 2)
    
    if len(parts) < 3:
        await message.answer(
            "📝 *Event Log*\n\n"
            "Kullanım: `/log <tag> <açıklama>`\n\n"
            "*Örnek tag'ler:*\n"
            "• `walk`, `gym`, `yoga` — hareket\n"
            "• `starbucks`, `coffee`, `lunch` — sosyal\n"
            "• `sugoda`, `dm`, `work` — aktivite\n"
            "• `low_energy`, `tired` — enerji\n"
            "• `happy`, `calm`, `anxious` — mood\n\n"
            "*Örnekler:*\n"
            "`/log walk sabah yürüyüş 30 dk`\n"
            "`/log sugoda gece yayını, keyifliydi`\n"
            "`/log low_energy bugün yorgunum`",
            parse_mode="Markdown",
        )
        return
    
    tag = parts[1].strip().lower()
    description = parts[2].strip()
    
    try:
        payload = {
            "tag": tag,
            "description": description,
            "energy": None,
            "mood": None,
        }
        data = await aurora_post("/day/event", payload)
        event_count = len(data.get("events", []))
        
        await message.answer(
            f"✅ *Log kaydedildi*\n\n"
            f"• tag: `{tag}`\n"
            f"• tarih: `{data.get('date')}`\n"
            f"• bugün toplam: `{event_count}` event\n\n"
            f"_/day ile günü özetle._",
            parse_mode="Markdown",
        )
    except Exception as e:
        await message.answer(
            f"❌ *Log kaydı hata*\n\n`{e}`",
            parse_mode="Markdown",
        )


@dp.message(Command("day"))
async def cmd_day(message: Message):
    """
    Get AI-powered day summary.
    
    Usage:
    /day → Today's summary
    /day 2025-11-29 → Specific date
    """
    parts = message.text.split(" ", 1)
    
    if len(parts) == 1:
        payload = {"date": None}  # Today
        date_str = "bugün"
    else:
        payload = {"date": parts[1].strip()}
        date_str = parts[1].strip()
    
    working_msg = await message.answer(
        f"🧠 *Aurora {date_str}ü okuyor...*",
        parse_mode="Markdown",
    )
    
    try:
        summary = await aurora_post("/ai/day_summary", payload)
        
        txt = (
            "🖤 *AuroraOS Story Mode*\n\n"
            f"✨ *Vibe:* {summary.get('vibe_summary', '')}\n\n"
            f"📖 *Bugün:* {summary.get('what_happened', '')}\n\n"
            f"🌙 *Akşam için:* {summary.get('evening_suggestion', '')}\n\n"
            f"⚡ *Enerji:* {summary.get('energy_advice', '')}"
        )
        
        await working_msg.edit_text(txt, parse_mode="Markdown")
        
    except Exception as e:
        await working_msg.edit_text(
            f"❌ *Day summary hata*\n\n`{e}`",
            parse_mode="Markdown",
        )


@dp.message(Command("timeline"))
async def cmd_timeline(message: Message):
    """
    Show today's event timeline.
    
    Usage:
    /timeline → Today
    """
    try:
        data = await aurora_get("/day/timeline")
        events = data.get("events", [])
        
        if not events:
            await message.answer(
                "📜 *Bugünün Timeline'ı*\n\n"
                "_Henüz event yok._\n\n"
                "`/log <tag> <açıklama>` ile event ekle.",
                parse_mode="Markdown",
            )
            return
        
        lines = [
            f"📜 *Timeline — {data.get('date')}*",
            "",
        ]
        
        if data.get("title"):
            lines.append(f"📌 *{data.get('title')}*\n")
        
        for ev in events:
            time_str = ev.get("time", "")[:16].split("T")[1] if "T" in ev.get("time", "") else ""
            tag = ev.get("tag", "")
            desc = ev.get("description", "")
            
            # Tag emojis
            tag_emoji = {
                "walk": "🚶", "gym": "💪", "yoga": "🧘",
                "starbucks": "☕", "coffee": "☕", "lunch": "🍽",
                "sugoda": "🎙", "dm": "💬", "work": "💼",
                "low_energy": "🪫", "tired": "😴",
                "happy": "😊", "calm": "😌", "anxious": "😰",
            }.get(tag, "•")
            
            lines.append(f"`{time_str}` {tag_emoji} *{tag}*")
            lines.append(f"  _{desc}_\n")
        
        lines.append("_/day ile Aurora'dan özet al._")
        
        await message.answer("\n".join(lines), parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(
            f"❌ *Timeline hata*\n\n`{e}`",
            parse_mode="Markdown",
        )


# ═══════════════════════════════════════════════════════════════════
# SPRINT 008: /evening → Akşam Raporu
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("evening"))
async def cmd_evening(message: Message):
    """
    Get full evening report from Aurora.
    
    Sprint 008: PWA + Notification
    - Day summary
    - Analytics snapshot
    - Evening suggestions
    - Energy advice
    """
    working_msg = await message.answer(
        "🌙 *Aurora akşam raporunu hazırlıyor...*",
        parse_mode="Markdown",
    )
    
    try:
        report = await aurora_get("/ai/evening_report")
        
        # Send the ready-to-use message
        await working_msg.edit_text(
            report.get("message", "Rapor hazırlanamadı."),
            parse_mode="Markdown",
        )
        
    except Exception as e:
        await working_msg.edit_text(
            f"❌ *Akşam raporu hata*\n\n`{e}`",
            parse_mode="Markdown",
        )


# ═══════════════════════════════════════════════════════════════════
# /help → Command list
# ═══════════════════════════════════════════════════════════════════

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Show available commands."""
    await message.answer(
        "🖤 *AuroraOS v1.0 Komutları*\n\n"
        "*Temel:*\n"
        "`/start` — Hoş geldin mesajı\n"
        "`/console` — Betül Console'u aç\n"
        "`/status` — Sistem durumu\n\n"
        "*İçerik:*\n"
        "`/generate [senaryo]` — Post içeriği üret\n"
        "`/quick` — Hızlı senaryo butonları\n\n"
        "*DM & Yayın:*\n"
        "`/reply` — Mesaja cevap öner (reply at)\n"
        "`/sugoda [tema]` — Yayın script'i üret\n\n"
        "*Story Mode:*\n"
        "`/log <tag> <açıklama>` — Event logla\n"
        "`/timeline` — Günün event'leri\n"
        "`/day` — AI günlük özet\n"
        "`/evening` — Akşam raporu 🌙\n\n"
        "*Tag'ler:*\n"
        "`walk`, `gym`, `starbucks`, `sugoda`, `low_energy`\n\n"
        "_Your aura is the system._",
        parse_mode="Markdown",
    )


# ═══════════════════════════════════════════════════════════════════
# Run Bot
# ═══════════════════════════════════════════════════════════════════

async def main():
    print("╔══════════════════════════════════════════╗")
    print("║   AuroraOS Bot — v1.0 Betül Edition      ║")
    print("║   Full AI + PWA + Evening Reports        ║")
    print("║   Dedicated to Betül ✨                  ║")
    print("╚══════════════════════════════════════════╝")
    print(f"  • WEBAPP_URL: {WEBAPP_URL}")
    print(f"  • AURORA_API: {AURORA_API_BASE}")
    print()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
