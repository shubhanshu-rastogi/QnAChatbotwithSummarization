from __future__ import annotations

from typing import Any
import re

from openai import OpenAI

from .config import settings
from .utils.prompts import build_answer_prompt, build_summary_prompt
from .vectorstore import query, get_chunks


_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _build_context(chunks: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]], list[str]]:
    context_lines: list[str] = []
    citations: list[dict[str, Any]] = []
    retrieval_context: list[str] = []

    for idx, chunk in enumerate(chunks):
        cite_id = f"C{idx + 1}"
        metadata = chunk.get("metadata", {})
        text = chunk.get("text", "")
        snippet = text[:320] + ("..." if len(text) > 320 else "")

        citations.append(
            {
                "id": cite_id,
                "chunk_id": chunk.get("chunk_id"),
                "snippet": snippet,
                "metadata": metadata,
            }
        )
        context_lines.append(
            f"[{cite_id}] (source: {metadata.get('source_filename', 'unknown')}, chunk: {metadata.get('chunk_index', 'n/a')})\n{text}"
        )
        retrieval_context.append(text)

    return "\n\n".join(context_lines), citations, retrieval_context


def _extract_player_name(question: str) -> str | None:
    match = re.search(
        r"\bdid\s+(?P<name>.+?)\s+(hit|score|make)\b",
        question,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group("name").strip()

    names = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", question)
    if names:
        return names[-1]
    return None


def _normalize_player_name(name: str) -> str | None:
    tokens = re.findall(r"[A-Za-z]+", name)
    if not tokens:
        return None
    return " ".join(tokens)


def _try_count_from_context(
    question: str, chunks: list[dict[str, Any]]
) -> tuple[str, list[int]] | None:
    q = question.lower()
    if not any(phrase in q for phrase in ["how many", "number of", "count of", "count"]):
        return None

    term = None
    if any(t in q for t in ["four", "fours", "4"]):
        term = "FOUR"
        term_label = "four"
        term_plural = "fours"
    elif any(t in q for t in ["six", "sixes", "6"]):
        term = "SIX"
        term_label = "six"
        term_plural = "sixes"
    else:
        return None

    player_raw = _extract_player_name(question)
    if not player_raw:
        return None
    player = _normalize_player_name(player_raw)
    if not player:
        return None
    player_re = re.escape(player)
    player_display = " ".join(word.capitalize() for word in player.split())
    used_indices: list[int] = []

    # 1) Prefer explicit stats like: "Tilak Varma ... [4s-3 6s-3]"
    try:
        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "")
            stats_match = re.search(
                rf"{player_re}[^\r\n]{{0,120}}\[(?P<stats>[^\]]+)\]",
                text,
                flags=re.IGNORECASE,
            )
            if stats_match:
                stats = stats_match.group("stats")
                four_match = re.search(r"4s-(\d+)", stats, flags=re.IGNORECASE)
                six_match = re.search(r"6s-(\d+)", stats, flags=re.IGNORECASE)
                if term_label == "four" and four_match:
                    used_indices.append(i)
                    count = int(four_match.group(1))
                    noun = term_label if count == 1 else term_plural
                    return (f"{player_display} hit {count} {noun}.", used_indices)
                if term_label == "six" and six_match:
                    used_indices.append(i)
                    count = int(six_match.group(1))
                    noun = term_label if count == 1 else term_plural
                    return (f"{player_display} hit {count} {noun}.", used_indices)
    except re.error:
        return None

    # 2) Count scoring events from ball-by-ball lines
    term_word = "SIX" if term_label == "six" else "FOUR"
    count = 0
    try:
        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "")
            # Split into ball-by-ball events like "8.5 6 Bowler to Batter, SIX"
            events = re.split(r"(?=\b\d+\.\d+\s+)", text)
            event_hits = 0
            for event in events:
                if re.search(rf"\bto\s+{player_re}\b", event, flags=re.IGNORECASE) and re.search(
                    rf"\b{term_word}\b", event, flags=re.IGNORECASE
                ):
                    event_hits += 1
            if event_hits > 0:
                count += event_hits
                used_indices.append(i)
    except re.error:
        return None

    if count == 0:
        return ("Not found in document.", used_indices)

    noun = term_label if count == 1 else term_plural
    answer = f"{player_display} hit {count} {noun}."
    return (answer, used_indices)


def _is_count_question(question: str) -> bool:
    q = question.lower()
    has_count = any(phrase in q for phrase in ["how many", "number of", "count of", "count"])
    has_term = any(t in q for t in ["four", "fours", "4", "six", "sixes", "6"])
    return has_count and has_term


def _strip_citations(text: str) -> str:
    return re.sub(r"\s*\[C\\d+\\]", "", text, flags=re.IGNORECASE).strip()


def answer_question(session_id: str, question: str) -> dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    if _is_count_question(question):
        all_chunks = get_chunks(session_id, limit=None)
        count_result = _try_count_from_context(question, all_chunks)
        if count_result is not None:
            answer, used_indices = count_result
            used_chunks = [all_chunks[i] for i in used_indices] if used_indices else []
            context_block, citations, retrieval_context = _build_context(used_chunks)
            return {
                "answer": answer,
                "citations": citations,
                "retrieval_context": retrieval_context,
            }

    embed_resp = _client.embeddings.create(
        model=settings.OPENAI_EMBED_MODEL,
        input=[question],
    )
    query_embedding = embed_resp.data[0].embedding

    results = query(session_id, query_embedding, settings.TOP_K)
    context_block, citations, retrieval_context = _build_context(results)

    prompt = build_answer_prompt(context_block, question)
    response = _client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a precise RAG assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    answer = _strip_citations(response.choices[0].message.content.strip())

    return {
        "answer": answer,
        "citations": citations,
        "retrieval_context": retrieval_context,
    }


def summarise(session_id: str) -> dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    chunks = get_chunks(session_id, limit=settings.MAX_CHUNKS_FOR_SUMMARY)
    context_block, citations, _ = _build_context(chunks)

    prompt = build_summary_prompt(context_block)
    response = _client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You summarize documents faithfully."},
            {"role": "user", "content": prompt},
        ],
    )

    summary = _strip_citations(response.choices[0].message.content.strip())

    return {"summary": summary, "citations": citations}
