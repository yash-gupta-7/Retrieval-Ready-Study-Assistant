# NCERT RAG — Retrieval-Augmented Generation Pipeline

A production-grade five-stage RAG system for NCERT Class 9 Science (Motion, Force & Laws of Motion, Gravitation).

---

## Project Structure

```
NCERT RAG Project/
├── config.py                   # Centralised paths & settings (import this, never hardcode paths)
│
├── extraction.py               # Stage 1a — PDF → pdf_text.txt
├── preprocess.py               # Stage 1b — txt → chunks.json + preprocess.txt
├── embeddings_conversion.py    # Stage 2  — chunks → embeddings.npy
├── create_index.py             # Stage 3  — embeddings → ncert.index  (FAISS)
├── retriever.py                # Stage 4  — BM25 lexical retriever
├── rag.py                      # Stage 4  — answer() — LLM grounded generation
├── pipeline.py                 # Master orchestrator — runs all stages
│
├── evaluation/
│   ├── eval_set.json           # 19-question evaluation set
│   ├── run_eval.py             # Evaluation runner → CSV + Markdown report
│   ├── tokenizer_comparison.py # GPT-2 vs BERT vs T5 token-count analysis
│   └── results/                # Auto-generated outputs (gitignored)
│       ├── evaluation_results.csv
│       ├── evaluation_results.md
│       └── tokenizer_comparison.txt
│
├── data/
│   ├── raw/                    # Place your PDF(s) here
│   └── processed/              # Auto-generated intermediate files
│       ├── pdf_text.txt
│       ├── chunks.json
│       ├── preprocess.txt
│       └── sentences.txt
│
├── embeddings.npy              # Auto-generated
├── ncert.index                 # Auto-generated
└── requirements.txt
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv .env
source .env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set OpenAI API key (required for Stage 6 — generation & evaluation)
export OPENAI_API_KEY=sk-...
```

---

## Usage

### Run the full pipeline

```bash
python pipeline.py
```

### Resume from a specific stage

```bash
python pipeline.py --from stage3   # skip extraction & preprocessing
```

### Skip evaluation (faster dev loop)

```bash
python pipeline.py --skip-eval
```

### Run individual scripts

```bash
python extraction.py              # Stage 1a
python preprocess.py              # Stage 1b
python embeddings_conversion.py   # Stage 2
python create_index.py            # Stage 3
python retriever.py               # Stage 4 — BM25 smoke-test
python rag.py                     # Stage 4 — single Q&A smoke-test
python evaluation/run_eval.py     # Stage 5 — full evaluation
python evaluation/tokenizer_comparison.py  # Supplementary analysis
```

---

## Pipeline Stages

| Stage | Script | Input | Output |
|-------|--------|-------|--------|
| 1a | `extraction.py` | `data/raw/*.pdf` | `data/processed/pdf_text.txt` |
| 1b | `preprocess.py` | `pdf_text.txt` | `chunks.json`, `preprocess.txt` |
| 2 | `embeddings_conversion.py` | `preprocess.txt` | `embeddings.npy`, `sentences.txt` |
| 3 | `create_index.py` | `embeddings.npy` | `ncert.index` |
| 4 | `retriever.py` + `rag.py` | `chunks.json` | Live BM25 + LLM answers |
| 5 | `evaluation/run_eval.py` | `eval_set.json` | `evaluation_results.csv/.md` |

---

## Chunking Strategy

**Sliding-window sentence chunking** — 5 sentences per chunk, 2-sentence (40 %) overlap.

- A sentence in this science text averages ~20 tokens → each chunk ≈ 100 tokens.
- 40 % overlap ensures concepts straddling chunk boundaries are always captured together.
- Boundaries are sentence-level (NLTK punkt), so no concept is split mid-sentence.
- Tail chunks shorter than `MIN_CHUNK_WORDS` are merged into the preceding chunk.

---

## Evaluation

19 questions across three categories:

| Category | Count | Purpose |
|----------|-------|---------|
| Textbook | 12 | Directly from end-of-chapter exercises |
| Paraphrase | 3 | Same answer, different wording |
| Out-of-scope | 4 | System must refuse cleanly |

Scored on three axes: **Correctness** · **Grounding** · **Refusal-appropriateness**

Results saved to `evaluation/results/evaluation_results.csv` and `.md`.

---

## Configuration

All paths and model settings are in `config.py`. Change values there — no other file needs editing.

| Setting | Default | Description |
|---------|---------|-------------|
| `CHUNK_WINDOW` | 5 | Sentences per chunk |
| `CHUNK_OVERLAP` | 2 | Overlap between chunks |
| `TOP_K` | 3 | Chunks retrieved per query |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model for generation |
