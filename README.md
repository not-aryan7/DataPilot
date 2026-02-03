# 🚀 DataPilot

DataPilot is a lightweight, local-first analytics tool that lets you query spreadsheets using plain English.

Upload a CSV or Excel file → ask a question → AI generates SQL → DuckDB executes it → results are shown as tables and charts.

Think:

ChatGPT + SQL + DuckDB + charts  
All running locally. No cloud. No external APIs. No heavy BI tools.

---

## ✨ What you can ask

Examples:

- total revenue by year
- sum of sales by region
- average price per product
- top 5 rows
- group by month
- average talk time per agent

---

## ⚙️ How it works

file → pandas → DuckDB table  
question → embeddings → FAISS search → rerank → prompt → LLM → SQL  
SQL → DuckDB → JSON → table + charts

Natural language in.  
SQL + charts out.

---

## 🧠 Architecture

Frontend (Vite + JS)
        ↓
FastAPI Backend (REST API)
        ↓
RAG SQL Engine (Embeddings + FAISS + Reranker + LLM)
        ↓
Generated SQL
        ↓
DuckDB execution
        ↓
Tables + Charts

---

## 🧩 Tech Stack

Backend
- FastAPI
- DuckDB
- Pandas

AI / ML
- Sentence Transformers (bi-encoder embeddings)
- FAISS (vector similarity search)
- Cross-encoder reranker
- Local LLM (TinyLlama / Mistral)
- Retrieval-Augmented Generation (RAG)

Frontend
- Vite
- Vanilla JavaScript
- Chart.js

---

## 🔥 Core Feature

Natural Language → SQL

Example:

Input
average revenue by region

Generated automatically
SELECT region, AVG(revenue)
FROM sales
GROUP BY region;

Executed instantly inside DuckDB.

---

## ✨ Features

- CSV + Excel upload
- automatic schema detection
- column normalization
- safe SQL generation (SELECT only)
- semantic schema retrieval
- DuckDB OLAP queries (very fast)
- automatic table rendering
- automatic chart creation
- fully local inference
- zero cloud dependencies

---

## 📂 Project Structure

app/        API + ingestion + endpoints  
rag/        embeddings + retriever + SQL generator  
frontend/   UI + charts  
tests_rag/  model tests  

---
## 🚀 Run Locally

### 1. Clone the repo
git clone https://github.com/<your-username>/DataPilot.git
cd DataPilot


### 2. Backend (FastAPI + DuckDB)

Create virtual environment

python -m venv venv

Activate

Windows
venv\Scripts\activate

macOS / Linux
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Start API

uvicorn app.main:app --reload

Backend running at:
http://127.0.0.1:8000

Swagger docs:
http://127.0.0.1:8000/docs


### 3. Frontend (Vite)

Open new terminal

cd frontend
npm install
npm run dev

Frontend running at:
http://localhost:5173


### 4. Use the app

• Open browser  
• Upload CSV or Excel  
• Ask questions in plain English  
• Get SQL + tables + charts instantly


### 5. Stop server

CTRL + C (both terminals)
deactivate   # exit virtual environment



---

## 🛡 Safety

- SELECT queries only
- no DROP/DELETE/UPDATE
- runs fully offline
- intended for small/medium datasets

---

## 🧠 Why We built this

To practice building complete end-to-end AI systems that combine:

- backend APIs
- analytical databases
- vector search
- LLM pipelines
- frontend visualization

Instead of using cloud tools, everything runs locally for privacy, speed, and zero cost.

---

## 👨‍💻 Author

Ayush Neupane , Aryan RajBhandari
Computer Science + Economics  
Building applied AI + data engineering systems

