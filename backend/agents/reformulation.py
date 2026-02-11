from backend.llm_client import LLMClient

class ReformulationAgent:
    def __init__(self):
        self.llm = LLMClient()

    def run(self, question: str):
        # In production: prompt Claude to output strict JSON
        out = self.llm.generate_json(
            task="reformulation",
            schema_hint="{intent: string, query: string, entities: list}",
            inputs={"question": question},
        )
        # Minimal normalization
        return {"intent": out["intent"], "query": out["query"], "mode": self.llm.provider}
