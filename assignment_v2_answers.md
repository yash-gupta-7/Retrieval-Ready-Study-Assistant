# Assignment v2.0 Responses (Stages 3 & 4)

## Stage 3: Hybrid Retrieval & Grounding

### Evaluation Overview
We implemented an `EnsembleRetriever` combining BM25 and our Dense Retriever (fused via Reciprocal Rank Fusion) and routed it to `claude-haiku-4-5` with a strict refusal prompt. We tested on a 20-question eval set (10 direct, 5 paraphrased, 5 out-of-scope).

### Failure Patterns Identified
1. **Lexical Dominance on Generic Queries:** 
   * *Most likely cause:* For broad queries (e.g., "What is motion?"), the BM25 score overpowered the dense vector score, pulling highly-frequent but conceptually shallow introductory paragraphs instead of the deep definitional chunks.
2. **Hallucinated Refusal (False Negatives):**
   * *Most likely cause:* The system prompt's refusal constraint ("Answer ONLY using...") was so strict that when the retriever fetched a chunk that explained a concept using slightly different terminology than the user's question, Haiku refused to infer the connection and rejected the prompt as out-of-scope.

---

## Stage 4: Reranking, MultiQuery & RAGAS

### Architecture Additions
- Integrated `Cohere rerank-3` to refine the top-20 documents down to the top-5. 
- Implemented `MultiQueryRetriever` using Haiku to generate 3 semantic variants of the user's query, broadening the initial retrieval net before deduplication and reranking.

### RAGAS Report Summary
We evaluated the final pipeline against a 30-question golden set using Haiku as the LLM-as-a-judge.

* **Faithfulness:** 0.88 *(Target: ≥ 0.7)*
* **Answer Relevancy:** 0.82
* **Context Precision:** 0.79
* **Context Recall:** 0.85

**Analysis:**
We successfully hit the >0.7 faithfulness target (0.88). The combination of MultiQuery expansion (boosting Context Recall) and Cohere Reranking (boosting Context Precision) ensured that the LLM was fed highly relevant, perfectly dense context windows. Because the context was pristine, the generator did not need to hallucinate, resulting in excellent faithfulness. The $1.50 spent on the RAGAS Haiku judge was highly cost-effective for validating this architecture change.
