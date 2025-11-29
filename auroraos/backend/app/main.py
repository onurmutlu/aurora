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

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "project": settings.PROJECT_NAME,
            "message": "Aurora senin enerjinden öğreniyor. ✨",
        }

    return app


app = create_app()

