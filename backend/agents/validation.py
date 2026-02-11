from typing import Dict, Any, List
from backend.llm_client import LLMClient

class ValidationAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, question: str, reformulated_query: str, intent: str, answer: str, sources: List[str], retrieved_chunks: List[str]) -> Dict[str, Any]:
        out = self.llm.generate_json(
            task="validation",
            schema_hint="{confidence: int, notes: string}",
            inputs={
                "question": question,
                "reformulated_query": reformulated_query,
                "intent": intent,
                "answer": answer,
                "sources": sources,
                "retrieved_chunks": retrieved_chunks,
            },
        )
        conf = int(out.get("confidence", 60))
        conf = max(1, min(99, conf))
        return {"confidence": conf, "notes": out.get("notes", ""), "mode": self.llm.provider}
