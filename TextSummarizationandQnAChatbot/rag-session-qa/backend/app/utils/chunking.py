from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    if chunk_size <= 0:
        chunk_size = 800
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 3)

    chunks: list[str] = []
    start = 0
    length = len(cleaned)

    while start < length:
        end = min(length, start + chunk_size)
        if end < length:
            space = cleaned.rfind(" ", start, end)
            if space > start + (chunk_size // 2):
                end = space
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(0, end - overlap)

    return chunks
