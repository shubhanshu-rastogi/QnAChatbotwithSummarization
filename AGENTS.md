# AGENTS.md

Project: rag-session-qa (session-based RAG document Q&A + DeepEval evaluation).

Key constraints:
- Session-based only; no long-term vector storage.
- On each upload, reset the vector store and create a new session_id.
- Backend: FastAPI; Frontend: React (Vite); ChromaDB; OpenAI embeddings + chat; DeepEval.
- Provide runnable code, README, .env.example, and evaluation notebooks.

Primary endpoints:
- POST /upload
- POST /ask
- POST /summary
- GET /health

Evaluation layers:
- Retrieval quality: Contextual Precision/Recall/Relevance.
- Output quality: Faithfulness/Answer Relevance/Completeness.

Follow user requirements in the main README and repo structure.
