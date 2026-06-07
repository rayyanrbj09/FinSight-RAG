"""Request and response schemas for the API."""

from pydantic import BaseModel, Field
from typing import List, Optional

from datetime import datetime
from typing import Dict, Any,Union, Optional   

# These schemas are used for request validation and response formatting in the API endpoints.

#-------------------Chunk Schemas-------------------#
class chunkBase(BaseModel):
    """The chunk schema represents a piece of text along with its associated metadata."""
    company: str = Field(..., description="Company name associated with the chunk")
    quarter: str = Field(..., description="Quarter associated with the chunk (e.g., Q1 2024)")
    speaker: Optional[str] = Field(default=None, description="Speaker associated with the chunk (if applicable)")
    role: Optional[str] = Field(default=None, description="Role of the speaker (e.g., CEO, CFO)")
    section: Optional[str] = Field(default=None, description="Section of the earnings call (e.g., Introduction, Q&A)")
    text: str = Field(..., description="The actual text content of the chunk")

class chunkMetadata(chunkBase):
    """Metadata for a text chunk, including source information and timestamps."""
    source: str = Field(..., description="Source of the chunk (e.g., document name or URL)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the chunk was created")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, description="Any additional metadata information")

class chunkCreate(chunkBase):
    """Schema for creating a new text chunk."""
    transcript_id: str
    sentiment_score: Optional[float] = Field(default=None, description="Sentiment score for the chunk (if applicable)")

class chunkResponse(chunkBase):
    """Schema for the response when retrieving a text chunk."""
    id: int = Field(..., description="Unique identifier for the chunk")
    transcript_id: str
    sentiment_score: Optional[float] = Field(default=None, description="Sentiment score for the chunk (if applicable)")
    created_at: datetime = Field(..., description="Timestamp when the chunk was created")

    class config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models,enable CRUD operations
        from_attributes = True  # Allow population from ORM attributes


#------------------------------Transcript Schemas------------------------------#
class transcriptBase(BaseModel):
    "Base schema for a transcript, containing common fields for both creation and response."

    company: str = Field(..., description="Company name associated with the transcript")
    quarter: str = Field(..., description="Quarter associated with the transcript (e.g., Q1 2024)")
    year: int = Field(..., description="Year associated with the transcript")
    date: datetime = Field(..., description="Date of the earnings call")
    file_name: Optional[str] = Field(default=None, description="Original file name of the transcript (if applicable)")
    
class transcriptCreate(transcriptBase):
    """Schema for creating a new transcript, inheriting from the base schema."""
    raw_txt : str = Field(..., description="The raw text content of the transcript")

class transcriptResponse(transcriptBase):
    "Schema for the response when retrieving a transcript, including an ID and creation timestamp."
    id: int = Field(..., description="Unique identifier for the transcript")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the transcript was created")
    chunk_count: int = Field(..., description="Number of chunks associated with the transcript")

    class config:
        orm_mode = True  # Enable ORM mode for compatibility with SQLAlchemy models
        from_attributes = True  # Allow population from ORM attributes
