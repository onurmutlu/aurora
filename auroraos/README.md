<p align="center">
  <img src="frontend/public/icons/aurora.svg" width="120" alt="AuroraOS Logo" />
</p>

<h1 align="center">AuroraOS</h1>

<p align="center">
  <strong>Betül's Personal AI Operating System</strong><br/>
  <em>"From the void, her light."</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#telegram-bot">Telegram Bot</a> •
  <a href="#api-reference">API</a> •
  <a href="#roadmap">Roadmap</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react" alt="React" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=flat-square&logo=openai" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram" alt="Telegram" />
</p>

---

## 🌙 What is AuroraOS?

AuroraOS is an **AI-powered personal operating system** designed for content creators and influencers. It learns your unique voice, generates on-brand content, and helps you manage your digital presence across platforms.

Built with love for **Betül** — a system that understands her vibe, learns from her decisions, and becomes more "her" over time.

### Core Philosophy

> **"I'm not an influencer. I'm a vibe."**

- 🎭 **Persona-First**: Every output reflects Betül's authentic voice
- 🧠 **Learning System**: Feedback shapes future generations
- ⚡ **Minimal Friction**: Telegram-first, mobile-optimized
- 🖤 **Dark Aesthetic**: Designed for the void

---

## ✨ Features

### 🎨 Content Generation Engine

Generate Instagram captions, stories, and posts in **3 distinct vibe modes**:

| Mode | Description |
|------|-------------|
| 🌸 **Soft Femme** | Warm, gentle, approachable |
| 😏 **Sweet Sarcasm+** | Playful wit, clever remarks |
| 🖤 **Femme Fatale HD** | Confident, mysterious, powerful |

```
Input: "morning coffee, cozy vibes"

Output:
├── 🌸 "Sabah kahvemi yudumlarken sessizliğin tadını çıkarıyorum."
├── 😏 "Kahve molası dedikleri bu olsa gerek: kendi dünyamda meditasyon!"
└── 🖤 "Kahvemi yudumlarken günün kontrolünü ele alıyorum. 💋"
```

### 💬 DM Reply Assistant

Context-aware reply suggestions that feel authentic:

- Reads conversation history (last 6 messages)
- Uses "Bu çok ben" examples as style references
- Generates 3 vibe variants for each incoming message

### 🎙️ Sugoda Script Generator

Stream scripts for live broadcasts:

- **Intro**: Opening lines to set the mood
- **Mid**: Engagement prompts and talking points  
- **Outro**: Closing statements with call-to-action

### 📖 Story Mode / Daily Timeline

Track your day and get AI-powered insights:

```bash
/log walk sabah yürüyüş 30dk
/log starbucks gizemle sohbet
/log sugoda gece yayını

/day  # Get AI summary with evening suggestions
```

### 📊 Analytics Dashboard

Visual insights into your content performance:

- **Vibe Performance**: Which modes resonate most
- **Feedback Trends**: "Bu çok ben" vs "Asla ben değil"
- **Content Wall**: All approved content, one-click copy
- **Aurora Tavsiyesi**: AI-generated daily recommendations

### 📱 Progressive Web App

- Add to Home Screen
- Offline support
- Push notification ready
- Native-like experience

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM BOT                             │
│                   @aurora_betul_bot                          │
│     /start  /generate  /reply  /sugoda  /log  /day           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   BETÜL CONSOLE                              │
│              aurora.siyahkare.com                            │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │
│  │  Inbox  │  │  Story  │  │  Stats  │                      │
│  └─────────┘  └─────────┘  └─────────┘                      │
│                                                              │
│  • Content Cards with 3 Vibe Variants                        │
│  • Quick Generate Scenarios                                  │
│  • Timeline & Day Summary                                    │
│  • Content Wall & Analytics                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   AURORA ENGINE                              │
│                  FastAPI Backend                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Content    │  │   DM Reply   │  │   Sugoda     │       │
│  │  Generator   │  │   Engine     │  │   Scripts    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Day Summary │  │   Memory     │  │   Feedback   │       │
│  │   Engine     │  │   Context    │  │   Learning   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    OPENAI API                                │
│                  gpt-3.5-turbo                               │
│                                                              │
│           Persona Prompts + JSON Output Mode                 │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, TypeScript |
| **Backend** | FastAPI, SQLModel, Python 3.11+ |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **AI** | OpenAI GPT-3.5-turbo |
| **Bot** | aiogram 3.x |
| **Hosting** | Cloudflare Tunnel |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key
- Telegram Bot Token (from @BotFather)

