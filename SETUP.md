# 📊 Earnings Call Analyzer - Complete Build

## Overview

A production-ready **Temporal RAG system** for analyzing earnings call transcripts across multiple quarters using **AWS Bedrock**, **PostgreSQL**, and **FAISS**.

### ✨ Key Features
- 🔄 Cross-quarter comparative analysis
- 🎙️ Speaker segmentation (CEO, CFO, Analysts)
- 📈 Sentiment analysis using Claude
- 🔍 Semantic search with FAISS embeddings
- 📊 Trend detection across quarters
- ⚡ FastAPI REST API with async support
- 🗂️ PostgreSQL metadata storage
- 🤖 AWS Bedrock Claude for LLM + Titan for embeddings

---

## 🏗️ Architecture

```
PDF Input
   ↓
Parser (speaker segmentation, chunking)
   ↓
Embeddings (AWS Bedrock Titan)
   ↓
Vector Store (FAISS)
   ↓
Database (PostgreSQL - metadata + sentiment)
   ↓
RAG Pipeline (retrieval + Claude analysis)
   ↓
API Response (cross-quarter insights)
```

---

## 📁 Project Structure

```
app/
├── core/
│   ├── config.py          # Configuration management
│   ├── schemas.py         # Request/response Pydantic models
│   └── __init__.py
├── db/
│   ├── database.py        # PostgreSQL connection
│   ├── models.py          # SQLAlchemy ORM models
│   ├── crud.py            # Database operations
│   └── __init__.py
├── services/
│   ├── parser.py          # PDF parsing + chunking
│   ├── embedding.py       # AWS Bedrock embeddings + LLM
│   ├── vector_store.py    # FAISS wrapper
│   ├── rag_pipeline.py    # Retrieval + context grouping
│   ├── sentiment.py       # Sentiment analysis
│   ├── trend_analyzer.py  # Trend detection
│   └── __init__.py
├── routes/
│   ├── ingest.py          # POST /ingest
│   ├── query.py           # POST /query/analyze, /query/trends
│   ├── comapnies.py       # GET /companies, /companies/{company}/quarters
│   └── __init__.py
├── main.py                # FastAPI app
└── __init__.py

data/
├── transcripts/           # Input PDFs
└── indices/              # FAISS indices

scripts/
└── bulk_ingest.py        # Batch ingestion script

requirements.txt          # Dependencies
.env                      # Configuration (create from .env.example)
README.md                 # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 12+
- AWS Account with Bedrock access
- AWS CLI configured with credentials

### 2. Setup

```bash
# Clone/navigate to project
cd /path/to/FinSight-RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
# Edit .env with your AWS credentials and PostgreSQL URL
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb earnings_analyzer

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/earnings_analyzer
```

### 4. AWS Bedrock Setup

```bash
# Configure AWS credentials
aws configure

# Verify access to Bedrock models
aws bedrock list-foundation-models --region us-east-1
```

### 5. Run Application

```bash
# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Ingest Transcript
```bash
POST /ingest
- Params: file (PDF), company (string), quarter (string, format: Q1-2024)
- Returns: IngestionResponse with transcript_id and chunk_count
```

### Query Analysis
```bash
POST /query/analyze
Body:
{
  "query": "How has revenue guidance changed?",
  "company": "TCS",
  "quarters": ["Q1-2024", "Q2-2024", "Q3-2024"],
  "top_k": 5
}
Returns: QueryResponse with retrieved chunks and LLM analysis
```

### Trend Analysis
```bash
POST /query/trends
Body:
{
  "company": "TCS",
  "quarters": ["Q1-2024", "Q2-2024"],
  "topic": "revenue growth"
}
Returns: TrendAnalysisResponse with sentiment trajectory and key shifts
```

### List Companies
```bash
GET /companies
Returns: List of CompanyResponse with available quarters
```

### Get Company Quarters
```bash
GET /companies/{company}/quarters
Returns: QuartersResponse with available quarters
```

---

## 🔄 Workflow

### 1. Ingestion

```python
# Via API
curl -F "file=@transcript.pdf" \
     -F "company=TCS" \
     -F "quarter=Q1-2024" \
     http://localhost:8000/ingest

# Or bulk script
python scripts/bulk_ingest.py \
    --directory ./data/transcripts \
    --company TCS \
    --quarter Q1-2024
```

**What happens:**
1. PDF extracted and parsed into chunks
2. Chunks segmented by speaker (CEO, CFO, etc.)
3. Embeddings generated (AWS Bedrock Titan)
4. Vectors stored in FAISS index
5. Metadata stored in PostgreSQL
6. Sentiment analysis performed

### 2. Querying

```python
# Via API
curl -X POST http://localhost:8000/query/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main risks?",
    "company": "TCS",
    "quarters": ["Q1-2024", "Q2-2024"],
    "top_k": 5
  }'
```

**What happens:**
1. Query embedded using Bedrock
2. FAISS retrieves top-k relevant chunks
3. Context grouped by quarter
4. Claude LLM generates comparative analysis
5. Response includes retrieved chunks + analysis

### 3. Trend Analysis

```python
curl -X POST http://localhost:8000/query/trends \
  -H "Content-Type: application/json" \
  -d '{
    "company": "TCS",
    "quarters": ["Q1-2024", "Q2-2024", "Q3-2024"],
    "topic": "capital expenditure"
  }'
```

**What happens:**
1. Sentiment scores aggregated per quarter
2. Narrative shifts detected
3. Keywords extracted per quarter
4. Claude generates trend narrative
5. Response includes sentiment trajectory and key shifts

---

## 🔧 Configuration

### `core/config.py`

Settings are loaded from environment variables:

