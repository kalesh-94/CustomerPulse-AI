# CustomerPulse AI 🎯

> An AI-powered customer support analytics platform that transforms raw support tickets into actionable business insights using a hybrid AI approach — combining deterministic rule-based processing with on-demand LLM intelligence.

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| 🔗 Backend API (FastAPI) | http://52.66.34.73:8000/docs |
| 📊 Frontend Dashboard (Streamlit) | https://customerpulse-ai.streamlit.app/ |

---

## 📌 Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Setup & Installation](#setup--installation)
- [Deployment](#deployment)
- [Best Practices](#best-practices)
- [Scalability](#scalability)

---

## Overview

CustomerPulse AI is a full-stack analytics platform built for e-commerce and SaaS businesses that receive high volumes of customer support tickets. It ingests ticket data (via CSV upload or real-time API), runs a structured data pipeline, and surfaces insights through an interactive Streamlit dashboard.

The platform uses a **hybrid AI architecture**: a fast, deterministic pipeline handles batch processing at scale, while LLMs (via Groq) are invoked on-demand for higher-quality tasks like reply generation and business summarization — keeping costs low and latency predictable.

---

## Core Features

- 📂 **Batch CSV Upload** — Upload thousands of support tickets and process them through a full AI pipeline
- ⚡ **Real-Time Ticket API** — Add individual tickets and receive instant sentiment, category, and reply suggestions
- 🧹 **Data Cleaning Pipeline** — Automated normalization, deduplication, and preprocessing via `utils/cleaning.py`
- 🏷️ **Rule-Based Categorization** — Fast, deterministic classification into predefined issue categories
- 😊 **Sentiment Analysis** — Classify tickets as positive, neutral, or negative with frustration scoring
- 💬 **LLM Reply Generation** — On-demand suggested agent responses via Groq (LLaMA 3)
- 📊 **Interactive Dashboard** — Sentiment trends, category distribution, revenue at risk, and AI business summaries
- 🤖 **AI Business Insights** — LLM-generated executive summaries for leadership reporting

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
│              Streamlit Dashboard  (frontend/app.py)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP Requests
┌────────────────────────────▼────────────────────────────────────────┐
│                  API LAYER  (backend/app/main.py)                   │
│                                                                     │
│   api/upload.py        api/tickets.py        api/insights.py        │
│   POST /upload         POST /tickets         GET /insights          │
└──────────┬──────────────────┬──────────────────────┬───────────────┘
           │                  │                      │
┌──────────▼──────────────────▼──────────────────────▼───────────────┐
│                       SERVICES LAYER                                │
│                                                                     │
│  pipeline.py        ai_service.py        insight_service.py        │
│  (orchestration)    (sentiment,          (aggregations,            │
│                      categories)          revenue at risk)         │
│                                                                     │
│  embedding_service.py    llm_service.py      storage_service.py    │
│  (MiniLM + FAISS)        (Groq on-demand)    (SQLite reads/writes) │
│                                                                     │
│  model_loader.py                                                    │
│  (cached model init)                                                │
└──────────┬──────────────────────────────────────────┬──────────────┘
           │                                          │
┌──────────▼──────────┐                  ┌────────────▼──────────────┐
│   SQLite Database   │                  │      FAISS Index          │
│   db/database.py    │                  │  (vector similarity       │
│   models/ticket.py  │                  │   search over embeddings) │
└─────────────────────┘                  └───────────────────────────┘
```

### Data Pipeline (Batch Processing)

The batch pipeline inside `services/pipeline.py` is **fully deterministic** — no LLM calls, no API costs, no rate limits. Fast and predictable for large datasets.

```
Raw CSV  (POST /upload → api/upload.py)
   │
   ▼
[Stage 1 — Clean]             utils/cleaning.py
  · Drop nulls and duplicates
  · Normalize whitespace, casing, and field types
  · Validate required fields
   │
   ▼
[Stage 2 — Categorize + Sentiment]    services/ai_service.py
  · Rule-based keyword matching → issue category
  · Sentiment scoring → positive / neutral / negative
  · Frustration level → low / medium / high
   │
   ▼
[Stage 3 — Embed]             services/embedding_service.py
  · Sentence-transformer (all-MiniLM-L6-v2) → 384-dim vectors
  · FAISS index built for semantic similarity search
   │
   ▼
[Stage 4 — Store]             services/storage_service.py + db/database.py
  · Enriched tickets persisted to SQLite
  · FAISS index saved to disk
```

### Why LLM Is NOT Used in the Batch Pipeline

| Concern | Impact if LLM ran on every ticket |
|---------|----------------------------------|
| **Cost** | 10,000 tickets × API call = significant spend |
| **Latency** | Batch would take hours instead of seconds |
| **Rate Limits** | Free-tier Groq API throttles at volume |
| **Reliability** | External API failure breaks the entire pipeline |

**Solution:** `services/llm_service.py` is invoked **on-demand only** — when a user explicitly requests a reply suggestion, business summary, or insight report from the dashboard. The core pipeline stays fast, cheap, and fault-tolerant.

### Hybrid AI Approach

```
┌──────────────────────────────────────────────────────────────────┐
│                    HYBRID AI DESIGN                              │
│                                                                  │
│  Rule-Based  (services/ai_service.py)                           │
│  ─────────────────────────────────────────                      │
│  · Ticket categorization                                         │
│  · Sentiment scoring                                             │
│  · Keyword / TF-IDF extraction                                   │
│  ✅ Fast   ✅ Free   ✅ Always available                        │
│                                                                  │
│  LLM On-Demand  (services/llm_service.py — Groq)                │
│  ────────────────────────────────────────────────                │
│  · Agent reply generation                                        │
│  · Executive business summaries                                  │
│  · Ad-hoc insight narration                                      │
│  ✅ High quality   ✅ Only when explicitly requested            │
└──────────────────────────────────────────────────────────────────┘
```

### Embeddings & Semantic Search

Each ticket message is converted into a dense vector using `sentence-transformers/all-MiniLM-L6-v2` inside `services/embedding_service.py`. These 384-dimensional vectors capture semantic meaning — enabling similarity-based search far beyond simple keyword matching.

**FAISS** stores these vectors in an efficient index and retrieves the most semantically similar tickets in milliseconds — useful for finding related issues, clustering complaints, and surfacing relevant past resolutions.

Model initialization is handled once in `services/model_loader.py` and cached across all requests to avoid repeated load overhead on every API call.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Frontend** | Streamlit |
| **Database** | SQLite (`db/database.py`) |
| **Vector Store** | FAISS (`services/embedding_service.py`) |
| **Embeddings** | Sentence Transformers `all-MiniLM-L6-v2` |
| **LLM** | Groq API — LLaMA 3.3 70B (`services/llm_service.py`) |
| **Data Processing** | Pandas, Scikit-learn (`utils/cleaning.py`) |
| **Containerization** | Docker (`backend/Dockerfile`) |
| **Deployment — Backend** | AWS EC2 |
| **Deployment — Frontend** | Streamlit Cloud |

---

## Project Structure

```
CustomerPulse-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── insights.py          # GET  /insights  — dashboard aggregations
│   │   │   ├── tickets.py           # POST /tickets   — real-time single ticket
│   │   │   └── upload.py            # POST /upload    — CSV batch processing
│   │   │
│   │   ├── db/
│   │   │   └── database.py          # SQLite connection, schema creation, CRUD ops
│   │   │
│   │   ├── models/
│   │   │   └── ticket.py            # Pydantic schemas
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py        # Rule-based sentiment + categorization
│   │   │   ├── embedding_service.py # MiniLM embeddings + FAISS index management
│   │   │   ├── insight_service.py   # Analytics aggregations (trends, revenue at risk)
│   │   │   ├── llm_service.py       # Groq API — reply gen + summaries (on-demand only)
│   │   │   ├── model_loader.py      # Cached model initialization (load once, reuse)
│   │   │   ├── pipeline.py          # Full batch pipeline orchestration
│   │   │   └── storage_service.py   # Persistence layer (SQLite + FAISS writes)
│   │   │
│   │   ├── utils/
│   │   │   └── cleaning.py          # Data cleaning and normalization helpers
│   │   │
│   │   └── main.py                  # FastAPI app entry point, router registration
│   │
│   ├── Dockerfile                   # Backend container definition
│   └── requirements.txt             # Backend Python dependencies
│
├── frontend/
│   ├── app.py                       # Streamlit dashboard (all UI and chart logic)
│   └── requirements.txt             # Frontend Python dependencies
│
├── .devcontainer/                   
├── .gitignore
└── README.md
```

---

## API Reference

### `POST /upload`
Upload a CSV file of support tickets and trigger the full deterministic pipeline (`services/pipeline.py`).

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | `File` | CSV file containing support tickets |

**Response:**
```json
{
  "status": "success",
  "tickets_processed": 10000,
  "summary": {
    "total_tickets": 10000,
    "category_distribution": { "Shipping Delay": 2500, "Refund Request": 2000 },
    "sentiment_distribution": { "negative": 4200, "neutral": 3100, "positive": 2700 },
    "revenue_at_risk": 84320.50
  }
}
```

---

### `POST /tickets`
Add a single new ticket and receive real-time AI analysis (sentiment + category + LLM reply).

**Request Body:**
```json
{
  "message": "My order hasn't arrived after 2 weeks. Very frustrated.",
  "product": "Laptop",
  "channel": "email",
  "order_value": 899.00,
  "customer_country": "US"
}
```

**Response:**
```json
{
  "ticket_id": "TKT-A1B2C3D4",
  "category": "Shipping Delay",
  "sentiment_label": "negative",
  "frustration_level": "high",
  "category_confidence": 0.94,
  "suggested_response": "We sincerely apologize for the delay with your order..."
}
```

---

### `GET /insights`
Retrieve all aggregated dashboard data in a single call. Powered by `api/insights.py` + `services/insight_service.py`.

**Response:**
```json
{
  "total_tickets": 10000,
  "revenue_at_risk": 84320.50,
  "sentiment_distribution": { "negative": 4200, "neutral": 3100, "positive": 2700 },
  "category_distribution": [
    { "category": "Shipping Delay", "count": 2500, "avg_sentiment": -0.62 }
  ],
  "top_issues": [
    { "issue": "shipping delay", "frequency": 2100, "percentage": 21.0 }
  ],
  "sentiment_trend": [
    { "month": "2024-01", "avg_sentiment": -0.45, "ticket_count": 830 }
  ],
  "recent_tickets": [ "..." ]
}
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- Git
- A free Groq API key → [console.groq.com/keys](https://console.groq.com/keys)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/kalesh-94/CustomerPulse-AI.git
cd CustomerPulse-AI
```

### Step 2 — Set Up the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3 — Set Up the Frontend

```bash
# Open a second terminal, navigate to frontend
cd frontend

pip install -r requirements.txt
```

### Step 4 — Configure Environment Variable

```bash
# Create a .env file inside the backend/ directory
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

Or export directly in your shell:

```bash
# macOS / Linux
export GROQ_API_KEY=your_groq_api_key_here

# Windows (Command Prompt)
set GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ Never commit your `.env` file or API key. The `.gitignore` already excludes `.env`.

### Step 5 — Start the Backend

```bash
# From the backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API live at: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### Step 6 — Start the Frontend

```bash
# From the frontend/ directory (separate terminal)
streamlit run app.py
```

- Dashboard at: `http://localhost:8501`

### Step 7 — Use the Dashboard

1. Open `http://localhost:8501` in your browser
2. Upload a CSV file of support tickets using the sidebar uploader
3. Click **Process Tickets** to run the full pipeline
4. Explore the sentiment chart, category breakdown, revenue at risk, and AI-generated insights

---

### Running the Backend with Docker

```bash
# From the backend/ directory
docker build -t customerpulse-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here customerpulse-backend
```

---

## Deployment

### Backend — AWS EC2

The FastAPI backend is deployed on an **AWS EC2 instance** (Ubuntu, `t2.micro` free tier) using Uvicorn. The `backend/Dockerfile` is used for containerized deployment.

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Clone the repo
git clone https://github.com/kalesh-94/CustomerPulse-AI.git
cd CustomerPulse-AI/backend

# Set environment variable
export GROQ_API_KEY=your_key_here

# Option A — Run directly
pip install -r requirements.txt
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Option B — Run via Docker
docker build -t customerpulse-backend .
docker run -d -p 8000:8000 -e GROQ_API_KEY=$GROQ_API_KEY customerpulse-backend
```

> For production, set up `nginx` as a reverse proxy and `systemd` to keep the service alive across reboots.


## Scalability

The current architecture handles up to ~50,000 tickets on a single instance. Upgrade path when traffic grows:

| Current | Production Scale-Up |
|---------|-------------------|
| SQLite (`db/database.py`) | PostgreSQL + SQLAlchemy connection pooling |
| FAISS in-memory index | Pinecone / Weaviate (managed hosted vector DB) |
| Single Uvicorn process | Gunicorn multi-worker + Nginx reverse proxy |
| Sync pipeline (`pipeline.py`) | Celery + Redis task queue (async batch jobs) |
| Manual EC2 deploy | Docker + GitHub Actions → AWS ECS / App Runner |
| No caching on `GET /insights` | Redis with TTL for insight aggregation responses |

The LLM-on-demand design in `llm_service.py` means AI API costs scale only with user interactions — not raw data volume — making the platform cost-efficient at scale.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

```bash
git checkout -b feature/your-feature-name
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# Open a Pull Request on GitHub
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Developed by **Kalesh Patil**

</div>
