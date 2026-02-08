from __future__ import annotations


def build_answer_prompt(context_block: str, question: str) -> str:
    return (
        "You are a careful assistant answering questions about a document. "
        "Use ONLY the provided context. If the answer is not present, say exactly: "
        "\"Not found in document.\"\n\n"
        "Provide a concise, structured answer.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
    )


def build_summary_prompt(context_block: str) -> str:
    return (
        "Summarize the document using ONLY the provided context. "
        "Write 8-12 short lines.\n\n"
        f"Context:\n{context_block}\n"
    )
