# macOS Setup

This repo contains a session-based RAG Document Q&A app.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Backend (FastAPI)

```bash
cd rag-session-qa/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_API_KEY=your_key
# Optional
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_EMBED_MODEL=text-embedding-3-small
export CORS_ORIGINS=http://localhost:5173

uvicorn app.main:app --port 8000
```

## Frontend (Vite)

```bash
cd rag-session-qa/frontend
npm install
npm run dev
```

UI: http://localhost:5173

## Notebooks (DeepEval)

```bash
cd rag-session-qa
python3.11 -m pip install -r eval/requirements.txt
python3.11 -m pip install ipykernel
python3.11 -m ipykernel install --user --name rag-session-qa --display-name "rag-session-qa"
python3.11 -m jupyter notebook
```

Open notebooks in `eval/notebooks/`.
