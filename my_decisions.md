-- Corpus Visibilty Set to private to the uploader
-- VENV set 3.13.5 

Implemented uploader-private corpus access:

New uploads save the authenticated user’s ID on each transcript. Transcript reads, edits, deletes, chunks, sentiments, and vector-index metadata are scoped to that owner in models.py and crud.py.
Two users can each upload the same company and quarter; duplicates are prevented per user, not globally. Company names remain shared metadata.
Legacy transcripts and vector indexes are preserved but left unowned and inaccessible until ownership is verified. The Alembic migration is in migrations/versions/20261126_add_private_corpus_ownership.py.
I added cross-user and legacy-data tests in test_ingest_authorization.py and documented the migration in SETUP.md. I also added the missing pinned auth dependencies to requirements.txt.
