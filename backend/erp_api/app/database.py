"""SQLAlchemy database session and engine."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()
_is_sqlite = "sqlite" in settings.database_url
_engine_kw: dict = {
    "echo": settings.database_echo,
    "connect_args": {"check_same_thread": False} if _is_sqlite else {},
    "pool_pre_ping": not _is_sqlite,
}
if not _is_sqlite:
    _engine_kw["pool_size"] = 5
    _engine_kw["max_overflow"] = 10
engine = create_engine(settings.database_url, **_engine_kw)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a DB session and closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for use outside FastAPI (e.g. scripts, ML pipeline)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
