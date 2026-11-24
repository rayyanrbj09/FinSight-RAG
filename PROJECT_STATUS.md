# FinSight RAG - Shared Project Guide and Status

**Status assessed:** 2026-11-24
**Purpose:** Shared source of truth for the project goal, current implementation, agreed roadmap, and decisions.

## How we maintain this document

This is a collaboration document, not authorization to change code, provision AWS resources, or create commits. We will update its status, roadmap, and decisions after discussing the change and agreeing on it together. Before making code changes, the guide will explain the goal, affected files, relevant concepts, trade-offs, and validation plan, then wait for approval.

Roadmap items are proposals until we agree to start them. Completed means implemented and verified, not merely described in another document.

## Product goal

FinSight RAG is intended to help users compare the financial narrative in a company's earnings-call transcripts across quarters. For example: “How did revenue guidance change from Q1 to Q3, and what reasons did management give?”

The target is **temporal retrieval-augmented generation (RAG)**:

1. Filter transcript passages by company and quarter.
2. Retrieve passages relevant to the question.
3. Organize evidence across the selected quarters.
4. Generate a comparison grounded in that evidence.
5. Return citations so the user can verify the answer.

## Current architecture

```text
Authenticated upload
  -> PDF/TXT text extraction
  -> text normalization and overlapping chunks
  -> SQL records for company, transcript, and chunks

Target, not yet implemented:
Question
  -> company/quarter filters
  -> embeddings and vector retrieval
  -> cross-quarter evidence grouping
  -> language-model analysis with citations
```

### Concepts in plain language

- **Chunk:** a manageable passage from a long transcript. Overlap helps avoid losing context at chunk boundaries.
- **Embedding:** a numerical representation of text used to find passages with similar meaning, even when they use different words.
- **Vector retrieval:** finding the most relevant chunks by comparing embeddings.
- **Temporal filter:** constraining retrieval to a company and selected fiscal quarters, so comparisons use the intended periods.
- **RAG:** retrieve source evidence first, then ask a language model to answer using that evidence rather than relying only on its general knowledge.
- **Migration:** a versioned database change that can be applied safely to existing data as the schema evolves.

## Implemented and verified at assessment

- FastAPI application startup and a health endpoint in `main.py`.
- Registration, login, and current-user profile routes in `routes/auth.py`.
- Password hashing and access/refresh JWT creation and access-token authentication in `core/security.py`.
- SQLAlchemy models for users, companies, transcripts, chunks, sentiments, and vector-index metadata in `db/models.py`.
- CRUD helpers for those records in `db/crud.py`.
- PDF and text extraction, normalization, heuristic speaker/section detection, and word-based chunking in `services/parser.py`.
- An authenticated `/ingest` route that validates basic upload metadata, rejects duplicate company/quarter/year transcripts, and saves the transcript and its chunks in one database transaction in `routes/ingest.py`.
- Parser tests pass: **2 passed** using the system Python 3.14 when pytest is run from the project directory.

## Not implemented yet

These features appear in planning documents or configuration but are not part of the working application at this assessment:

- AWS Bedrock embedding or language-model calls.
- Embedding generation and a functioning vector store/search path.
- Query, cross-quarter comparison, sentiment, or trend-analysis endpoints.
- S3 transcript storage or a background ingestion worker.
- A token refresh endpoint, despite refresh-token issuance.
- Database migrations.
- A containerized application image: the repository's `Dockerfile` is empty, and `docker-compose.yml` currently defines PostgreSQL only.
- Broad API, authorization, retrieval-quality, and production integration tests.

The README, setup guide, and `BUILD_INDEX.py` describe a more complete system than the code currently implements. We will treat code plus passing tests as evidence of completion, and mark documentation-only capabilities as planned.

## Existing worktree changes at assessment

These changes were already present; they were not made as part of this document:

- Modified: `core/config.py` (adds TXT/TEXT to supported file types).
- Modified: `main.py` (includes the ingestion router).
- Untracked: `routes/ingest.py`, `services/parser.py`, and `tests/`.

