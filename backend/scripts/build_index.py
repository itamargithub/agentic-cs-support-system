from backend.rag.store import RAGStore

if __name__ == "__main__":
    store = RAGStore()
    store.build()
    print("✅ Built TF-IDF index from knowledge base documents.")
