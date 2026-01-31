# DataPilot

Self-serve analytics: Upload CSV → Ask questions → Get SQL + Results

## Quick Start

### Backend
```bash
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| API Docs | http://127.0.0.1:8000/docs |
