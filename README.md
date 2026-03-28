# DataPilot

![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![DuckDB](https://img.shields.io/badge/DuckDB-analytics-orange)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-yellow)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

An AI-powered analytics engine that lets you query spreadsheets using plain English.

**Live Demo:** https://datapilot-production-5e68.up.railway.app  
**GitHub:** https://github.com/not-aryan7/DataPilot  

---

## Overview

Upload a CSV or Excel file, ask a question, and DataPilot:
- generates SQL
- executes it on DuckDB
- returns results as tables and charts

---

## How It Works
File → Pandas → DuckDB
Query → RAG → LLM → SQL
SQL → DuckDB → Results → Charts


---

## Architecture
Frontend (Vite + JS + Chart.js)
↓
FastAPI Backend
↓
RAG Pipeline (FAISS + Embeddings + Reranker + Groq LLM)
↓
SQL Generation
↓
DuckDB Execution
↓
Tables + Charts


---

## Tech Stack

| Layer      | Technology |
|------------|-----------|
| Backend    | FastAPI, DuckDB, Pandas |
| AI / ML    | FAISS, Sentence Transformers, Cross-Encoder |
| LLM        | Groq (Llama 3.3 70B) |
| Frontend   | Vite, JavaScript, Chart.js |
| Deployment | Docker, Railway |

---

## Features

- CSV + Excel upload  
- Natural language → SQL  
- Schema-aware retrieval (RAG)  
- Sample data injection (better accuracy)  
- Fast DuckDB queries  
- Auto charts + tables  
- SELECT-only safety  

---

## Example

**Input**

average revenue by region


**Generated SQL**
```sql
SELECT region, AVG(revenue) AS average_revenue
FROM sales
GROUP BY region;
``` 


---
## Project Structure
app/        FastAPI backend  
rag/        RAG + SQL generation  
frontend/   UI + charts  
tests_rag/  testing  

---

## Running Locally

Prerequisites:
1. Python 3.11+
2. Node.js 18+
3. Groq API key

---

## Clone

## Clone

```bash
git clone https://github.com/not-aryan7/DataPilot.git
cd DataPilot
``` 
---
## Setup

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

Create .env:

GROQ_API_KEY=your_api_key

## Run Backend

uvicorn app.main:app --reload --port 8001

## Run Frontend
cd frontend
npm install
npm run dev

---

## Authors

Ayush Neupane
Aryan RajBhandari