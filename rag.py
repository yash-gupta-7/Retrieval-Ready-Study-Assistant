"""
rag.py — Stage 4: answer() — grounded generation via OpenAI.

Combines the BM25 retriever with an LLM that is instructed to answer
ONLY from the provided context, and to refuse when the answer is absent.

Exposes:
  answer(question, k=TOP_K) -> {"answer": str, "retrieved_chunks": list[dict]}
"""
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from retriever import load_retriever, SemanticRetriever
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

def _get_llm(model: str = LLM_MODEL) -> ChatGroq:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set.\n"
            "Please ensure it is set in your .env file or exported in the shell!"
        )
    return ChatGroq(model=model, api_key=api_key, temperature=0.1, max_tokens=512)

# ── Core answer function ──────────────────────────────────────────────────────

def answer(
    question  : str,
    retriever : Optional[SemanticRetriever] = None,
    k         : int = TOP_K,
    model     : str = LLM_MODEL,
) -> dict:
    """
    Full RAG answer pipeline.

    Parameters
    ----------
    question  : Natural-language question to answer.
    retriever : Pre-built SemanticRetriever (lazy-loaded if None).
    k         : Number of context chunks to retrieve.
    model     : Groq model identifier.

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

    # Step 3 — Generate using Langchain ChatGroq
    llm = _get_llm(model=model)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context Chunks:\n{context}\n\nQuestion: {question}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context_blocks,
        "question": question
    })

    return {
        "answer"           : response.content.strip(),
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
        print(f"  [{r['section']}] score={r.get('similarity_score', 0):.4f} | {r['text'][:80]}…")
