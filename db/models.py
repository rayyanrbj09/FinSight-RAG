from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Company(Base):
    """Root entity for all financial data. Each company is independent with its own
    transcripts and vector indices. Cascading deletes ensure cleanup when company removed."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transcripts = relationship("Transcript", back_populates="company", cascade="all, delete-orphan")
    vector_indices = relationship("VectorIndex", back_populates="company", cascade="all, delete-orphan")


class Transcript(Base):
    """Represents a single earnings call transcript for a company.
    Unique constraint on (company_id, quarter, year) prevents duplicate transcripts.
    Index on same columns speeds up lookups by quarter/year for batch processing."""
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
    """Text segments extracted from transcripts, tagged with metadata (speaker, role, section).
    Direct company_id link enables searching across all company chunks without traversing transcript.
    One-to-one relationship with Sentiment (each chunk has max one sentiment record)."""
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
    """Sentiment analysis results for a chunk. Unique on chunk_id enforces one sentiment per chunk.
    Score range: -1.0 (negative) to 1.0 (positive). Deleted when parent chunk deleted."""
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id"), unique=True, nullable=False)
    score = Column(Float, nullable=False)
    label = Column(String(20))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunk = relationship("Chunk", back_populates="sentiment")


class VectorIndex(Base):
    """Stores embedding index metadata per company. Unique on company_id ensures one vector
    index per company. Tracks chunk_count for validation and embedding model used for regeneration."""
    __tablename__ = "vector_indices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False, index=True)
    index_path = Column(String(500), nullable=False)
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = relationship("Company", back_populates="vector_indices")
