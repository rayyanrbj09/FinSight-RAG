from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ==================== Chunk Schemas ====================

class ChunkBase(BaseModel):
    """Base schema for a text chunk."""

    company: str = Field(..., description="Company name")
    quarter: str = Field(..., description="Quarter (e.g. Q1 2024)")
    speaker: str | None = Field(None, description="Speaker name")
    role: str | None = Field(None, description="Speaker role")
    section: str | None = Field(None, description="Transcript section")
    text: str = Field(..., description="Chunk text")


class ChunkMetadata(ChunkBase):
    """Chunk metadata."""

    source: str = Field(..., description="Document source")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    additional_info: dict[str, Any] | None = None


class ChunkCreate(ChunkBase):
    """Create chunk schema."""

    transcript_id: int
    sentiment_score: float | None = None


class ChunkResponse(ChunkBase):
    """Chunk response schema."""

    id: int
    transcript_id: int
    sentiment_score: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Transcript Schemas ====================

class TranscriptBase(BaseModel):
    """Base transcript schema."""

    company: str
    quarter: str
    year: int
    date: datetime
    file_name: str | None = None


class TranscriptCreate(TranscriptBase):
    """Create transcript schema."""

    raw_text: str


class TranscriptResponse(TranscriptBase):
    """Transcript response schema."""

    id: int
    created_at: datetime
    chunk_count: int

    class Config:
        from_attributes = True


# ==================== Sentiment Schemas ====================

class SentimentBase(BaseModel):
    """Base sentiment schema."""

    chunk_id: int

    sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Sentiment score",
    )

    label: str | None = None

    confidence: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
    )


class SentimentResponse(SentimentBase):
    """Sentiment response schema."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Data Ingestion Schemas ====================

class DataIngestionRequest(BaseModel):
    """Transcript ingestion request."""

    company: str
    quarter: str
    year: int
    date: datetime

    file_name: str | None = None
    raw_text: str

    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
    )

    status: str = Field(
        default="pending",
    )


class DataIngestionResponse(BaseModel):
    """Transcript ingestion response."""

    transcript_id: int
    company: str
    quarter: str
    chunk_count: int
    status: str
    created_at: datetime


# ==================== Query Schemas ====================

class QueryRequest(BaseModel):
    """Cross-quarter query request."""

    query: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )

    company: str

    quarters: list[str] = Field(
        default_factory=list,
        description="Empty means all quarters",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class RetrievedChunk(BaseModel):
    """Retrieved chunk schema."""

    chunk_id: int
    quarter: str
    speaker: str | None = None
    section: str | None = None
    text: str
    similarity_score: float


class QueryResponse(BaseModel):
    """Query response schema."""

    query: str
    company: str
    quarters: list[str]

    retrieved_chunks: list[RetrievedChunk] = Field(
        default_factory=list
    )

    analysis: str | None = None

    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


# ==================== Company & Quarter Schemas ====================

class CompanyResponse(BaseModel):
    """Company listing schema."""

    name: str
    transcript_count: int

    available_quarters: list[str] = Field(
        default_factory=list
    )


class QuartersResponse(BaseModel):
    """Quarter listing schema."""

    company: str

    quarters: list[str] = Field(
        default_factory=list
    )


# ==================== Trend Analysis Schemas ====================

class TrendAnalysisRequest(BaseModel):
    """Trend analysis request."""

    company: str

    quarters: list[str] = Field(
        ...,
        min_length=2,
        description="At least 2 quarters required",
    )

    topic: str


class TrendAnalysisResponse(BaseModel):
    """Trend analysis response."""

    company: str
    quarters: list[str]
    topic: str

    trend_description: str

    sentiment_trajectory: dict[str, float]

    key_shifts: list[str]


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """API error response."""

    detail: str
    status_code: int

    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )