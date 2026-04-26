# Retrieval-Ready Study Assistant — Assignment Responses

## Part A — Your implementation artifacts

### A1. Your chunking parameters
**Parameters:**
- `CHUNK_WINDOW`: 5 sentences per chunk
- `CHUNK_OVERLAP`: 2 sentences overlap (40%)
- **Handling:** Sentences are split using NLTK `punkt` tokenizer to ensure boundaries are strictly at the sentence level so no concept is split awkwardly mid-sentence.

**Observation that pushed these values:**
When analyzing the raw text output from the PyMuPDF extraction, I observed that a typical sentence in this Class 9 Science textbook averages around 20 tokens. I specifically wanted my chunks to be around 100 tokens long to fit well within LLM context windows while containing a complete thought. 5 sentences yielded exactly ~100 tokens. I chose a 40% (2-sentence) overlap because many physics concepts in the text (like explanations of inertia) straddle consecutive sentences. When testing a 0-overlap approach, I noticed key explanations were being truncated right when the textbook was about to provide the crucial example, leading to incomplete retrieval.

### A2. A retrieved chunk that was wrong for its query
**Query:** "State Newton's second law of motion."

**Wrong Retrieved Chunk:** 
> "These three laws are known as Newton’s laws of motion. The first law of motion is stated as: An object remains in a state of rest or of uniform motion in a straight line unless compelled to change that state by an applied force. In other words, all objects resist a change in their state of motion. In a qualitative way, the tendency of undisturbed objects to stay at rest or to keep moving with the same velocity is called inertia. This is why, the first law of motion is also known as the law of inertia."

**Why it was retrieved:**
My system uses a BM25 lexical retriever. The query contains the terms "Newton's", "law", "of", "motion". The retrieved chunk contains the exact string "Newton's laws of motion" and repeats "law of motion" three separate times, resulting in an extremely high lexical overlap score. BM25 does not understand semantic meaning, so the single token difference ("first" vs "second") was completely overpowered by the frequency of the other matching words.

### A3. Your grounding prompt, v1 and v(final)
I only wrote one version of the prompt for this pipeline iteration, which served as my final version:

```python
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
```
**Why I didn't need to iterate:** 
I designed this prompt defensively from the start. Anticipating that LLMs (specifically Llama 3.1) tend to hallucinate out-of-scope answers, I hardcoded the exact refusal string I wanted the LLM to output (Rule 2). This guaranteed that my programmatic evaluation script (`_score_refusal` in `run_eval.py`) could cleanly catch refusals via a simple substring match without needing complex parsing logic.

---

## Part B — Numbers from your evaluation

### B1. Your evaluation scores
Out of the 19 questions in the evaluation set (`eval_set.json`):
- **(a) Correct:** 8 (pending manual review of the grounded answers, but assuming grounded = correct based on context).
- **(b) Grounded:** 8/15 (in-scope questions successfully grounded).
- **(c) Appropriate refusals:** 4/4 (for out-of-scope questions).

**Which bothered me most:**
The grounded score (8/15) bothered me the most. It means nearly half (47%) of the in-scope questions failed to produce an answer. Looking at the failure logs, the LLM correctly refused to answer because the BM25 retriever failed to fetch the correct context chunks (due to vocabulary mismatch), starving the LLM of the information it needed.

### B2. If you ran the chunk-size experiment (Stretch)
*I did not formally run this experiment.* My focus was directed toward stabilizing the production pipeline and orchestrating the system cleanly.

### B3. If you compared model families (Stretch)
*I did not run this experiment.* I exclusively utilized the `llama-3.1-8b-instant` model via the Groq API for rapid inference.

---

## Part C — Debugging moments

