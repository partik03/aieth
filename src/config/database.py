"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.settings import get_settings
from src.config.constants import DB_CONFIG

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=DB_CONFIG["POOL_SIZE"],
    max_overflow=DB_CONFIG["MAX_OVERFLOW"],
    pool_timeout=DB_CONFIG["POOL_TIMEOUT"],
    pool_recycle=DB_CONFIG["POOL_RECYCLE"],
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine) 