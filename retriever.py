"""
retriever.py — Semantic retriever using Chroma and text-embedding-3-small.

Loads: data/processed/chunks.json   (produced by preprocess.py)

Exposes:
  SemanticRetriever      — class (build index, query)
  load_retriever()       — factory that builds from disk
"""
import json
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import CHUNKS_JSON_FILE, CHROMA_DB_DIR, TOP_K, EMBEDDING_MODEL

class SemanticRetriever:
    """Wrapper around LangChain Chroma that keeps chunk metadata alongside scores."""

    def __init__(self, chunks: list[dict]):
        if not chunks:
            raise ValueError("Cannot build retriever from empty chunk list.")
        
        self.chunks = chunks
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # Check if Chroma DB already exists to avoid re-embedding every time
        if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
            print(f"  [retriever] Loading existing Chroma index from {CHROMA_DB_DIR}")
            self._vectorstore = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=self.embeddings
            )
        else:
            print(f"  [retriever] Building new Chroma index over {len(chunks)} chunks (this may take a moment)")
            docs = [
                Document(
                    page_content=c["text"], 
                    metadata={
                        "chapter": c["chapter"],
                        "section": c["section"],
                        "content_type": c["content_type"],
                        "chunk_idx": i
                    }
                )
                for i, c in enumerate(chunks)
            ]
            self._vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=CHROMA_DB_DIR
            )
            print(f"  [retriever] Index persisted to {CHROMA_DB_DIR}")

    def retrieve(self, query: str, k: int = TOP_K) -> list[dict]:
        """
        Return the top-k chunks most semantically relevant to the query.
        Each result is the original chunk dict plus a 'similarity_score' key.
        """
        results_with_scores = self._vectorstore.similarity_search_with_score(query, k=k)
        
        results = []
        for doc, score in results_with_scores:
            idx = doc.metadata.get("chunk_idx")
            if idx is not None and idx < len(self.chunks):
                result = self.chunks[idx].copy()
            else:
                result = {
                    "text": doc.page_content,
                    "chapter": doc.metadata.get("chapter", "Unknown"),
                    "section": doc.metadata.get("section", "Unknown"),
                    "content_type": doc.metadata.get("content_type", "Unknown")
                }
            # Note: Chroma similarity_search_with_score returns distance (lower is better) by default
            result["similarity_score"] = round(float(score), 4)
            results.append(result)
        return results

    def __repr__(self) -> str:
        return f"SemanticRetriever(n_chunks={len(self.chunks)})"

def load_retriever(chunks_file: str = CHUNKS_JSON_FILE) -> "SemanticRetriever":
    """
    Load chunk metadata from disk and return a ready-to-query SemanticRetriever.
    Raises FileNotFoundError if preprocess.py has not been run yet.
    """
    if not os.path.exists(chunks_file):
        raise FileNotFoundError(
            f"Chunk store not found: '{chunks_file}'\n"
            "Run preprocess.py first."
        )
    with open(chunks_file, "r", encoding="utf-8") as fh:
        chunks = json.load(fh)
    return SemanticRetriever(chunks)

if __name__ == "__main__":
    retriever = load_retriever()

    test_queries = [
        "What is the definition of uniform motion?",
        "State Newton's second law of motion.",
        "How does gravitational force depend on mass?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        for r in retriever.retrieve(q, k=3):
            print(f"  [score={r.get('similarity_score', 0):.4f}] [{r['section']}] {r['text'][:110]}…")