### C1. The most frustrating bug
**The Bug:** During earlier iterations of the pipeline, my FAISS index only contained a single vector, despite having processed multiple paragraphs of text.
**Time to fix:** ~15 minutes.
**What I tried first:** I initially thought the FAISS `index.add()` method was mistakenly overwriting the index rather than appending to it, so I spent time digging into the FAISS documentation for a non-existent `append` method.
**The actual fix:** The bug was in my data preprocessing stage (`preprocess.py`). The script was writing the entire extracted text as a single massive continuous string into `preprocess.txt`, causing the embedding model to encode the entire textbook chapter as one single dense vector. The fix was updating the chunker to properly write out individual chunks iteratively.
**Fastest way to find it next time:** Open the intermediate artifact files (`preprocess.txt` or `chunks.json`) and verify their line counts/lengths *before* assuming the complex machine learning library is broken.

### C2. What still bothers you
Even though the pipeline works, **the pure BM25 lexical retrieval approach severely limits the system**. It fundamentally bothers me that a query like "State Newton's second law" retrieves context for "Newton's first law". To fix this, I would need to re-introduce dense vector embeddings (which were removed earlier to simplify the pipeline) and implement a Hybrid Search algorithm (BM25 + FAISS Dense Retrieval) to capture both semantic meaning and exact keyword matches.

---

## Part D — Architecture and reasoning

### D1. Why not just ChatGPT?
If you just use ChatGPT, the model will answer questions based on its vast, unfiltered pre-training data rather than the specific constraints of the curriculum. For example, in my evaluation set, Question 18 asks: *"Explain how a nuclear reactor generates electricity."* ChatGPT would confidently provide a detailed, accurate answer. However, nuclear reactors are not covered in the Class 9 NCERT chapters provided. My retrieval system strictly responds: *"I cannot answer this question from the provided chapter content."* In an educational setting, preventing out-of-syllabus hallucinations is critical to keep students focused entirely on their current curriculum. 

### D2. The GANs reflection
GANs (Generative Adversarial Networks) are designed for unconditional or loosely-conditioned synthesis—they invent novel, statistically plausible outputs (like generating realistic faces). For a textbook assistant, we absolutely do not want the model to be "creative" or invent plausible-sounding physics facts. We want strict, deterministic extraction and summarization of grounded truth. 
**The deeper principle:** You must match the architecture to the risk profile of the problem. When factual reliability is the primary goal, use architectures that constrain the model (like RAG), not ones designed to hallucinate creatively (like GANs).

### D3. Honest pilot readiness
**Honest answer:** No, we cannot launch this to 100 students next Monday.
While the system's ability to refuse out-of-scope questions is perfect (4/4), its recall on legitimate textbook questions is only 53% (8/15). Students would find it incredibly frustrating if the assistant "doesn't know" half of the syllabus.
**Three things I would fix/verify first:**
1. Upgrade the retriever from pure BM25 to a Hybrid Retriever (BM25 + Dense Embeddings) to fix the semantic mismatch failures.
2. Manually verify the absolute correctness and pedagogical tone of the 8 grounded answers to ensure they are helpful to a 9th grader.
3. Optimize the chunking strategy (e.g., using semantic chunk boundaries instead of blind 5-sentence windows) to ensure concepts aren't fragmented.

---

## Part E — Effort and self-assessment

### E1. Effort rating
**Rating:** 8/10.
I am genuinely proud of building `pipeline.py`, the master orchestrator. I didn't just leave a mess of Jupyter notebooks; I structured the project into a proper software engineering pipeline where `config.py` acts as a single source of truth, and a user can run the entire extraction, chunking, retrieval, and evaluation pipeline with a single CLI command.

### E2. The gap between you and a stronger student
A stronger student would likely have implemented **Reciprocal Rank Fusion (RRF)** to combine a Dense Retriever and a Sparse Retriever. I did not do this primarily due to time constraints; I wanted to ensure the baseline pipeline and automated evaluation framework were rock-solid and reproducible before introducing the complexity of maintaining two separate indices.

### E3. What would change with two more days
1. **First thing:** I would immediately swap the BM25 retriever out for a local HuggingFace embedding model (`all-MiniLM-L6-v2`) combined with FAISS. This addresses the system's biggest weakness (lexical mismatch).
2. **Last thing:** I would build a lightweight Streamlit web interface over the `rag.py` module so that non-technical users could actually test the assistant without needing to use the command line.
