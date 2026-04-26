"""
rag.py — Stage 4: answer() — grounded generation via OpenAI.

Combines the BM25 retriever with an LLM that is instructed to answer
ONLY from the provided context, and to refuse when the answer is absent.

Exposes:
  answer(question, k=TOP_K) -> {"answer": str, "retrieved_chunks": list[dict]}
"""
import os
from typing import Optional
from groq import Groq
from retriever import load_retriever, BM25Retriever
from config import TOP_K, LLM_MODEL

# ── System prompt (grounding contract) ────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a precise science tutor for NCERT Class 9 students.

STRICT RULES — follow without exception:
1. Answer ONLY using the information present in the provided Context Chunks.
2. If the answer cannot be found in the Context Chunks, respond with exactly:
     "I cannot answer this question from the provided chapter content."
   Do NOT guess, do NOT draw on general knowledge, do NOT attempt a partial answer.
3. Keep answers concise, factual, and student-friendly.
4. When possible, mirror the language of the textbook rather than paraphrasing.
"""

# ── Client ────────────────────────────────────────────────────────────────────
# You can securely add your Groq API key here.
# (If you don't want to hardcode it, leave it blank and run `export GROQ_API_KEY=gsk_...` in your terminal instead).
USER_API_KEY = "YOUR_API_KEY_HERE"

def _get_client() -> Groq:
    # 1. Try to get it from the environment first
    api_key = os.environ.get("GROQ_API_KEY", "")
    
    # 2. If it's not in the environment, use the variable defined above
    if not api_key:
        api_key = USER_API_KEY
        
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise EnvironmentError(
            "GROQ_API_KEY is not set.\n"
            "Please paste your API key in `USER_API_KEY` in rag.py or export it in the shell!"
        )
    return Groq(api_key=api_key)


# ── Core answer function ──────────────────────────────────────────────────────

def answer(
    question  : str,
    retriever : Optional[BM25Retriever] = None,
    k         : int = TOP_K,
    model     : str = LLM_MODEL,
) -> dict:
    """
    Full RAG answer pipeline.

    Parameters
    ----------
    question  : Natural-language question to answer.
    retriever : Pre-built BM25Retriever (lazy-loaded if None).
    k         : Number of context chunks to retrieve.
    model     : OpenAI model identifier.

    Returns
    -------
    {
        "answer"           : str        — Groq LLM response,
        "retrieved_chunks" : list[dict] — chunks used as context,
    }
    """
    if retriever is None:
        retriever = load_retriever()

    # Step 1 — Retrieve
    retrieved = retriever.retrieve(question, k=k)

    # Step 2 — Format context
    context_blocks = "\n\n".join(
        f"[Chunk {i+1} | Chapter: {r['chapter']} | "
        f"Section: {r['section']} | Type: {r['content_type']}]\n{r['text']}"
        for i, r in enumerate(retrieved)
    )

    user_message = (
        f"Context Chunks:\n{context_blocks}\n\n"
        f"Question: {question}"
    )

    # Step 3 — Generate
    client   = _get_client()
    response = client.chat.completions.create(
        model       = model,
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature = 0.1,
        max_tokens  = 512,
    )

    return {
        "answer"           : response.choices[0].message.content.strip(),
        "retrieved_chunks" : retrieved,
    }


# ── Quick smoke-test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_q = "What is the definition of uniform motion?"
    print(f"Question: {test_q}\n")
    result = answer(test_q)
    print("Answer:", result["answer"])
    print(f"\nBacked by {len(result['retrieved_chunks'])} chunks:")
    for r in result["retrieved_chunks"]:
        print(f"  [{r['section']}] score={r['bm25_score']} | {r['text'][:80]}…")
