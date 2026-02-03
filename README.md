# DataPilot

DataPilot is a lightweight analytics tool that lets you query spreadsheets using plain English.

Upload a CSV or Excel file → ask a question → an LLM generates SQL → DuckDB executes it → results are returned as tables and charts.

The goal was to build a simple, local-first alternative to tools like Power BI or Tableau while learning how to connect AI + databases + APIs + frontend in one system.

---

## Demo

Example questions:

- total revenue by year
- sum of sales by region
- average price per product
- top 5 rows
- group by month

---

## Architecture
Frontend (Vite + JS)
↓
FastAPI backend
↓
AI → SQL generation
↓
DuckDB execution
↓
Results → charts

---

## Tech Stack

Backend
- FastAPI
- DuckDB
- Pandas

Frontend
- Vite
- Vanilla JavaScript
- Chart.js

AI
- local LLM for text-to-SQl generation

---

## Why these choices

**FastAPI**
- simple REST APIs
- async support
- auto docs
- lightweight

**DuckDB**
- embedded analytics database
- no server required
- very fast for aggregations
- great for local OLAP workloads

**Pandas**
- easy CSV/Excel ingestion
- schema cleaning

**Chart.js**
- quick visualization without heavy frontend frameworks

The focus was keeping everything local, simple, and fast.

---

## Features

- CSV + Excel upload
- automatic schema detection
- column name normalization
- natural language → SQL
- safe SELECT-only execution
- results table
- automatic charts
- dataset history

---


### This project was mainly about learning:

- designing APIs

- handling file ingestion

- working with analytical databases

- building text-to-SQl systems with LLMs

- connecting backend + frontend cleanly

- building small end-to-end products


Notes

- runs fully local

-designed for small/medium datasets

-not meant for production scale

-SELECT queries only for safety

## Run locally

### Backend

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend
cd frontend
npm install
npm run dev
----
