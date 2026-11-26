import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import get_current_user
from db.crud import (
    delete_company,
    delete_chunk,
    delete_transcript,
    get_company_by_id,
    get_sentiment_by_chunk,
    get_chunks_by_transcript,
    get_transcript_by_id,
    get_transcripts_by_company,
    get_vector_index_by_company,
    update_transcript,
)
from db.database import get_db
from db.models import Base, Chunk, Company, Sentiment, Transcript, User, VectorIndex
from routes.ingest import router as ingest_router


@pytest.fixture
def authorization_context():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)

    with test_session() as db:
        alice = User(
            email="alice@example.test",
            username="alice",
            full_name="Alice",
            hashed_password="not-used",
        )
        bob = User(
            email="bob@example.test",
            username="bob",
            full_name="Bob",
            hashed_password="not-used",
        )
        db.add_all([alice, bob])
        db.commit()
        db.refresh(alice)
        db.refresh(bob)

    active_user = {"user": alice}
    app = FastAPI()
    app.include_router(ingest_router)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    def override_current_user():
        return active_user["user"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    with TestClient(app) as client:
        yield client, test_session, active_user, alice, bob

    engine.dispose()


def _upload(client: TestClient):
    return client.post(
        "/ingest",
        data={"company": "Acme", "quarter": "Q1", "year": "2025"},
        files={"file": ("call.txt", b"Prepared Remarks\nCEO: Revenue grew.\n", "text/plain")},
    )


def test_transcripts_are_private_and_duplicate_checks_are_per_user(authorization_context):
    client, test_session, active_user, alice, bob = authorization_context

    alice_response = _upload(client)
    assert alice_response.status_code == 201

    active_user["user"] = bob
    bob_response = _upload(client)
    assert bob_response.status_code == 201

    active_user["user"] = alice
    duplicate_response = _upload(client)
    assert duplicate_response.status_code == 409

    with test_session() as db:
        transcripts = db.query(Transcript).order_by(Transcript.owner_user_id).all()
        assert [transcript.owner_user_id for transcript in transcripts] == [alice.id, bob.id]

        company_id = transcripts[0].company_id
        assert [transcript.owner_user_id for transcript in get_transcripts_by_company(
            db, company_id, alice.id
        )] == [alice.id]
        assert get_transcript_by_id(db, transcripts[0].id, bob.id) is None


def test_users_cannot_update_or_delete_another_users_transcript_or_chunks(authorization_context):
    client, test_session, _, alice, bob = authorization_context
    response = _upload(client)
    assert response.status_code == 201
    transcript_id = response.json()["transcript_id"]

    with test_session() as db:
        chunk = db.query(Chunk).filter(Chunk.transcript_id == transcript_id).first()
        assert chunk is not None
        assert get_chunks_by_transcript(db, transcript_id, bob.id) == []
        assert update_transcript(
            db,
            transcript_id,
            bob.id,
            company_name="Changed by another user",
        ) is None
        assert delete_transcript(db, transcript_id, bob.id) is False
        assert delete_chunk(db, chunk.id, bob.id) is False

        assert get_transcript_by_id(db, transcript_id, alice.id) is not None
        assert get_chunks_by_transcript(db, transcript_id, alice.id)


def test_company_deletion_does_not_remove_another_users_corpus(authorization_context):
    client, test_session, active_user, alice, bob = authorization_context
    assert _upload(client).status_code == 201

    active_user["user"] = bob
    assert _upload(client).status_code == 201

    with test_session() as db:
        company_id = db.query(Transcript.company_id).first()[0]
        alice_transcript = (
            db.query(Transcript)
            .filter(Transcript.owner_user_id == alice.id)
            .first()
        )
        bob_transcript = (
            db.query(Transcript)
            .filter(Transcript.owner_user_id == bob.id)
            .first()
        )

        assert delete_company(db, company_id, alice.id) is True
        assert get_transcript_by_id(db, alice_transcript.id, alice.id) is None
        assert get_transcript_by_id(db, bob_transcript.id, bob.id) is not None
        assert get_company_by_id(db, company_id) is not None


def test_legacy_records_without_an_owner_are_not_visible(authorization_context):
    _, test_session, _, alice, _ = authorization_context

    with test_session() as db:
        company = Company(name="Legacy Co")
        db.add(company)
        db.flush()
        transcript = Transcript(
            owner_user_id=None,
            company_id=company.id,
            company_name=company.name,
            quarter="Q1",
            year=2024,
            raw_text="Legacy content",
        )
        db.add(transcript)
        db.flush()
        chunk = Chunk(
            transcript_id=transcript.id,
            company_id=company.id,
            quarter="Q1",
            text="Legacy chunk",
        )
        db.add(chunk)
        db.flush()
        db.add(Sentiment(chunk_id=chunk.id, score=0.0, label="neutral", confidence=1.0))
        db.add(
            VectorIndex(
                owner_user_id=None,
                company_id=company.id,
                index_path="legacy.index",
                embedding_model="test-model",
            )
        )
        db.commit()

        assert get_transcript_by_id(db, transcript.id, alice.id) is None
        assert get_transcripts_by_company(db, company.id, alice.id) == []
        assert get_chunks_by_transcript(db, transcript.id, alice.id) == []
        assert get_sentiment_by_chunk(db, chunk.id, alice.id) is None
        assert get_vector_index_by_company(db, company.id, alice.id) is None