```python
# Database
DATABASE_URL              # PostgreSQL connection
SQLALCHEMY_ECHO          # Log SQL queries

# AWS
AWS_REGION              # Default: us-east-1
AWS_ACCESS_KEY_ID       # AWS credentials
AWS_SECRET_ACCESS_KEY   

# Bedrock Models
BEDROCK_EMBEDDING_MODEL # Default: amazon.titan-embed-text-v2:0
BEDROCK_LLM_MODEL       # Default: anthropic.claude-3-sonnet-20240229-v1:0

# Vector Store
VECTOR_DIMENSION        # Default: 1024 (Titan v2)
FAISS_INDEX_DIR         # Default: ./data/indices

# API
API_HOST                # Default: 0.0.0.0
API_PORT                # Default: 8000
```

---

## 🧪 Testing

```bash
# Run with test data
python -m pytest tests/ -v

# Manual test
python -c "
from app.services.parser import parser
from app.services.embedding import embeddings_client

# Test parser
text = 'Sample transcript text'

# Test embeddings
embedding = embeddings_client.embed_text('test query')
print(f'Embedding dim: {embedding.shape}')
"
```

---

## 📊 Database Schema

### Companies
```sql
- id (PK)
- name (unique)
- created_at
```

### Transcripts
```sql
- id (PK)
- company_id (FK)
- company_name
- quarter
- year
- filename
- raw_text
- chunk_count
- created_at, updated_at
```

### Chunks
```sql
- id (PK)
- transcript_id (FK)
- company
- quarter
- speaker
- role (management, analyst, etc.)
- section (prepared, qa)
- text
- created_at
```

### Sentiments
```sql
- id (PK)
- chunk_id (FK, unique)
- score (-1.0 to 1.0)
- label (positive, negative, neutral)
- confidence
- created_at
```

### VectorIndices
```sql
- id (PK)
- company (unique)
- index_path
- chunk_count
- embedding_model
- created_at, updated_at
```

---

## 🔍 Key Modules

### Parser (`services/parser.py`)
- Extracts text from PDF
- Segments by speaker
- Detects sections (prepared vs Q&A)
- Chunks with configurable size/overlap
- Returns structured `ChunkCreate` objects

### Embeddings (`services/embedding.py`)
- `BedrockEmbeddingsClient`: AWS Bedrock Titan embeddings
- `LLMClient`: AWS Bedrock Claude for generation
- Handles batch operations efficiently

### Vector Store (`services/vector_store.py`)
- FAISS IndexFlatL2 (Euclidean distance)
- Per-company indices
- Persistent storage to disk
- Quarter-filtered search
- Metadata management

### RAG Pipeline (`services/rag_pipeline.py`)
- Retrieve context across quarters
- Group by quarter
- Generate LLM analysis
- Full query → response orchestration

### Sentiment (`services/sentiment.py`)
- Uses Claude for sentiment analysis
- Returns score, label, confidence
- Batch processing support
- Aggregation functions

### Trends (`services/trend_analyzer.py`)
- Quarter-to-quarter sentiment tracking
- Keyword extraction
- Narrative shift detection
- Comparative analysis generation

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to server: No such file or directory
```
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct
```bash
psql -U user -d earnings_analyzer -c "SELECT 1"
```

### AWS Bedrock Access Denied
```
Error: User is not authorized to perform: bedrock:InvokeModel
```
**Solution:** Verify IAM permissions for Bedrock and credentials are configured
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

### FAISS Index Errors
```
Error: Cannot create index of type IndexFlatL2 with dimension 768
```
**Solution:** Ensure VECTOR_DIMENSION in config matches embedding model output
- Titan v2: 1024 dimensions
- Update config if using different model

### Empty Query Results
```
No results retrieved for query
```
**Solution:** 
- Verify transcripts are ingested: `GET /companies`
- Check vector store has data: inspect `data/indices/` directory
- Ensure query text is substantive (min 5 chars)

---

## 📚 Dependencies

Key packages:
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **psycopg2** - PostgreSQL adapter
- **boto3** - AWS SDK (Bedrock)
- **faiss** - Vector search
- **pdfplumber** - PDF extraction
- **sentence-transformers** - Embeddings (local alternative)
- **langchain** - LLM orchestration

See `requirements.txt` for full list.

---

## 🚀 Performance Tips

1. **Batch Ingestion:** Use `scripts/bulk_ingest.py` for multiple files
2. **Chunk Size:** Tune `CHUNK_SIZE` based on GPU memory
3. **Vector Store:** FAISS uses CPU by default (IndexFlatL2)
   - For GPU support, use `index_cpu_to_gpu()`
4. **Embeddings:** Cache frequently used embeddings
5. **Database:** Add indexes on `(company, quarter)` for queries

---

## 🤝 Contributing

### Code Style
```bash
black app/
flake8 app/ --max-line-length=120
```

### Type Checking
```bash
mypy app/
```

---

## 📝 License

[Your license here]

---

## 🎯 Future Enhancements

- [ ] Topic modeling across quarters
- [ ] Speaker influence scoring
- [ ] Real-time ingestion pipeline
- [ ] Sentiment trend visualization
- [ ] Alerting for narrative shifts
- [ ] Multi-model ensemble (Claude + Llama)
- [ ] Caching layer (Redis)
- [ ] Advanced NLP (NER, relation extraction)
- [ ] Batch query optimization
- [ ] Web dashboard (Streamlit/React)

---

## 📞 Support

For issues or questions:
1. Check `Troubleshooting` section above
2. Review AWS Bedrock documentation
3. Check FastAPI docs at `/docs` endpoint
4. Verify configuration in `.env`

---

**Happy analyzing! 📊**
