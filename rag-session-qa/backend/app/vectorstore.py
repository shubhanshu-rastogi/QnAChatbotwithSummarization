from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

_COLLECTION_NAME = "rag_session"

_client = chromadb.Client(
    ChromaSettings(allow_reset=True, anonymized_telemetry=False)
)
_collection = None
_current_session_id: str | None = None


def reset_session(session_id: str) -> None:
    global _collection, _current_session_id
    try:
        _client.delete_collection(_COLLECTION_NAME)
    except Exception:
        pass
    _collection = _client.create_collection(
        _COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )
    _current_session_id = session_id


def get_current_session_id() -> str | None:
    return _current_session_id


def _ensure_collection():
    global _collection
    if _collection is None:
        _collection = _client.create_collection(
            _COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )
    return _collection


def upsert_chunks(
    session_id: str, chunks: list[str], metadatas: list[dict[str, Any]], embeddings: list[list[float]]
) -> None:
    if session_id != _current_session_id:
        raise ValueError("Session mismatch or expired session.")
    collection = _ensure_collection()
    ids = [f"{session_id}_{i}" for i in range(len(chunks))]
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )


def query(session_id: str, query_embedding: list[float], top_k: int) -> list[dict[str, Any]]:
    if session_id != _current_session_id:
        raise ValueError("Session not found. Please upload a document.")
    collection = _ensure_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(
            {
                "chunk_id": ids[i],
                "text": doc,
                "metadata": metas[i],
                "score": dists[i],
            }
        )
    return formatted


def get_chunks(session_id: str, limit: int | None = None) -> list[dict[str, Any]]:
    if session_id != _current_session_id:
        raise ValueError("Session not found. Please upload a document.")
    collection = _ensure_collection()
    results = collection.get(include=["documents", "metadatas"])
    docs = results.get("documents", [])
    metas = results.get("metadatas", [])
    ids = results.get("ids", [])

    combined = []
    for i, doc in enumerate(docs):
        chunk_id = ids[i] if i < len(ids) else f"{session_id}_{i}"
        combined.append(
            {
                "chunk_id": chunk_id,
                "text": doc,
                "metadata": metas[i],
            }
        )

    combined.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
    if limit is not None:
        combined = combined[:limit]
    return combined
