# Session-Based RAG Document Q&A + DeepEval

A complete demo of a session-based RAG document Q&A system with FastAPI, React (Vite), ChromaDB, OpenAI embeddings/completions, and DeepEval evaluation.

## Features

- Upload PDF/DOCX/TXT
- Ask questions grounded in retrieved context with citations
- Generate 8–12 line summaries
- Session-based vector store (new upload clears previous vectors)
- Evaluation layers for retrieval quality and output quality

## Repo Structure

```
rag-session-qa/
  backend/
  frontend/
  .env.example
  README.md
```

## Setup

### 1) Environment Variables

Copy `.env.example` to `.env` in the repo root (or export variables in your shell):

```bash
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_EMBED_MODEL=text-embedding-3-small
export TOP_K=5
export MAX_CHUNKS_FOR_SUMMARY=12
export CHUNK_SIZE=800
export CHUNK_OVERLAP=120
export CORS_ORIGINS=http://localhost:5173
export DEEPEVAL_CONFIDENT_API_KEY=
```

### 2) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3) Frontend

```bash
cd frontend
npm install
npm run dev
```

If your backend is not at `http://localhost:8000`, set:

```bash
export VITE_API_URL=http://localhost:8000
```

## Demo Flow

1. Start the backend and frontend.
2. Upload a document.
3. Ask questions and view answers with citations.
4. Click **Summarise** for a concise summary.
5. Uploading a new document resets the vector store and session.

## Notes

- This is session-based: **no persistent storage**.
- On each upload, the server resets the vector store and creates a new `session_id`.
