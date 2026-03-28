# DataPilot

![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![DuckDB](https://img.shields.io/badge/DuckDB-analytics-orange)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-yellow)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

An AI-powered analytics engine that lets you query spreadsheets using plain English.

Upload a CSV or Excel file, ask a question, and DataPilot generates SQL, executes it on DuckDB, and returns results as tables and charts.

Try it live: https://datapilot-production-5e68.up.railway.app  
GitHub: https://github.com/not-aryan7/DataPilot  

---

## How It Works

file → pandas → DuckDB table  
question → RAG retrieval → LLM generates SQL  
SQL → DuckDB executes → tables + charts  

---

## Architecture

Frontend (Vite + JS + Chart.js)  
↓  
FastAPI Backend (REST API)  
↓  
RAG Pipeline (Schema Retrieval + Groq LLM)  
↓  
SQL Generation  
↓  
DuckDB Execution  
↓  
Tables + Charts  

---

## Tech Stack

Backend: FastAPI, DuckDB, Pandas, SQLite  
AI/ML: RAG Pipeline, FAISS, Sentence Transformers, Cross-Encoder Reranker, Groq API (Llama 3.3 70B)  
Frontend: Vite, Vanilla JS, Chart.js  
Deployment: Docker, Railway  

---

## Features

- CSV and Excel upload with automatic schema detection  
- Column name normalization to SQL-safe snake_case  
- Natural language to SQL generation via RAG pipeline  
- Safe SQL execution (SELECT only)  
- Sample data injection into prompts for better accuracy  
- DuckDB OLAP queries  
- Automatic table and chart rendering  
- Dataset management (list, select, delete)  
- Query history tracking  

---

## Example

Input: average revenue by region  

Generated SQL:  
SELECT region, AVG(revenue) AS average_revenue  
FROM sales  
GROUP BY region;

Executed instantly on DuckDB. Results displayed as a table and auto-generated chart.

---

## Project Structure

app/ – FastAPI backend, API endpoints, ingestion service  
rag/ – RAG pipeline, prompt builder, LLM client  
frontend/ – Vite UI, Chart.js visualizations  
tests_rag/ – Unit tests for RAG components  

---

## Run Locally

Prerequisites:
- Python 3.11+  
- Node.js 18+  
- Groq API key (https://console.groq.com)  

---

Clone and setup:
git clone https://github.com/not-aryan7/DataPilot.git  
cd DataPilot  

---

Configure environment:

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here  

---

Start backend:

python -m venv venv  

Windows: venv\Scripts\activate  
macOS/Linux: source venv/bin/activate  

pip install -r requirements.txt  
uvicorn app.main:app --reload --port 8001  

Backend runs at http://127.0.0.1:8001  

---

Start frontend:

cd frontend  
npm install  
npm run dev  

Frontend runs at http://localhost:5173  

---

## API Endpoints

GET    /api/datasets         – List datasets  
POST   /api/upload           – Upload file  
POST   /api/ask              – Ask question  
DELETE /api/datasets/{id}    – Delete dataset  

---

## Deployment

DataPilot is deployed on Railway using Docker.

To deploy your own instance:

- Fork the repository  
- Sign up at https://railway.app and connect your repo  
- Add GROQ_API_KEY as an environment variable  
- Railway auto-detects Dockerfile and deploys  

---

## Safety

- SELECT queries only (no DROP, DELETE, UPDATE)  
- No data leaves your session  
- Designed for small to medium datasets  

---

## Authors

Ayush Neupane  
Aryan RajBhandari