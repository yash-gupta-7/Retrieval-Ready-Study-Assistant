"""
config.py — Centralised project paths and settings.
All other scripts import from here so paths never need to be hardcoded elsewhere.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Root ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Data directories ──────────────────────────────────────────────────────────
DATA_DIR      = os.path.join(BASE_DIR, "data")
RAW_DIR       = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

# ── File paths (processed) ────────────────────────────────────────────────────
PDF_TEXT_FILE    = os.path.join(PROCESSED_DIR, "pdf_text.txt")
CHUNKS_JSON_FILE = os.path.join(PROCESSED_DIR, "chunks.json")
PREPROCESS_FILE  = os.path.join(PROCESSED_DIR, "preprocess.txt")   # flat text, one chunk/line
SENTENCES_FILE   = os.path.join(PROCESSED_DIR, "sentences.txt")    # alias kept for compatibility

# ── Evaluation ────────────────────────────────────────────────────────────────
EVAL_DIR         = os.path.join(BASE_DIR, "evaluation")
EVAL_SET_FILE    = os.path.join(EVAL_DIR, "eval_set.json")
EVAL_RESULTS_DIR = os.path.join(EVAL_DIR, "results")
EVAL_RESULTS_CSV = os.path.join(EVAL_RESULTS_DIR, "evaluation_results.csv")
EVAL_RESULTS_MD  = os.path.join(EVAL_RESULTS_DIR, "evaluation_results.md")

# ── Model settings ────────────────────────────────────────────────────────────
LLM_MODEL       = "llama-3.1-8b-instant"     # Groq model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # Local HuggingFace embeddings

# ── Chunking strategy ─────────────────────────────────────────────────────────
CHUNK_WINDOW = 5   # legacy sentence-window setting kept for compatibility
CHUNK_OVERLAP = 2  # legacy sentence overlap setting kept for compatibility
MIN_CHUNK_WORDS = 10

# LangChain chunking settings
LANGCHAIN_CHUNK_SIZE = 600      # characters per chunk
LANGCHAIN_CHUNK_OVERLAP = 150   # overlapping characters between chunks

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K = 3   # number of chunks returned per query

# ── Ensure required directories exist ────────────────────────────────────────
for _d in (RAW_DIR, PROCESSED_DIR, EVAL_DIR, EVAL_RESULTS_DIR):
    os.makedirs(_d, exist_ok=True)
