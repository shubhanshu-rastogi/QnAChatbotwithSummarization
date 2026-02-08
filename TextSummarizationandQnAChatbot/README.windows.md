# Windows Setup

This repo contains a session-based RAG Document Q&A app.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Backend (FastAPI)

```powershell
cd rag-session-qa\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

$env:OPENAI_API_KEY="your_key"
# Optional
$env:OPENAI_MODEL="gpt-4o-mini"
$env:OPENAI_EMBED_MODEL="text-embedding-3-small"
$env:CORS_ORIGINS="http://localhost:5173"

uvicorn app.main:app --port 8000
```

## Frontend (Vite)

```powershell
cd rag-session-qa\frontend
npm install
npm run dev
```

UI: http://localhost:5173

## Notebooks (DeepEval)

```powershell
cd rag-session-qa
python -m pip install -r eval\requirements.txt
python -m pip install ipykernel
python -m ipykernel install --user --name rag-session-qa --display-name "rag-session-qa"
python -m jupyter notebook
```

Open notebooks in `eval/notebooks/`.
