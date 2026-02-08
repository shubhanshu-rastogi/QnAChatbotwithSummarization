from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .ingest import ingest_upload
from .rag import answer_question, summarise
from .schemas import UploadResponse, AskRequest, AskResponse, SummaryRequest, SummaryResponse

app = FastAPI(title="Session RAG Q&A")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(status_code=400, detail="No file provided.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = ingest_upload(content, file.filename, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    return UploadResponse(
        session_id=result["session_id"],
        message="Document indexed successfully.",
        num_chunks=result["num_chunks"],
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    try:
        result = answer_question(request.session_id, request.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ask failed: {exc}")

    return AskResponse(**result)


@app.post("/summary", response_model=SummaryResponse)
def summary(request: SummaryRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    try:
        result = summarise(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summary failed: {exc}")

    return SummaryResponse(**result)