The project virtual environment's Python executable points to a Python 3.13 installation that is unavailable on this machine. The two parser tests passed with the system Python 3.14 when run from the project root. Re-establishing a reproducible project environment is an early roadmap task.

## Important decisions to agree on

1. **Transcript visibility:** Is the corpus shared among all users, or should each user's uploaded transcripts be private? Current transcript records are not associated with the authenticated user, so this must be resolved before query access is built.
2. **Vector storage:** Proposed first production direction: PostgreSQL with `pgvector`, keeping vectors and company/quarter metadata together. Confirm this against expected dataset size and operational needs before implementation.
3. **AWS scope:** Confirm AWS account, region, Bedrock model access, and budget before creating resources. Start with a development environment.
4. **Ingestion processing:** Decide when upload volume warrants SQS and a separate worker; it is not required for the first local retrieval milestone.

## Proposed production direction on AWS

Subject to agreement:

```text
Client -> API on ECS Fargate -> RDS PostgreSQL + pgvector
                    |         -> S3 for original transcripts
                    |         -> Bedrock for embeddings and grounded answers
                    -> Secrets Manager and CloudWatch

Later, if needed:
Upload -> S3/SQS -> ingestion worker -> parse/embed -> RDS + pgvector
```

- Use an ECS task IAM role and AWS's default credential chain rather than committing or deploying long-lived AWS access keys.
- Keep S3 private and enable encryption; keep secrets in Secrets Manager.
- Use CloudWatch for application logs and operational metrics.
- Add SQS/background workers when processing must outlive an HTTP request or handle meaningful volume.
- Return source citations with generated answers and test that citations belong to the requested company and quarters.

## Proposed 10-working-day roadmap

This is a planning baseline, not a commitment to finish a stage without review. Dependencies and estimates can change after each stage.

| Day | Proposed focus | Learning goal / completion evidence |
| --- | --- | --- |
| 1 | Agree on corpus visibility; make the test command/environment reproducible; record baseline | Understand authorization scope and repeatable testing |
| 2 | Design and add database migrations and the agreed ownership model | Understand schema evolution, tenant boundaries, and migration rollback |
| 3 | Harden upload validation and parser behavior; add focused ingestion tests | Understand request validation, transaction boundaries, and failure cases |
| 4 | Agree AWS development setup; add private S3 storage and IAM-role configuration | Understand object storage, IAM least privilege, and secret handling |
| 5 | Add a Bedrock client boundary with mocked provider tests | Understand embeddings versus text generation and how to test cloud dependencies |
| 6 | Add the agreed vector store and company/quarter-filtered retrieval | Understand similarity search, metadata filters, and retrieval evaluation |
| 7 | Build the comparison response with evidence citations | Understand grounding, temporal grouping, and unsupported-answer handling |
| 8 | Add evaluation cases for retrieval, citations, and cross-quarter answers | Understand measurable quality checks rather than relying on demos |
| 9 | Decide whether ingestion needs SQS/worker processing; add only if justified | Understand asynchronous jobs, retries, and idempotency |
| 10 | Add production checks, application container, CI, and a reviewed AWS development deployment | Understand deployment configuration, observability, and release safety |

### Commit rhythm

Aim for **2–4 useful commits on a working day**, usually two or three when the work naturally separates into implementation, tests, or documentation. Do not split changes artificially to hit a count. Each commit should be small, understandable, and validated; we will agree on any commit or push action before it happens.

## Completion standard

A roadmap item is done only when:

- The behavior matches the agreed requirement.
- Relevant tests pass, including failure and authorization cases where applicable.
- Configuration and secrets are handled appropriately for the target environment.
- Directly related documentation is updated.
- The result and any remaining limitations have been reviewed together.

## Agreed progress

### Completed

- Reviewed the current FinSight project structure, implementation, docs, and test baseline.
- Recorded the initial architecture, known gaps, AWS direction, and proposed roadmap in this document.

### Next discussion

- Agree whether transcript data is shared or private per user.
- Confirm the development AWS region/account and budget only when ready to plan provisioning.
