"""
retriever.py — Lexical BM25 retriever over annotated chunk store.

Loads: data/processed/chunks.json   (produced by preprocess.py)

Exposes:
  BM25Retriever          — class (build index, query)
  load_retriever()       — factory that builds from disk
"""
import re
import json
import os
from rank_bm25 import BM25Okapi
from config import CHUNKS_JSON_FILE, TOP_K


# ── Tokeniser ─────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    return re.sub(r"[^\w\s]", "", text.lower()).split()


# ── Retriever class ───────────────────────────────────────────────────────────

class BM25Retriever:
    """Thin wrapper around rank-bm25 that keeps chunk metadata alongside scores."""

    def __init__(self, chunks: list[dict]):
        if not chunks:
            raise ValueError("Cannot build retriever from empty chunk list.")
        self.chunks   = chunks
        self._corpus  = [_tokenize(c["text"]) for c in chunks]
        self._bm25    = BM25Okapi(self._corpus)
        print(f"  [retriever] BM25 index built over {len(chunks)} chunks")

    # ------------------------------------------------------------------
    def retrieve(self, query: str, k: int = TOP_K) -> list[dict]:
        """
        Return the top-k chunks most relevant to query.
        Each result is the original chunk dict plus a 'bm25_score' key.
        """
        q_tokens = _tokenize(query)
        scores   = self._bm25.get_scores(q_tokens)
        top_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        results = []
        for idx in top_idxs:
            result = self.chunks[idx].copy()
            result["bm25_score"] = round(float(scores[idx]), 4)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"BM25Retriever(n_chunks={len(self.chunks)})"


# ── Factory ───────────────────────────────────────────────────────────────────

def load_retriever(chunks_file: str = CHUNKS_JSON_FILE) -> "BM25Retriever":
    """
    Load chunk metadata from disk and return a ready-to-query BM25Retriever.
    Raises FileNotFoundError if preprocess.py has not been run yet.
    """
    if not os.path.exists(chunks_file):
        raise FileNotFoundError(
            f"Chunk store not found: '{chunks_file}'\n"
            "Run preprocess.py first."
        )
    with open(chunks_file, "r", encoding="utf-8") as fh:
        chunks = json.load(fh)
    return BM25Retriever(chunks)


# ── Quick smoke-test ──────────────────────────────────────────────────────────

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
            print(f"  [score={r['bm25_score']:.4f}] [{r['section']}] {r['text'][:110]}…")
