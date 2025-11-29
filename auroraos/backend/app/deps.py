# backend/app/deps.py
from .db import get_session
from sqlmodel import Session


def get_db() -> Session:
    yield from get_session()

