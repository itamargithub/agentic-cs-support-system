from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import time

from backend.rag.store import RAGStore
from backend.agents.reformulation import ReformulationAgent
from backend.agents.search import SearchAgent
from backend.agents.validation import ValidationAgent
from backend.db import DB

app = FastAPI(title="Agentic CS Support System", version="1.0.0")

rag = RAGStore()
db = DB()

class AskRequest(BaseModel):
    rep_id: str = Field(default="rep-1")
    question: str

class AskResponse(BaseModel):
    rep_id: str
    question: str
    intent: str
    reformulated_query: str
    answer: str
    confidence: int
    sources: List[str]
    latency_ms: int

@app.on_event("startup")
def startup():
    rag.load_or_build()
    db.init()

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t0 = time.time()

    # 1) Reformulate
    reform = ReformulationAgent().run(req.question)

    # 2) Search + RAG answer
    search = SearchAgent(rag=rag).run(reformulated_query=reform["query"], intent=reform["intent"])

    # 3) Validate / score
    valid = ValidationAgent().run(
        question=req.question,
        reformulated_query=reform["query"],
        intent=reform["intent"],
        answer=search["answer"],
        sources=search["sources"],
        retrieved_chunks=search["retrieved_chunks"],
    )

    latency_ms = int((time.time() - t0) * 1000)

    # Log interaction for dashboard
    db.log_interaction(
        rep_id=req.rep_id,
        question=req.question,
        intent=reform["intent"],
        reformulated_query=reform["query"],
        answer=search["answer"],
        sources=",".join(search["sources"]),
        confidence=valid["confidence"],
        latency_ms=latency_ms,
        agent_mode=valid.get("mode", "unknown"),
    )

    return AskResponse(
        rep_id=req.rep_id,
        question=req.question,
        intent=reform["intent"],
        reformulated_query=reform["query"],
        answer=search["answer"],
        confidence=valid["confidence"],
        sources=search["sources"],
        latency_ms=latency_ms,
    )

@app.get("/source/{doc_id}", response_class=PlainTextResponse)
def source(doc_id: str):
    text = rag.get_document_text(doc_id)
    if text is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return text

@app.get("/stats")
def stats():
    return db.get_stats()
