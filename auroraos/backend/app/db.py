# backend/app/db.py
from sqlmodel import SQLModel, create_engine, Session
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)


def init_db() -> None:
    from . import models  # ensure models imported
    from .orchestrator import models as orchestrator_models  # orchestrator models
    from .state import models as state_models  # state/government models
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session

