from __future__ import annotations

import os
import tempfile
from uuid import uuid4

from openai import OpenAI

from .config import settings
from .utils.loaders import extract_text
from .utils.chunking import chunk_text
from .vectorstore import reset_session, upsert_chunks


_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ingest_upload(file_bytes: bytes, filename: str, content_type: str | None) -> dict:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    session_id = str(uuid4())
    reset_session(session_id)

    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path, content_type, filename)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    if not text.strip():
        raise ValueError("No readable text found in the document.")

    chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("Document produced no chunks after processing.")

    embed_resp = _client.embeddings.create(
        model=settings.OPENAI_EMBED_MODEL,
        input=chunks,
    )
    embeddings = [item.embedding for item in embed_resp.data]

    metadatas = [
        {
            "session_id": session_id,
            "chunk_index": i,
            "source_filename": filename,
        }
        for i in range(len(chunks))
    ]

    upsert_chunks(session_id, chunks, metadatas, embeddings)

    return {"session_id": session_id, "num_chunks": len(chunks)}
