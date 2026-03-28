# DataPilot

![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![DuckDB](https://img.shields.io/badge/DuckDB-analytics-orange)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-yellow)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

An AI-powered analytics engine that lets you query spreadsheets using plain English.

Upload a CSV or Excel file, ask a question, and DataPilot generates SQL, executes it on DuckDB, and returns results as tables and charts instantly.

**Live Demo:** https://datapilot-production-5e68.up.railway.app  
**GitHub:** https://github.com/not-aryan7/DataPilot  

---

## Overview

DataPilot enables natural language querying over structured data without requiring SQL knowledge.

Users can simply ask:

> What is the average revenue by region?

The system automatically:
- understands the query
- retrieves relevant schema context
- generates optimized SQL
- executes it on DuckDB
- returns results with visualizations

---

## How It Works
File Upload → Pandas → DuckDB Table
User Query → RAG Retrieval → LLM (Groq) → SQL Generation
SQL → DuckDB Execution → Results → Tables + Charts


---

## Architecture
Frontend (Vite + JS + Chart.js)
↓
FastAPI Backend (REST API)
↓
RAG Pipeline (FAISS + Embeddings + Reranker + Groq LLM)
↓
Generated SQL
↓
DuckDB Execution
↓
Tables + Charts


---

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | FastAPI, DuckDB, Pandas |
| AI / ML    | FAISS, Sentence Transformers, Cross-Encoder Reranker, RAG Pipeline |
| LLM        | Groq API (Llama 3.3 70B) |
| Frontend   | Vite, Vanilla JavaScript, Chart.js |
| Deployment | Docker, Railway |

---

## Features

- CSV and Excel upload with automatic schema detection  
- Column normalization to SQL-safe formats  
- Natural language to SQL generation using RAG  
- Semantic schema retrieval for accurate queries  
- Sample data injection into prompts for improved SQL accuracy  
- DuckDB OLAP query execution (millisecond latency)  
- Automatic table rendering and chart generation  
- Dataset management (upload, list, delete)  
- Query history tracking  
- Safe execution (SELECT-only queries)  

---

## Example

**Input**
average revenue by region


**Generated SQL**
```sql
SELECT region, AVG(revenue) AS average_revenue
FROM sales
GROUP BY region;

Executed instantly in DuckDB with results rendered as tables and charts.

Project Structure
app/          FastAPI backend, ingestion, API endpoints  
rag/          RAG pipeline, retriever, SQL generation  
frontend/     UI and chart rendering  
tests_rag/    RAG evaluation and testing  

Running Locally
Prerequisites
Python 3.11+
Node.js 18+
Groq API key (https://console.groq.com)

1. Clone Repository

git clone https://github.com/not-aryan7/DataPilot.git
cd DataPilot

2. Configure Environment

Create a .env file in the root:
GROQ_API_KEY=your_api_key_here

3. Start Backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

Backend runs at: http://127.0.0.1:8001

4. Start Frontend

cd frontend
npm install
npm run dev

Frontend runs at: http://localhost:5173

5. Use the App
Open the frontend
Upload a CSV or Excel file
Ask questions in plain English
Get SQL, tables, and charts instantly

API Endpoints
Method	Route	Description
GET	/api/datasets	List datasets
POST	/api/upload	Upload dataset
POST	/api/ask	Ask a query
DELETE	/api/datasets/{id}	Delete dataset

Deployment

DataPilot is deployed on Railway using Docker.

To deploy your own instance:

Fork the repository
Connect it to Railway (https://railway.app)
Add GROQ_API_KEY as an environment variable
Deploy using Docker
Safety
Only SELECT queries are allowed
No DROP, DELETE, or UPDATE operations
Data remains within the session
Designed for small to medium datasets
Authors

Ayush Neupane
Aryan RajBhandari

Computer Science + Economics
Building applied AI systems, RAG pipelines, and data-driven products