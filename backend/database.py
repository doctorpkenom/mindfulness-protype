"""
Database configuration and session management.
Uses SQLAlchemy with SQLite for development (easy to switch to PostgreSQL for production).
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - SQLite for development, can be overridden via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindfulness.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def reset_db():
    """Reset database - drop all tables and recreate."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset successfully")
