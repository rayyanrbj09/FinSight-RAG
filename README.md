# 📊 Earnings Call Analyzer

### Temporal RAG for Financial Narrative Intelligence

A production-style Retrieval-Augmented Generation (RAG) system that analyzes **earnings call transcripts across multiple quarters** to surface **trend shifts, sentiment changes, and evolving management narratives**.

> Not “what does this document say?”
> → **“How has the story changed over time?”**

---

## 🚀 Why This Exists

Earnings call transcripts are:

* Long (50–80 pages)
* Dense and repetitive
* Distributed across quarters

Comparing them manually is slow and inconsistent.

This system:

* Structures transcripts into analyzable data
* Retrieves context **across time**
* Generates **comparative insights**, not summaries

---

## 🧠 Core Idea

**Temporal RAG** — extend standard RAG with time-aware retrieval.

```text
Query → Filter (company + quarters)
      → Retrieve (multi-quarter)
      → Group by time
      → Compare
      → Generate insight
```

---

## 🏗️ System Architecture

### Ingestion

* Upload transcripts (PDF / text)
* Batch ingest via scripts
* Optional web scraping (Seeking Alpha)

### Processing

* Speaker segmentation (CEO, CFO, Analyst)
* Section detection (Prepared vs Q&A)
* Chunking with metadata

### Enrichment

* Sentiment scoring (FinBERT / LLM-based)
* Embeddings (OpenAI / Amazon Titan)

### Storage

* **PostgreSQL** → metadata + sentiment
* **FAISS** → vector search (per company index)

### Query Engine

* Metadata-filtered retrieval
* Cross-quarter grouping
* LLM-based comparison

---

## 📁 Project Structure

```text
EarningsCallAnalyzer/
│
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── ingest.py
│   │   ├── query.py
│   │   └── companies.py
│   │
│   ├── services/
│   │   ├── parser.py
│   │   ├── sentiment.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── rag_pipeline.py
│   │   └── trend_analyzer.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── database.py
│   │
│   └── core/
│       ├── config.py
│       └── schemas.py
│
├── interface/
│   └── dashboard.py
│
├── data/
│   ├── transcripts/
│   └── indices/
│
├── scripts/
│   ├── bulk_ingest.py
│   └── scraper.py
│
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ How It Works

### 1. Parsing → Structured Chunks

```json
{
  "company": "TCS",
  "quarter": "Q1-2024",
  "speaker": "CEO",
  "role": "management",
  "section": "prepared",
  "text": "..."
}
```

---

### 2. Embedding + Storage

* Each chunk → embedding vector
* Stored in FAISS with metadata filters

---

### 3. Cross-Quarter Retrieval

* Filter by:

  * company
  * selected quarters
* Retrieve semantically relevant chunks

---

### 4. Comparative Generation

LLM receives grouped context:

```text
Q1: ...
Q2: ...
Q3: ...
```

Produces:

* Trend analysis
* Tone shifts
* Strategy evolution

---

## 📡 API Endpoints

### POST `/ingest`

Upload and process transcript

**Params:**

* file
* company
* quarter

---

### POST `/query`

```json
{
  "query": "How has revenue guidance changed?",
  "company": "TCS",
  "quarters": ["Q1-2024", "Q2-2024", "Q3-2024"]
}
```

---

### GET `/companies`

### GET `/quarters`

---

## 📈 Features

* Cross-quarter financial analysis
* Speaker-aware chunking
* Metadata-driven retrieval
* Temporal comparison via LLM
* Modular, production-style architecture

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Vector DB:** FAISS
* **Database:** PostgreSQL
* **LLM:** OpenAI / Claude
* **Embeddings:** OpenAI / Amazon Titan
* **NLP:** FinBERT (optional)
* **UI:** Streamlit (optional)

---

## 🧪 Status

* ✅ Parsing & chunking
* 🔄 Vector storage
* 🔄 Cross-quarter retrieval
* ⏳ Sentiment analysis
* ⏳ Dashboard

---

## 💡 Future Work

* Topic modeling across quarters
* Better speaker classification
* Real-time ingestion pipeline
* Sentiment trend visualization
* Alerting for narrative shifts

---

## 🎯 What This Demonstrates

* RAG beyond basic implementation
* Temporal reasoning in NLP systems
* End-to-end ML system design
* Real-world financial use case

---

## 📌 Example Use Cases

* Equity research
* Investment analysis
* Earnings trend tracking
* Risk signal detection

---

## 📄 License

MIT
