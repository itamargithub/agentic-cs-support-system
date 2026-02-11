# Agentic Customer Service Support System

An end-to-end, agentic customer support assistant for banking contact centers. A Streamlit UI for representatives and managers talks to a FastAPI backend that orchestrates three agents (reformulation, RAG search, validation) over a small banking knowledge base, with all interactions logged to SQLite for reporting.

This repo implements a multi-agent customer service support pipeline:

**Rep question → Reformulation Agent → Search/RAG Agent → Validation Agent → Response + Confidence + Sources**

It includes:
- A small banking knowledge base (Markdown docs)
- A local RAG retriever (TF-IDF + cosine similarity) so it works without external services
- Optional Claude (Anthropic) integration via `ANTHROPIC_API_KEY`
- FastAPI backend + SQLite logging
- Streamlit UI with:
  - Representative screen
  - Manager dashboard with meaningful metrics

> The system is structured so you can iterate easily and switch the agents to real Claude calls by setting `ANTHROPIC_API_KEY`.

---

## Quickstart (Local)

### 1) Create venv + install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Build the search index
```bash
python backend/scripts/build_index.py
```

### 3) Start backend API
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4) Start UI
In another terminal:
```bash
streamlit run ui/app.py --server.port 8501
```

Open:
- UI: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## Run with Docker (optional)
```bash
docker compose up --build
```
UI: http://localhost:8501

---

## Environment Variables
- `ANTHROPIC_API_KEY` (optional): if set, agents use Claude for reformulation + validation and for generating the final answer.
- `AGENT_MODE` (optional): `auto` (default) or `mock`
  - `mock` makes everything deterministic for demos without external calls.

---

## Demo Script (2–3 minutes)
1. In Rep View, ask:
   - "Customer is yelling that money was stolen from his card"
2. Show:
   - Reformulated query (visible)
   - Answer + sources + confidence
3. Click "Open source" to view full KB doc
4. Go to Manager Dashboard:
   - Show queries per rep
   - Topics distribution
   - Avg confidence and low-confidence list

---

## Repo Structure
- `backend/` FastAPI app, agents, RAG, SQLite logging
- `backend/knowledge_base/` KB documents
- `backend/scripts/build_index.py` builds the TF-IDF index
- `ui/` Streamlit UI (two screens)
