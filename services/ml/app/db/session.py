import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from services.ml.app.config import settings

logger = logging.getLogger("football_ml.database")

DATABASE_URL = settings.database_url or os.getenv(
    "DATABASE_URL", "sqlite:///:memory:"
)

# Production-grade SQLAlchemy Engine Configuration
engine_kwargs = {
    "pool_pre_ping": True,  # Verifies connection health before checkout
}

if DATABASE_URL.startswith("sqlite"):
    # SQLite fallback support for local testing/development
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL production pooling settings
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session lifecycle with automatic cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error during API request session: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def db_transaction() -> Generator[Session, None, None]:
    """
    Context manager for transactional operations with automatic commit and rollback.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction failed and rolled back safely: {e}")
        raise
    finally:
        session.close()


def check_database_health() -> dict:
    """
    Performs ping check to verify live database readiness.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "HEALTHY", "database_url": mask_database_url(DATABASE_URL)}
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return {"status": "UNHEALTHY", "error": "Database server unavailable"}


def mask_database_url(url: str) -> str:
    """
    Redacts credentials from database URL string for safe logging.
    """
    if not url:
        return "NOT_CONFIGURED"
    if "@" in url:
        prefix, host_part = url.split("@", 1)
        driver_part = prefix.split("://")[0] if "://" in prefix else "db"
        return f"{driver_part}://*****:*****@{host_part}"
    return url
