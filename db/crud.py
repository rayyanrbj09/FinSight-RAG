from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db.models import Company, Transcript, Chunk, Sentiment, VectorIndex
from core.schemas import (
    ChunkCreate,
    TranscriptCreate,
    SentimentBase
)
# =====================Company CRUD Operations=====================

def create_company(db: Session, name: str) -> Company:
    """Create a new company."""
    db_company = Company(name=name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company_by_name(db: Session, name: str) -> Company:
    """Retrieve a company by its name."""
    return db.query(Company).filter(Company.name == name).first()


def get_or_create_company(db: Session, name: str) ->  Optional[Company]:
    """Retrieve a company by its name or create it if it doesn't exist."""
    company = get_company_by_name(db, name)
    if not company:
        company = create_company(db, name)
    return company

def get_all_companies(db: Session):
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

def update_company(db: Session, company_id: int, new_name: str) -> Company:
    """Update a company's name by its ID."""
    company = get_company_by_id(db, company_id)
    if company:
        company.name = new_name
        db.commit()
        db.refresh(company)
        return company
    return None