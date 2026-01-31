# DataPilot

Self-serve analytics: Upload CSV → Ask questions → Get SQL + Results + Charts

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/not-aryan7/DataPilot.git
cd DataPilot
```

### 2. Set up virtual environment
```bash
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\activate

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

## Ports & URLs

| Service | URL |
|---------|-----|
| API | http://127.0.0.1:8000 |
| Swagger Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

## Project Structure
```
DataPilot/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── api/             # API routes
│   ├── core/            # Config, database
│   ├── services/        # Business logic
│   └── utils/           # Helpers
├── data/                # Uploaded files (gitignored)
├── requirements.txt
└── README.md
```

## Team Split
- **Backend/Product**: FastAPI, DuckDB, file handling, SQL execution
- **AI/RAG**: Embeddings, FAISS, vLLM, SQL generation
