import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

# === DATABASE CONFIGURATION ===
# Priority: Environment variable > SQLite (development)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./iot_watering.db"  # Fallback to SQLite for development
)

# Engine configuration with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Test connections before using
    echo=False  # Set to True for SQL debug logging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# === DATABASE SESSION CONTEXT MANAGER ===
@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db():
    """Dependency for FastAPI endpoint injections."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()