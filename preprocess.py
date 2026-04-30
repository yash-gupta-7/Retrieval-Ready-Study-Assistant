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
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    PDF_TEXT_FILE, CHUNKS_JSON_FILE, PREPROCESS_FILE,
    LANGCHAIN_CHUNK_SIZE, LANGCHAIN_CHUNK_OVERLAP, MIN_CHUNK_WORDS
)

def _ensure_nltk_resource(resource_path: str, download_name: str) -> None:
    try:
        nltk.data.find(resource_path)
    except LookupError:
        if not nltk.download(download_name, quiet=True):
            raise RuntimeError(
                f"Missing NLTK resource '{download_name}'. "
                "Install it manually with nltk.download()."
            )


_ensure_nltk_resource("tokenizers/punkt", "punkt")
_ensure_nltk_resource("tokenizers/punkt_tab", "punkt_tab")


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


# ── LangChain chunker ──────────────────────────────────────────────────────────

def build_chunks(
    text: str,
    chapter: str = "NCERT Class 9 Science",
    chunk_size: int = LANGCHAIN_CHUNK_SIZE,
    chunk_overlap: int = LANGCHAIN_CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split text into overlapping LangChain chunks, each annotated with:
      chunk_id, chapter, section, content_type, num_sentences, text
    """
    clean = re.sub(r"\s+", " ", text).strip()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        length_function=len,
    )
    raw_chunks = splitter.split_text(clean)

    chunks: list[dict] = []
    for raw_chunk in raw_chunks:
        chunk_text = re.sub(r"\s+", " ", raw_chunk).strip()
        if not chunk_text:
            continue

        sentences = [
            s.strip() for s in nltk.tokenize.sent_tokenize(chunk_text)
            if len(s.split()) > 3
        ]
        sentence_count = max(len(sentences), 1)

        if len(chunk_text.split()) < MIN_CHUNK_WORDS and chunks:
            chunks[-1]["text"] += " " + chunk_text
            chunks[-1]["num_sentences"] += sentence_count
        else:
            chunks.append({
                "chunk_id"     : len(chunks),
                "chapter"      : chapter,
                "section"      : _infer_section(sentences[0] if sentences else chunk_text),
                "content_type" : classify_paragraph(chunk_text),
                "num_sentences": sentence_count,
                "text"         : chunk_text,
            })

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

    loader = TextLoader(input_file, encoding="utf-8")
    documents = loader.load()
    raw_text = "\n".join(doc.page_content for doc in documents)

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