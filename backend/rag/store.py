import os
import glob
import pickle
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
KB_DIR = os.path.join(os.path.dirname(BASE_DIR), "knowledge_base")
INDEX_PATH = os.path.join(DATA_DIR, "tfidf_index.pkl")

def chunk_text(text: str, max_chars: int = 700, overlap: int = 120) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+max_chars]
        chunks.append(chunk.strip())
        i += (max_chars - overlap)
    return [c for c in chunks if c]

class RAGStore:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix = None
        self.metadatas: List[Dict] = []
        self.doc_texts: Dict[str, str] = {}

    def load_or_build(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "rb") as f:
                obj = pickle.load(f)
            self.vectorizer = obj["vectorizer"]
            self.matrix = obj["matrix"]
            self.metadatas = obj["metadatas"]
            self.doc_texts = obj["doc_texts"]
            return
        self.build()

    def build(self):
        # Ensure the data directory exists when building the index (important for fresh Docker images)
        os.makedirs(DATA_DIR, exist_ok=True)

        paths = sorted(glob.glob(os.path.join(KB_DIR, "*.md")))
        docs = []
        self.doc_texts = {}
        self.metadatas = []
        for p in paths:
            doc_id = os.path.splitext(os.path.basename(p))[0].split("_")[0]  # e.g., KB-001
            with open(p, "r", encoding="utf-8") as f:
                text = f.read()
            self.doc_texts[doc_id] = text
            chunks = chunk_text(text)
            for idx, ch in enumerate(chunks):
                docs.append(ch)
                self.metadatas.append({"doc_id": doc_id, "chunk_id": idx, "chunk": ch})

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(docs)

        with open(INDEX_PATH, "wb") as f:
            pickle.dump(
                {
                    "vectorizer": self.vectorizer,
                    "matrix": self.matrix,
                    "metadatas": self.metadatas,
                    "doc_texts": self.doc_texts,
                },
                f,
            )

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.vectorizer or self.matrix is None:
            self.load_or_build()
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix).flatten()
        best_idx = sims.argsort()[::-1][:top_k]
        hits = []
        for i in best_idx:
            md = self.metadatas[int(i)]
            hits.append({"score": float(sims[int(i)]), "doc_id": md["doc_id"], "chunk": md["chunk"]})
        return hits

    def get_document_text(self, doc_id: str) -> Optional[str]:
        # doc_id like "KB-004"
        if not self.doc_texts:
            self.load_or_build()
        return self.doc_texts.get(doc_id)
