from typing import Dict, Any, List
from backend.rag.store import RAGStore
from backend.llm_client import LLMClient

class SearchAgent:
    def __init__(self, rag: RAGStore):
        self.rag = rag
        self.llm = LLMClient()

    def run(self, reformulated_query: str, intent: str) -> Dict[str, Any]:
        # Retrieve top chunks
        hits = self.rag.search(reformulated_query, top_k=3)
        sources = sorted(list({h["doc_id"] for h in hits}))
        chunks = [h["chunk"] for h in hits]

        # Ask LLM to draft rep-facing response grounded in chunks
        answer = self.llm.generate_text(
            task="rag_answer",
            inputs={"intent": intent, "query": reformulated_query, "chunks": chunks},
        )

        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": chunks,
        }
