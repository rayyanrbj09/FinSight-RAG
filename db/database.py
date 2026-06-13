from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from core.config import settings
from db.models import Base

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from settings."""
    return settings.DATABASE_URL


# SQLite-specific settings: check_same_thread=False allows cross-thread access (needed for async).
# StaticPool prevents connection recycling for in-memory DBs. Non-SQLite uses default NullPool.
engine = create_engine(
    get_database_url(),
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {},
    poolclass=StaticPool if "sqlite" in get_database_url() else None,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Dependency for getting database session. Always rolls back on error before closing."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database with all tables defined in Base.metadata."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_all_tables() -> None:
    """Drop all tables. Dangerous operation—use only for testing or reset."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise

def reset_database() -> None:
    """Full reset: drop all tables and recreate schema. Use for dev/testing only."""
    try:
        drop_all_tables()
        init_db()
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise
