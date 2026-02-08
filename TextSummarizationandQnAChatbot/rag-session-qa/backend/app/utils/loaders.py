from __future__ import annotations

import os
from typing import Optional

from pypdf import PdfReader
from docx import Document


SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


def _guess_type(content_type: Optional[str], filename: str) -> str:
    if content_type in SUPPORTED_MIME_TYPES:
        return SUPPORTED_MIME_TYPES[content_type]
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    if ext == ".txt":
        return "txt"
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def extract_text(file_path: str, content_type: Optional[str], filename: str) -> str:
    file_type = _guess_type(content_type, filename)
    if file_type == "pdf":
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages).strip()

    if file_type == "docx":
        doc = Document(file_path)
        paras = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paras).strip()

    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")
