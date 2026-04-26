"""
preprocess.py — Stage 1b: Chunk extracted text into annotated segments.

Reads : data/processed/pdf_text.txt
Writes: data/processed/chunks.json   (rich metadata)
        data/processed/preprocess.txt (flat text, one chunk per line)
"""
import re
import json
import nltk
import os
from config import (
    PDF_TEXT_FILE, CHUNKS_JSON_FILE, PREPROCESS_FILE,
    CHUNK_WINDOW, CHUNK_OVERLAP, MIN_CHUNK_WORDS
)

nltk.download("punkt",      quiet=True)
nltk.download("punkt_tab",  quiet=True)


# ── Content-type classifier ────────────────────────────────────────────────────

def classify_paragraph(text: str) -> str:
    """Heuristic: assign one of three content types to a text block."""
    t = text.strip()
    if re.search(r"\bExample\b|\bSolution\b|=\s*\d", t, re.IGNORECASE):
        return "worked_example"
    if re.match(r"^\d+[\.\)]", t) and "?" in t:
        return "exercise_question"
    return "concept_paragraph"


def _infer_section(sentence: str) -> str:
    """Rough section label from first sentence vocabulary."""
    s = sentence.lower()
    if re.search(r"velocity|speed|distance|displacement|uniform motion", s):
        return "Motion & Speed"
    if re.search(r"force|newton|inertia|momentum|action|reaction", s):
        return "Force & Laws of Motion"
    if re.search(r"gravit|weight|free.fall|g =", s):
        return "Gravitation"
    if re.search(r"example|solution", s):
        return "Worked Example"
    return "General"


# ── Sliding-window chunker ─────────────────────────────────────────────────────

def build_chunks(
    text: str,
    chapter: str = "NCERT Class 9 Science",
    window: int  = CHUNK_WINDOW,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split text into overlapping sentence-window chunks, each annotated with:
      chunk_id, chapter, section, content_type, num_sentences, text
    """
    # Normalise whitespace
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = [s.strip() for s in nltk.tokenize.sent_tokenize(clean)
                 if len(s.split()) > 3]

    chunks: list[dict] = []
    i = 0
    while i < len(sentences):
        window_sents = sentences[i : i + window]
        chunk_text   = " ".join(window_sents)

        if len(chunk_text.split()) < MIN_CHUNK_WORDS and chunks:
            # Merge tiny tail into previous chunk
            chunks[-1]["text"] += " " + chunk_text
            chunks[-1]["num_sentences"] += len(window_sents)
        else:
            chunks.append({
                "chunk_id"     : len(chunks),
                "chapter"      : chapter,
                "section"      : _infer_section(window_sents[0] if window_sents else ""),
                "content_type" : classify_paragraph(chunk_text),
                "num_sentences": len(window_sents),
                "text"         : chunk_text,
            })

        i += (window - overlap)

    return chunks


# ── Main ──────────────────────────────────────────────────────────────────────

def preprocess(
    input_file : str = PDF_TEXT_FILE,
    chunks_file: str = CHUNKS_JSON_FILE,
    flat_file  : str = PREPROCESS_FILE,
) -> list[dict]:
    """
    Full preprocessing pipeline — reads extracted text, produces annotated
    chunks and saves both JSON and flat-text formats.

    Returns the list of chunk dicts.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"Input file not found: '{input_file}'\n"
            "Run extraction.py first."
        )

    with open(input_file, "r", encoding="utf-8") as fh:
        raw_text = fh.read()

    chunks = build_chunks(raw_text)

    # Save rich JSON
    os.makedirs(os.path.dirname(chunks_file), exist_ok=True)
    with open(chunks_file, "w", encoding="utf-8") as fh:
        json.dump(chunks, fh, indent=2, ensure_ascii=False)

    # Save flat text (one chunk per line) — used by embeddings_conversion.py
    with open(flat_file, "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(c["text"] + "\n")

    from collections import Counter
    types = Counter(c["content_type"] for c in chunks)
    print(f"  [preprocess] {len(chunks)} chunks created")
    print(f"  [preprocess] Content types: {dict(types)}")
    print(f"  [preprocess] Saved → {chunks_file}")
    print(f"  [preprocess] Saved → {flat_file}")
    return chunks


if __name__ == "__main__":
    preprocess()