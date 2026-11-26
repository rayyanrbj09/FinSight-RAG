"""Transcript ingestion API route."""

from datetime import datetime
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from core.config import settings
from core.schemas import DataIngestionResponse
from core.security import get_current_user
from db.database import get_db
from db.models import Chunk, Company, Transcript, User
from db.crud import get_transcript_by_company_quarter_year
from services.parser import chunk_text, extract_text


router = APIRouter()


def _parse_quarter(quarter: str, year: int | None) -> tuple[str, int]:
    value = quarter.strip().upper().replace(" ", "")
    match = re.fullmatch(r"Q([1-4])(?:-?([0-9]{4}))?", value)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quarter must use Q1-Q4, optionally with a year (for example Q1-2024)",
        )

    resolved_year = int(match.group(2)) if match.group(2) else year
    if resolved_year is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Year is required when it is not included in the quarter",
        )

    quarter_value = f"Q{match.group(1)}"
    return quarter_value, resolved_year


@router.post("/ingest", response_model=DataIngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_transcript(
    file: UploadFile = File(...),
    company: str = Form(..., min_length=2, max_length=255),
    quarter: str = Form(...),
    year: int | None = Form(default=None, ge=1900, le=2100),
    chunk_size: int = Form(default=0, ge=0, le=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DataIngestionResponse:
    """Parse and persist an earnings-call transcript."""
    filename = file.filename or ""
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if f".{extension}" not in settings.SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Accepted types: {', '.join(settings.SUPPORTED_FILE_TYPES)}",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    resolved_quarter, resolved_year = _parse_quarter(quarter, year)
    company_name = company.strip()

    try:
        raw_text = extract_text(file_bytes, filename)
        if not raw_text:
            raise ValueError("No extractable text was found in the uploaded file")

        parsed_chunks = chunk_text(
            raw_text,
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        if not parsed_chunks:
            raise ValueError("Transcript produced no chunks")
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    db_company = db.query(Company).filter(Company.name == company_name).first()
    if db_company is None:
        db_company = Company(name=company_name)
        db.add(db_company)
        db.flush()
    existing = get_transcript_by_company_quarter_year(
        db,
        db_company.id,
        resolved_quarter,
        resolved_year,
        current_user.id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{company_name} {resolved_quarter}-{resolved_year} has already been ingested",
        )

    try:
        transcript = Transcript(
            owner_user_id=current_user.id,
            company_id=db_company.id,
            company_name=db_company.name,
            quarter=resolved_quarter,
            year=resolved_year,
            filename=filename,
            raw_text=raw_text,
            chunk_count=len(parsed_chunks),
        )
        db.add(transcript)
        db.flush()

        for parsed_chunk in parsed_chunks:
            db.add(
                Chunk(
                    transcript_id=transcript.id,
                    company_id=db_company.id,
                    quarter=resolved_quarter,
                    speaker=parsed_chunk.speaker,
                    role=parsed_chunk.role,
                    section=parsed_chunk.section,
                    text=parsed_chunk.text,
                )
            )

        db.commit()
        db.refresh(transcript)
    except Exception:
        db.rollback()
        raise

    return DataIngestionResponse(
        transcript_id=transcript.id,
        company=db_company.name,
        quarter=f"{resolved_quarter}-{resolved_year}",
        chunk_count=len(parsed_chunks),
        status="completed",
        created_at=transcript.created_at or datetime.utcnow(),
    )
