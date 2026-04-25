# FinSight RAG — Financial Intelligence Assistant (FastAPI)

FinSight RAG is a Retrieval-Augmented Generation (RAG) system designed to analyze and answer questions from financial documents such as annual reports, balance sheets, and filings.

It uses semantic search and large language models to generate accurate, context-aware financial insights grounded in real data.

---

## 🚀 Features

* 📄 Upload and process financial documents (PDF, CSV)
* 🔍 Semantic search using vector embeddings
* 💬 Natural language querying of financial data
* 📌 Context-aware responses with source attribution
* ⚡ Fast retrieval using FAISS
* 🧠 LLM-powered insights (AWS Bedrock - Claude)
* 🔗 Interactive interface connected via API

---

## 🧩 System Architecture

```id="y7kq2c"
User → Client Interface → FastAPI → RAG Pipeline → Response
```

### Flow:

1. Documents are uploaded and processed
2. Text is split into meaningful chunks
3. Embeddings are generated using Amazon Titan
4. Stored in FAISS for fast retrieval
5. Query is converted into embedding
6. Relevant chunks are retrieved
7. Claude generates a grounded response
8. Response is returned with sources

---

## 🏗️ Tech Stack

* **Backend**: FastAPI
* **LLM**: AWS Bedrock (Claude)
* **Embeddings**: Amazon Titan
* **Vector Store**: FAISS
* **Libraries**: Boto3, LangChain (optional), PyPDF

---

## 📂 Project Structure

```bash id="r9x2ml"
FinSight-RAG/
│── app/
│   │── main.py
│   │── routes/
│   │   ├── upload.py
│   │   ├── query.py
│   │── services/
│   │   ├── rag_pipeline.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │── core/
│   │   ├── config.py
│   │── models/
│   │   ├── schemas.py
│
│── interface/
│   │── client.py
│
│── data/
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash id="v1l3pk"
git clone https://github.com/your-username/FinSight-RAG.git
cd FinSight-RAG
```

---

### 2. Create Virtual Environment

```bash id="z8wq0c"
python -m venv venv
source venv/bin/activate   # macOS/Linux  
venv\Scripts\activate      # Windows  
```

---

### 3. Install Dependencies

```bash id="l0c9dw"
pip install -r requirements.txt
```

---

## 🔐 AWS Configuration

Ensure access to:

* Amazon Bedrock
* Claude model
* Titan embeddings

Set environment variables:

```bash id="m2w8yn"
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=your_region
```

---

## ▶️ Running the Application

### Start FastAPI Server

```bash id="n3x8qp"
uvicorn app.main:app --reload
```

API available at:

```id="q7r4bt"
http://127.0.0.1:8000
```

Interactive API docs:

```id="h2v8lm"
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

### Upload Document

**POST** `/upload`

---

### Query

**POST** `/query`

```json id="t4k1zs"
{
  "question": "What are the key financial risks mentioned?"
}
```

**Response**

```json id="x9c2pq"
{
  "answer": "The company faces risks related to market volatility...",
  "sources": [
    "Page 12: Risk Factors",
    "Page 40: Financial Overview"
  ]
}
```

---

## 🧪 Future Improvements

* ⚡ Async processing for large files
* ☁️ Deployment on AWS (EC2 / ECS)
* 🔍 Hybrid search (keyword + semantic)
* 📊 Financial ratio extraction
* 🔐 Authentication (JWT)

---

## 🎯 Why This Project Stands Out

* Demonstrates end-to-end RAG pipeline
* Uses AWS Bedrock (industry-relevant GenAI stack)
* Combines backend engineering with AI systems
* Designed for real-world financial data use cases

---
