from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from core.config import settings

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcripts = relationship("Transcript", back_populates="company", cascade="all, delete-orphan")
    vector_indices = relationship("VectorIndex", back_populates="company", cascade="all, delete-orphan")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    quarter = Column(String(10), nullable=False)
    year = Column(Integer, nullable=False)
    filename = Column(String(500))
    raw_text = Column(Text)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="transcripts")
    chunks = relationship("Chunk", back_populates="transcript", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_company_quarter_year", "company_id", "quarter", "year"),
        UniqueConstraint("company_id", "quarter", "year", name="uq_company_quarter_year"),
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    quarter = Column(String(10), nullable=False)
    speaker = Column(String(255))
    role = Column(String(100))
    section = Column(String(50))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcript = relationship("Transcript", back_populates="chunks")
    company = relationship("Company")
    sentiment = relationship("Sentiment", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_company_id_quarter", "company_id", "quarter"),
        Index("idx_transcript_id", "transcript_id"),
    )


class Sentiment(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"), unique=True, nullable=False)
    score = Column(Float, nullable=False)  # -1.0 to 1.0
    label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)

    chunk = relationship("Chunk", back_populates="sentiment")


class VectorIndex(Base):
    __tablename__ = "vector_indices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False, index=True)
    index_path = Column(String(500), nullable=False)
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="vector_indices")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default=settings.ROLE_USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"<User(id={self.id}, email={self.email})>"
