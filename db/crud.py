from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db.models import Company, Transcript, Chunk, Sentiment, VectorIndex
from core.schemas import (
    ChunkCreate,
    TranscriptCreate,
    SentimentBase
)

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="faiss")

# =====================Company CRUD Operations=====================
# Company is the root entity. Name uniqueness is enforced at DB level.
# All company operations cascade to related transcripts and vector indices.

def create_company(db: Session, name: str) -> Company:
    """Create a new company. Raises IntegrityError if name already exists."""
    db_company = Company(name=name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company_by_name(db: Session, name: str) -> Company:
    """Retrieve a company by its name."""
    return db.query(Company).filter(Company.name == name).first()


def get_or_create_company(db: Session, name: str) -> Company:
    """Retrieve a company by its name or create it if it doesn't exist."""
    company = get_company_by_name(db, name)
    if not company:
        company = create_company(db, name)
    return company

def get_all_companies(db: Session) -> list:
    """Retrieve all companies."""
    return db.query(Company).all()

def get_company_by_id(db: Session, company_id: int) -> Company:
    """Retrieve a company by its ID."""
    return db.query(Company).filter(Company.id == company_id).first()

def delete_company(db: Session, company_id: int) -> bool:
    """Delete a company by its ID."""
    company = get_company_by_id(db, company_id)
    if company:
        db.delete(company)
        db.commit()
        return True
    return False


# =====================Transcript CRUD Operations=====================
# Unique constraint (company_id, quarter, year) prevents duplicate transcripts.
# Index on same columns speeds up lookups during batch processing.

def create_transcript(db: Session, company_id: int, company_name: str, quarter: str,
                     year: int, filename: str , raw_text: str ) -> Transcript:
    """Create a new transcript. Raises IntegrityError if (company, quarter, year) already exists."""
    db_transcript = Transcript(
        company_id=company_id,
        company_name=company_name,
        quarter=quarter,
        year=year,
        filename=filename,
        raw_text=raw_text,
        chunk_count=0
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    return db_transcript

def get_transcript_by_id(db: Session, transcript_id: int) -> Transcript:
    """Retrieve a transcript by its ID."""
    return db.query(Transcript).filter(Transcript.id == transcript_id).first()

def get_transcripts_by_company(db: Session, company_id: int) -> list:
    """Retrieve all transcripts for a company."""
    return db.query(Transcript).filter(Transcript.company_id == company_id).all()

def get_transcript_by_company_quarter_year(db: Session, company_id: int, quarter: str, year: int) -> Transcript:
    """Retrieve a transcript by company, quarter, and year."""
    return db.query(Transcript).filter(
        and_(
            Transcript.company_id == company_id,
            Transcript.quarter == quarter,
            Transcript.year == year
        )
    ).first()

def update_transcript(db: Session, transcript_id: int, **kwargs) -> Transcript:
    """Update a transcript."""
    transcript = get_transcript_by_id(db, transcript_id)
    if transcript:
        for key, value in kwargs.items():
            if hasattr(transcript, key):
                setattr(transcript, key, value)
        db.commit()
        db.refresh(transcript)
        return transcript
    return transcript

def delete_transcript(db: Session, transcript_id: int) -> bool:
    """Delete a transcript by its ID."""
    transcript = get_transcript_by_id(db, transcript_id)
    if transcript:
        db.delete(transcript)
        db.commit()
        return True
    return False


# =====================Chunk CRUD Operations=====================
# Each chunk stores a text segment with metadata (speaker, role, section).
# Direct company_id link enables cross-company searches without traversing transcripts.

def create_chunk(db: Session, transcript_id: int, company_id: int, quarter: str,
                speaker: str , role: str , section: str , text: str ) -> Chunk:
    """Create a new chunk. Links to transcript and company for flexible querying."""
    db_chunk = Chunk(
        transcript_id=transcript_id,
        company_id=company_id,
        quarter=quarter,
        speaker=speaker,
        role=role,
        section=section,
        text=text
    )
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

def get_chunk_by_id(db: Session, chunk_id: int) -> Chunk:
    """Retrieve a chunk by its ID."""
    return db.query(Chunk).filter(Chunk.id == chunk_id).first()

def get_chunks_by_transcript(db: Session, transcript_id: int) -> list:
    """Retrieve all chunks for a transcript."""
    return db.query(Chunk).filter(Chunk.transcript_id == transcript_id).all()

def get_chunks_by_company(db: Session, company_id: int) -> list:
    """Retrieve all chunks for a company."""
    return db.query(Chunk).filter(Chunk.company_id == company_id).all()

def update_chunk(db: Session, chunk_id: int, **kwargs) -> Chunk:
    """Update a chunk."""
    chunk = get_chunk_by_id(db, chunk_id)
    if chunk:
        for key, value in kwargs.items():
            if hasattr(chunk, key):
                setattr(chunk, key, value)
        db.commit()
        db.refresh(chunk)
        return chunk
    return chunk

def delete_chunk(db: Session, chunk_id: int) -> bool:
    """Delete a chunk by its ID."""
    chunk = get_chunk_by_id(db, chunk_id)
    if chunk:
        db.delete(chunk)
        db.commit()
        return True
    return False


# =====================Sentiment CRUD Operations=====================
# One-to-one relationship with chunk. Unique on chunk_id ensures one sentiment per chunk.
# Score ranges from -1.0 (negative) to 1.0 (positive). Deleted when parent chunk deleted.

def create_sentiment(db: Session, chunk_id: int, score: float, label: str, confidence: float) -> Sentiment:
    """Create sentiment record for a chunk. Raises IntegrityError if chunk already has sentiment."""
    db_sentiment = Sentiment(
        chunk_id=chunk_id,
        score=score,
        label=label,
        confidence=confidence
    )
    db.add(db_sentiment)
    db.commit()
    db.refresh(db_sentiment)
    return db_sentiment

def get_sentiment_by_chunk(db: Session, chunk_id: int) -> Sentiment:
    """Retrieve sentiment by chunk ID."""
    return db.query(Sentiment).filter(Sentiment.chunk_id == chunk_id).first()

def update_sentiment(db: Session, chunk_id: int, **kwargs) -> Sentiment:
    """Update sentiment data."""
    sentiment = get_sentiment_by_chunk(db, chunk_id)
    if sentiment:
        for key, value in kwargs.items():
            if hasattr(sentiment, key) and key != "chunk_id":
                setattr(sentiment, key, value)
        db.commit()
        db.refresh(sentiment)
        return sentiment
    return sentiment

def delete_sentiment(db: Session, chunk_id: int) -> bool:
    """Delete sentiment by chunk ID."""
    sentiment = get_sentiment_by_chunk(db, chunk_id)
    if sentiment:
        db.delete(sentiment)
        db.commit()
        return True
    return False


# =====================VectorIndex CRUD Operations=====================
# Metadata store for FAISS/embedding indices. Unique on company_id ensures one index per company.
# chunk_count tracks validation. embedding_model enables index regeneration with different models.

def create_vector_index(db: Session, company_id: int, index_path: str,
                       embedding_model: str, chunk_count: int = 0) -> VectorIndex:
    """Create vector index metadata. Raises IntegrityError if company already has index."""
    db_index = VectorIndex(
        company_id=company_id,
        index_path=index_path,
        embedding_model=embedding_model,
        chunk_count=chunk_count
    )
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return db_index

def get_vector_index_by_company(db: Session, company_id: int) -> VectorIndex:
    """Retrieve vector index by company ID."""
    return db.query(VectorIndex).filter(VectorIndex.company_id == company_id).first()

def update_vector_index(db: Session, company_id: int, **kwargs) -> VectorIndex:
    """Update vector index."""
    vector_index = get_vector_index_by_company(db, company_id)
    if vector_index:
        for key, value in kwargs.items():
            if hasattr(vector_index, key) and key != "company_id":
                setattr(vector_index, key, value)
        db.commit()
        db.refresh(vector_index)
        return vector_index
    return vector_index

def delete_vector_index(db: Session, company_id: int) -> bool:
    """Delete vector index by company ID."""
    vector_index = get_vector_index_by_company(db, company_id)
    if vector_index:
        db.delete(vector_index)
        db.commit()
        return True
    return False
