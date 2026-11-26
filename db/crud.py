from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from core.security import hash_password, verify_password
from db.models import Company, Transcript, Chunk, Sentiment, VectorIndex, User
from core.schemas import (
    ChunkCreate,
    TranscriptCreate,
    SentimentBase
)

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="faiss")


# =====================User CRUD Operations=====================


def create_user(db: Session, email: str, username: str, password: str, full_name: str) -> User:
    """Create a new user account with hashed password."""
    db_user = User(
        email=email.strip().lower(),
        username=username.strip(),
        full_name=full_name.strip(),
        hashed_password=hash_password(password),
        is_active=True,
        is_verified=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a user by id."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email."""
    return db.query(User).filter(User.email == email.strip().lower()).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetch a user by username."""
    return db.query(User).filter(User.username == username.strip()).first()


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    """Authenticate user using email or username."""
    user = db.query(User).filter(
        or_(
            User.email == identifier.strip().lower(),
            User.username == identifier.strip(),
        )
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


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

def get_all_companies(db: Session) -> list[Company]:
    """Retrieve the shared company metadata directory."""
    return db.query(Company).all()

def get_company_by_id(db: Session, company_id: int) -> Company:
    """Retrieve a company by its ID."""
    return db.query(Company).filter(Company.id == company_id).first()

def delete_company(db: Session, company_id: int, owner_user_id: int) -> bool:
    """Delete only the user's transcripts and index for a company."""
    company = get_company_by_id(db, company_id)
    if company is None:
        return False

    transcripts = (
        db.query(Transcript)
        .filter(
            Transcript.company_id == company_id,
            Transcript.owner_user_id == owner_user_id,
        )
        .all()
    )
    vector_indices = (
        db.query(VectorIndex)
        .filter(
            VectorIndex.company_id == company_id,
            VectorIndex.owner_user_id == owner_user_id,
        )
        .all()
    )
    if not transcripts and not vector_indices:
        return False

    for transcript in transcripts:
        db.delete(transcript)
    for vector_index in vector_indices:
        db.delete(vector_index)

    db.flush()
    has_other_transcripts = (
        db.query(Transcript.id).filter(Transcript.company_id == company_id).first() is not None
    )
    has_other_indices = (
        db.query(VectorIndex.id).filter(VectorIndex.company_id == company_id).first() is not None
    )
    if not has_other_transcripts and not has_other_indices:
        db.delete(company)

    db.commit()
    return True


# =====================Transcript CRUD Operations=====================
# Uniqueness is scoped to the uploader, company, quarter, and year.
# The company/quarter/year index supports transcript lookup.

def create_transcript(
    db: Session,
    owner_user_id: int,
    company_id: int,
    company_name: str,
    quarter: str,
    year: int,
    filename: str,
    raw_text: str,
) -> Transcript:
    """Create a transcript owned by a user."""
    db_transcript = Transcript(
        owner_user_id=owner_user_id,
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


def get_transcript_by_id(db: Session, transcript_id: int, owner_user_id: int) -> Transcript | None:
    """Retrieve a transcript by ID only if it belongs to the user."""
    return (
        db.query(Transcript)
        .filter(Transcript.id == transcript_id, Transcript.owner_user_id == owner_user_id)
        .first()
    )


def get_transcripts_by_company(db: Session, company_id: int, owner_user_id: int) -> list[Transcript]:
    """Retrieve the user's transcripts for a company."""
    return (
        db.query(Transcript)
        .filter(
            Transcript.company_id == company_id,
            Transcript.owner_user_id == owner_user_id,
        )
        .all()
    )


def get_transcript_by_company_quarter_year(
    db: Session,
    company_id: int,
    quarter: str,
    year: int,
    owner_user_id: int,
) -> Transcript | None:
    """Retrieve a user's transcript by company, quarter, and year."""
    return db.query(Transcript).filter(
        and_(
            Transcript.company_id == company_id,
            Transcript.quarter == quarter,
            Transcript.year == year,
            Transcript.owner_user_id == owner_user_id,
        )
    ).first()


def update_transcript(
    db: Session,
    transcript_id: int,
    owner_user_id: int,
    **kwargs,
) -> Transcript | None:
    """Update a transcript only if it belongs to the user."""
    transcript = get_transcript_by_id(db, transcript_id, owner_user_id)
    if transcript:
        for key, value in kwargs.items():
            if hasattr(transcript, key) and key not in {"id", "owner_user_id"}:
                setattr(transcript, key, value)
        db.commit()
        db.refresh(transcript)
        return transcript
    return transcript

def delete_transcript(db: Session, transcript_id: int, owner_user_id: int) -> bool:
    """Delete a transcript only if it belongs to the user."""
    transcript = get_transcript_by_id(db, transcript_id, owner_user_id)
    if transcript:
        db.delete(transcript)
        db.commit()
        return True
    return False


# =====================Chunk CRUD Operations=====================
# Each chunk stores a text segment with metadata (speaker, role, section).
# Direct company_id link enables cross-company searches without traversing transcripts.

def create_chunk(
    db: Session,
    transcript_id: int,
    owner_user_id: int,
    company_id: int,
    quarter: str,
    speaker: str | None,
    role: str | None,
    section: str | None,
    text: str,
) -> Chunk | None:
    """Create a chunk only under a transcript owned by the user."""
    if get_transcript_by_id(db, transcript_id, owner_user_id) is None:
        return None

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

def get_chunk_by_id(db: Session, chunk_id: int, owner_user_id: int) -> Chunk | None:
    """Retrieve a chunk only if its transcript belongs to the user."""
    return (
        db.query(Chunk)
        .join(Transcript, Chunk.transcript_id == Transcript.id)
        .filter(Chunk.id == chunk_id, Transcript.owner_user_id == owner_user_id)
        .first()
    )


def get_chunks_by_transcript(
    db: Session,
    transcript_id: int,
    owner_user_id: int,
) -> list[Chunk]:
    """Retrieve chunks only from a transcript owned by the user."""
    return (
        db.query(Chunk)
        .join(Transcript, Chunk.transcript_id == Transcript.id)
        .filter(
            Chunk.transcript_id == transcript_id,
            Transcript.owner_user_id == owner_user_id,
        )
        .all()
    )


def get_chunks_by_company(db: Session, company_id: int, owner_user_id: int) -> list[Chunk]:
    """Retrieve the user's chunks for a company."""
    return (
        db.query(Chunk)
        .join(Transcript, Chunk.transcript_id == Transcript.id)
        .filter(
            Chunk.company_id == company_id,
            Transcript.owner_user_id == owner_user_id,
        )
        .all()
    )


def update_chunk(
    db: Session,
    chunk_id: int,
    owner_user_id: int,
    **kwargs,
) -> Chunk | None:
    """Update a chunk only if its transcript belongs to the user."""
    chunk = get_chunk_by_id(db, chunk_id, owner_user_id)
    if chunk:
        for key, value in kwargs.items():
            if hasattr(chunk, key) and key not in {"id", "transcript_id", "company_id"}:
                setattr(chunk, key, value)
        db.commit()
        db.refresh(chunk)
        return chunk
    return chunk

def delete_chunk(db: Session, chunk_id: int, owner_user_id: int) -> bool:
    """Delete a chunk only if its transcript belongs to the user."""
    chunk = get_chunk_by_id(db, chunk_id, owner_user_id)
    if chunk:
        db.delete(chunk)
        db.commit()
        return True
    return False


# =====================Sentiment CRUD Operations=====================
# One-to-one relationship with chunk. Unique on chunk_id ensures one sentiment per chunk.
# Score ranges from -1.0 (negative) to 1.0 (positive). Deleted when parent chunk deleted.

def create_sentiment(
    db: Session,
    chunk_id: int,
    owner_user_id: int,
    score: float,
    label: str,
    confidence: float,
) -> Sentiment | None:
    """Create sentiment only for a chunk in the user's corpus."""
    if get_chunk_by_id(db, chunk_id, owner_user_id) is None:
        return None

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

def get_sentiment_by_chunk(
    db: Session,
    chunk_id: int,
    owner_user_id: int,
) -> Sentiment | None:
    """Retrieve sentiment only if its chunk belongs to the user."""
    return (
        db.query(Sentiment)
        .join(Chunk, Sentiment.chunk_id == Chunk.id)
        .join(Transcript, Chunk.transcript_id == Transcript.id)
        .filter(
            Sentiment.chunk_id == chunk_id,
            Transcript.owner_user_id == owner_user_id,
        )
        .first()
    )


def update_sentiment(
    db: Session,
    chunk_id: int,
    owner_user_id: int,
    **kwargs,
) -> Sentiment | None:
    """Update sentiment only for a chunk in the user's corpus."""
    sentiment = get_sentiment_by_chunk(db, chunk_id, owner_user_id)
    if sentiment:
        for key, value in kwargs.items():
            if hasattr(sentiment, key) and key != "chunk_id":
                setattr(sentiment, key, value)
        db.commit()
        db.refresh(sentiment)
        return sentiment
    return sentiment

def delete_sentiment(db: Session, chunk_id: int, owner_user_id: int) -> bool:
    """Delete sentiment only for a chunk in the user's corpus."""
    sentiment = get_sentiment_by_chunk(db, chunk_id, owner_user_id)
    if sentiment:
        db.delete(sentiment)
        db.commit()
        return True
    return False


# =====================VectorIndex CRUD Operations=====================
# Metadata store for FAISS/embedding indices, scoped to the owner and company.
# chunk_count tracks validation. embedding_model enables index regeneration with different models.

def create_vector_index(
    db: Session,
    owner_user_id: int,
    company_id: int,
    index_path: str,
    embedding_model: str,
    chunk_count: int = 0,
) -> VectorIndex:
    """Create vector-index metadata owned by a user."""
    db_index = VectorIndex(
        owner_user_id=owner_user_id,
        company_id=company_id,
        index_path=index_path,
        embedding_model=embedding_model,
        chunk_count=chunk_count
    )
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return db_index

def get_vector_index_by_company(
    db: Session,
    company_id: int,
    owner_user_id: int,
) -> VectorIndex | None:
    """Retrieve vector-index metadata only if it belongs to the user."""
    return (
        db.query(VectorIndex)
        .filter(
            VectorIndex.company_id == company_id,
            VectorIndex.owner_user_id == owner_user_id,
        )
        .first()
    )


def update_vector_index(
    db: Session,
    company_id: int,
    owner_user_id: int,
    **kwargs,
) -> VectorIndex | None:
    """Update vector-index metadata only if it belongs to the user."""
    vector_index = get_vector_index_by_company(db, company_id, owner_user_id)
    if vector_index:
        for key, value in kwargs.items():
            if hasattr(vector_index, key) and key not in {"id", "company_id", "owner_user_id"}:
                setattr(vector_index, key, value)
        db.commit()
        db.refresh(vector_index)
        return vector_index
    return vector_index

def delete_vector_index(db: Session, company_id: int, owner_user_id: int) -> bool:
    """Delete vector-index metadata only if it belongs to the user."""
    vector_index = get_vector_index_by_company(db, company_id, owner_user_id)
    if vector_index:
        db.delete(vector_index)
        db.commit()
        return True
    return False
