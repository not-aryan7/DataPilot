# DataPilot

A local-first analytics engine that lets you query spreadsheets using plain English.

Upload a CSV or Excel, ask a question, AI generates SQL, DuckDB executes, results show as tables and charts.

---

## How It Works

```
file → pandas → DuckDB table
question → embeddings → FAISS → reranker → prompt + sample data → LLM → SQL
SQL → DuckDB → JSON → table + charts
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, DuckDB, Pandas, SQLite |
| AI / ML | Sentence Transformers, FAISS, Cross-Encoder Reranker, Ollama, Qwen2.5-Coder |
| Frontend | Vite, Vanilla JS, Chart.js |

---

## Features

- CSV and Excel upload with automatic schema detection
- Column name normalization (SQL-safe snake_case)
- Natural language to SQL generation via RAG pipeline
- Safe SQL execution (SELECT only)
- Semantic schema retrieval with sample data context
- DuckDB OLAP queries
- Automatic table and chart rendering
- Dataset management (list, select, delete)
- Query history tracking
- Fully local inference via Ollama

---

## Project Structure

```
app/          FastAPI backend, API endpoints, ingestion service
rag/          Embeddings, FAISS index, reranker, prompt builder, LLM client
frontend/     Vite UI, Chart.js visualizations
tests_rag/    Unit tests for RAG components
```

---

## Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed

### 1. Clone and set up

```bash
git clone https://github.com/not-aryan7/DataPilot.git
cd DataPilot
```

### 2. Pull the model

```bash
ollama pull qwen2.5-coder:3b
```

### 3. Start the backend

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Backend runs at `http://127.0.0.1:8001`

### 4. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 5. Use the app

1. Open `http://localhost:5173`
2. Upload a CSV or Excel file
3. Ask questions in plain English
4. Get SQL, tables, and charts

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/datasets` | List all uploaded datasets |
| POST | `/api/upload` | Upload CSV or Excel file |
| POST | `/api/ask` | Ask a natural language question |
| DELETE | `/api/datasets/{id}` | Delete a dataset |

---

## Safety

- SELECT queries only — no DROP, DELETE, UPDATE
- Runs fully offline
- Designed for small to medium datasets

---

## Authors

**Ayush Neupane** and **Aryan RajBhandari**
