import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from services.ml.app.config import settings

logger = logging.getLogger("football_ml.database")

DATABASE_URL = settings.database_url or os.getenv(
    "DATABASE_URL", "sqlite:///:memory:"
)

# SQLite fallback support for local testing/development
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
