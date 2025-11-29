"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Telegram Worker — Real DM Bridge                      ║
║   Telethon client for real Telegram account integration          ║
║                                                                  ║
║   This worker:                                                   ║
║   1. Connects to Betül's real Telegram account (Telethon)        ║
║   2. Listens for incoming DMs                                    ║
║   3. Forwards to AuroraOS /orchestrator/telegram/inbound         ║
║   4. Polls /orchestrator/telegram/outbound for replies           ║
║   5. Sends AI replies back to Telegram users                     ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝

Usage:
    export TELEGRAM_API_ID=your_api_id
    export TELEGRAM_API_HASH=your_api_hash
    export TELEGRAM_SESSION=betul_session
    export AURORA_API_BASE=http://localhost:8001/v1
    
    python -m app.telegram_worker.worker
"""

import os
import asyncio
from datetime import datetime
from typing import Optional

import httpx

# Telethon import (install with: pip install telethon)
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import User
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("⚠️ Telethon not installed. Run: pip install telethon")


# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION", "betul_session")
AURORA_API_BASE = os.getenv("AURORA_API_BASE", "http://localhost:8001/v1")

# Polling interval for outbound messages
OUTBOUND_POLL_INTERVAL = 2  # seconds


# ═══════════════════════════════════════════════════════════════════
# Aurora API Client
# ═══════════════════════════════════════════════════════════════════

class AuroraClient:
    """HTTP client for Aurora orchestrator API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
    
    async def send_inbound(
        self,
        telegram_user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        message: str,
        message_id: Optional[int] = None,
    ) -> dict:
        """Send inbound message to Aurora."""
        async with httpx.AsyncClient() as http:
            payload = {
                "telegram_user_id": telegram_user_id,
                "username": username,
                "first_name": first_name,
                "message": message,
                "message_id": message_id,
            }
            
            response = await http.post(
                f"{self.base_url}/orchestrator/telegram/inbound",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def poll_outbound(self, limit: int = 10) -> list:
        """Poll for outbound messages to send."""
        async with httpx.AsyncClient() as http:
            response = await http.get(
                f"{self.base_url}/orchestrator/telegram/outbound",
                params={"limit": limit},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("messages", [])
    
    async def confirm_delivered(
        self,
        external_user_id: str,
        message_id: int,
    ) -> bool:
        """Confirm message was delivered."""
        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{self.base_url}/orchestrator/telegram/delivered",
                params={
                    "external_user_id": external_user_id,
                    "message_id": message_id,
                },
                timeout=10.0,
            )
            return response.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# Telegram Worker
# ═══════════════════════════════════════════════════════════════════

class TelegramWorker:
    """
    Telegram worker that bridges real DMs to AuroraOS.
    """
    
    def __init__(self):
        if not TELETHON_AVAILABLE:
            raise RuntimeError("Telethon is not installed")
        
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            raise RuntimeError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
        
        self.client = TelegramClient(
            TELEGRAM_SESSION,
            int(TELEGRAM_API_ID),
            TELEGRAM_API_HASH,
        )
        
        self.aurora = AuroraClient(AURORA_API_BASE)
        self._running = False
        
        # Track users we've sent to (for outbound mapping)
        self._user_cache: dict[int, User] = {}
    
    async def start(self):
        """Start the worker."""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS Telegram Worker                                       ║
║   Connecting to Telegram...                                      ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        await self.client.start()
        print("✅ Connected to Telegram")
        
        me = await self.client.get_me()
        print(f"📱 Logged in as: {me.first_name} (@{me.username})")
        print(f"🔗 Aurora API: {AURORA_API_BASE}")
        
        # Register event handlers
        self._register_handlers()
        
        # Start outbound polling task
        self._running = True
        asyncio.create_task(self._outbound_poll_loop())
        
        print("🚀 Worker running. Press Ctrl+C to stop.")
        await self.client.run_until_disconnected()
    
    def _register_handlers(self):
        """Register Telegram event handlers."""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            """Handle incoming DM."""
            # Only handle private messages
            if not event.is_private:
                return
            
            sender = await event.get_sender()
            if not sender or not isinstance(sender, User):
                return
            
            # Skip bots
            if sender.bot:
                return
            
            # Cache user for outbound
            self._user_cache[sender.id] = sender
            
            text = event.raw_text
            if not text:
                return
            
            print(f"📥 Incoming from @{sender.username or sender.id}: {text[:50]}...")
            
            try:
                result = await self.aurora.send_inbound(
                    telegram_user_id=sender.id,
                    username=sender.username,
                    first_name=sender.first_name,
                    message=text,
                    message_id=event.message.id,
                )
                
                routing_mode = result.get("routing_mode", "AI_ONLY")
                print(f"   → Routing: {routing_mode}")
                
                # If AI reply was generated and queued, it will be sent via outbound poll
                if result.get("ai_reply"):
                    print(f"   → AI reply queued")
                
            except Exception as e:
                print(f"❌ Error sending to Aurora: {e}")
    
    async def _outbound_poll_loop(self):
        """Poll for outbound messages and send them."""
        while self._running:
            try:
                messages = await self.aurora.poll_outbound()
                
                for msg in messages:
                    external_user_id = msg.get("external_user_id", "")
                    text = msg.get("text", "")
                    message_id = msg.get("message_id")
                    
                    # Extract Telegram user ID from external_user_id
                    # Format: "tg_123456789"
                    if external_user_id.startswith("tg_"):
                        try:
                            tg_user_id = int(external_user_id[3:])
                        except ValueError:
                            continue
                    else:
                        continue
                    
                    # Send the message
                    try:
                        await self.client.send_message(tg_user_id, text)
                        print(f"📤 Sent to {external_user_id}: {text[:50]}...")
                        
                        # Confirm delivery
                        if message_id:
                            await self.aurora.confirm_delivered(
                                external_user_id=external_user_id,
                                message_id=message_id,
                            )
                            
                    except Exception as e:
                        print(f"❌ Error sending to Telegram: {e}")
                
            except Exception as e:
                print(f"⚠️ Outbound poll error: {e}")
            
            await asyncio.sleep(OUTBOUND_POLL_INTERVAL)
    
    async def stop(self):
        """Stop the worker."""
        self._running = False
        await self.client.disconnect()
        print("👋 Worker stopped")


# ═══════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════

async def main():
    worker = TelegramWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())

