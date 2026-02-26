## database.py
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id          = Column(String, primary_key=True, index=True)
    query       = Column(Text, nullable=False)
    filename    = Column(String, nullable=False)
    status      = Column(String, default="pending")   # pending | running | complete | failed
    result      = Column(Text, nullable=True)
    error       = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI routes — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
