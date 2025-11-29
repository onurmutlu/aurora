"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   AuroraOS — Betül'ün Aurasına İthafen                          ║
║   Backend API Server                                             ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import init_db
from .routers import content, ai, analytics, dm, day
from .orchestrator.router import router as orchestrator_router
from .state.router import router as state_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AuroraOS — Betül'e ithaf edilen yapay zekâ sistemi",
        version="0.1.0",
    )

    # CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "https://aurora.siyahkare.com",
            "https://*.siyahkare.com",
            "https://*.ngrok.io",
            "https://*.ngrok-free.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_db()

    app.include_router(content.router, prefix=settings.API_V1_PREFIX)
    app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
    app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
    app.include_router(dm.router, prefix=settings.API_V1_PREFIX)
    app.include_router(day.router, prefix=settings.API_V1_PREFIX)
    
    # 🚀 Orchestrator — FlirtMarket, Telegram, Web entegrasyonu
    app.include_router(orchestrator_router, prefix=f"{settings.API_V1_PREFIX}/orchestrator", tags=["orchestrator"])
    
    # 🏛️ State — Government data (Citizens, Treasury, AI Ops)
    app.include_router(state_router, prefix=f"{settings.API_V1_PREFIX}/state", tags=["state"])

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "project": settings.PROJECT_NAME,
            "message": "Aurora senin enerjinden öğreniyor. ✨",
        }

    return app


app = create_app()