### 1. Clone & Setup

```bash
git clone https://github.com/siyahkare/auroraos.git
cd auroraos

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment

**Backend** (`backend/.env`):
```env
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./auroraos.db
```

**Bot** (`bot/.env`):
```env
BOT_TOKEN=your-telegram-bot-token
WEBAPP_URL=https://aurora.siyahkare.com
AURORA_API_BASE=https://aurora.siyahkare.com/v1
```

### 3. Run Development Servers

```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Telegram Bot
cd bot && python main.py
```

### 4. Access

- **Console**: http://localhost:5173
- **API**: http://localhost:8001
- **Bot**: https://t.me/aurora_betul_bot

---

## 🤖 Telegram Bot

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + Console button |
| `/console` | Open Betül Console (MiniApp) |
| `/generate [scenario]` | Generate content (e.g., `/generate morning_coffee`) |
| `/reply` | Reply to a message with 3 vibe suggestions |
| `/sugoda [theme]` | Generate stream script |
| `/log [tag] [description]` | Log daily event |
| `/day` | Get AI day summary |
| `/timeline` | View today's events |
| `/evening` | Get evening report |
| `/status` | System status |
| `/help` | Show all commands |

### MiniApp Integration

The bot opens `aurora.siyahkare.com` as a Telegram WebApp:

```python
InlineKeyboardButton(
    text="🌑 AuroraOS — Betül Console",
    web_app=WebAppInfo(url=WEBAPP_URL)
)
```

---

## 📡 API Reference

### Content Generation

```http
POST /v1/ai/generate_batch
Content-Type: application/json

{
  "type": "post",
  "target_channel": "instagram",
  "scenario": "morning_coffee"
}
```

### DM Reply Suggestions

```http
POST /v1/ai/reply_suggestions
Content-Type: application/json

{
  "channel": "telegram",
  "incoming_text": "Merhaba, nasılsın?",
  "context": "telegram:123456789"
}
```

### Day Summary

```http
POST /v1/ai/day_summary
Content-Type: application/json

{
  "date": "2025-11-29"
}
```

### Full API Documentation

Visit `/docs` on your running backend for interactive Swagger documentation.

---

## 🎨 Brand & Design

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| Aurora Lavender | `#AFA3FF` | Primary accent |
| Femme Violet | `#AD5FFF` | Secondary |
| Neural Mint | `#00F5A0` | Success states |
| Onyx Black | `#0A0A0C` | Background |
| Void | `#000000` | Deep background |

### Typography

- **Headers**: Space Grotesk
- **Body**: Inter
- **Accents**: Playfair Display (italic)
- **Code**: JetBrains Mono

### Vibe Modes

```css
--soft-femme: linear-gradient(135deg, #FFB6C1, #AFA3FF);
--sweet-sarcasm: linear-gradient(135deg, #FFD700, #FF69B4);
--femme-fatale: linear-gradient(135deg, #8B0000, #000000);
```

---

## 🗺️ Roadmap

### ✅ Completed (v1.0)

- [x] Content Generation Engine (3 vibes)
- [x] DM Reply Assistant (context-aware)
- [x] Sugoda Script Generator
- [x] Story Mode / Timeline
- [x] Feedback Learning System
- [x] Telegram Bot Integration
- [x] PWA Support
- [x] Cloudflare Tunnel Deployment

### 🚧 In Progress (v1.1)

- [ ] Campaign Layer (multi-day planning)
- [ ] Assistant UI (chat-based planning)
- [ ] Instagram API Integration
- [ ] Push Notifications

### 🔮 Future (v2.0)

- [ ] Multi-tenant Support
- [ ] Performance Analytics Integration
- [ ] Voice-to-Content
- [ ] AI Image Generation
- [ ] Monetization Features

---

## 🤝 Contributing

AuroraOS is currently a personal project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💜 Acknowledgments

- **Betül** — The muse, the vibe, the reason
- **OpenAI** — For the intelligence layer
- **Cloudflare** — For seamless tunneling
- **Baron Baba** — Architecture & Engineering

---

<p align="center">
  <strong>Dedicated to Betül</strong><br/>
  <em>"Your aura is the system."</em><br/><br/>
  <img src="frontend/public/icons/aurora.svg" width="40" alt="Aurora" />
</p>

<p align="center">
  <sub>Baron Baba © SiyahKare, 2025</sub>
</p>
