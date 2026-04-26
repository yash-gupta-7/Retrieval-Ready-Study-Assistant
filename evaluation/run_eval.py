"""
evaluation/run_eval.py — Stage 5: Run the full evaluation suite.

Reads : evaluation/eval_set.json
Calls : rag.answer() for every question
Scores: correctness | grounding | refusal_appropriate
Writes: evaluation/results/evaluation_results.csv
        evaluation/results/evaluation_results.md
"""
import sys
import os
import csv
import json
import time

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag import answer
from retriever import load_retriever
from config import (
    EVAL_SET_FILE, EVAL_RESULTS_CSV, EVAL_RESULTS_MD,
    EVAL_RESULTS_DIR, TOP_K
)

REFUSAL_PHRASE = "I cannot answer this question from the provided chapter content"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _score_refusal(ans: str) -> str:
    return "yes" if REFUSAL_PHRASE.lower() in ans.lower() else "no"


def _prompt_scores(qid: int, question: str, ans: str, rtype: str) -> dict:
    """
    Auto-score what we can; leave correctness as 'TBD' for human review.
    Grounding is set to 'yes' conservatively; swap to 'no' manually if needed.
    """
    refusal = _score_refusal(ans)
    if rtype == "out_of_scope":
        return {
            "correctness"         : "N/A",
            "grounding"           : "N/A",
            "refusal_appropriate" : refusal,
        }
    return {
        "correctness"         : "TBD",   # Requires human review
        "grounding"           : "yes" if REFUSAL_PHRASE.lower() not in ans.lower() else "no",
        "refusal_appropriate" : "N/A",
    }


# ── CSV writer ─────────────────────────────────────────────────────────────────

FIELDS = [
    "id", "type", "question", "answer",
    "retrieved_section_1", "retrieved_score_1", "retrieved_text_1",
    "retrieved_section_2", "retrieved_score_2", "retrieved_text_2",
    "retrieved_section_3", "retrieved_score_3", "retrieved_text_3",
    "correctness", "grounding", "refusal_appropriate",
]

def _flatten(result: dict, meta: dict) -> dict:
    row = {
        "id"      : meta["id"],
        "type"    : meta["type"],
        "question": meta["question"],
        "answer"  : result["answer"],
    }
    for i, chunk in enumerate(result["retrieved_chunks"][:3], start=1):
        row[f"retrieved_section_{i}"] = chunk.get("section", "")
        row[f"retrieved_score_{i}"]   = chunk.get("bm25_score", "")
        row[f"retrieved_text_{i}"]    = chunk.get("text", "")[:300]
    # Pad missing chunk columns
    for i in range(len(result["retrieved_chunks"]) + 1, 4):
        row[f"retrieved_section_{i}"] = ""
        row[f"retrieved_score_{i}"]   = ""
        row[f"retrieved_text_{i}"]    = ""
    scores = _prompt_scores(meta["id"], meta["question"], result["answer"], meta["type"])
    row.update(scores)
    return row


# ── Markdown report builder ────────────────────────────────────────────────────

def _build_markdown(rows: list[dict]) -> str:
    in_scope  = [r for r in rows if r["type"] != "out_of_scope"]
    out_scope = [r for r in rows if r["type"] == "out_of_scope"]

    refused_correctly = sum(1 for r in out_scope if r["refusal_appropriate"] == "yes")
    grounded_yes      = sum(1 for r in in_scope  if r["grounding"] == "yes")

    lines = [
        "# Evaluation Results — NCERT RAG Pipeline",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total questions | {len(rows)} |",
        f"| In-scope questions | {len(in_scope)} |",
        f"| Grounded answers (in-scope) | {grounded_yes}/{len(in_scope)} |",
        f"| Grounded answers percentage (in-scope) | {round((grounded_yes/len(in_scope))*100)}|",
        f"| Out-of-scope questions | {len(out_scope)} |",
        f"| Correct refusals | {refused_correctly}/{len(out_scope)} |",
        "",
        "---",
        "",
        "## Per-Question Results",
        "",
        "| ID | Type | Question | Correctness | Grounding | Refusal | Answer (excerpt) |",
        "|----|------|----------|-------------|-----------|---------|-----------------|",
    ]

    for r in rows:
        ans_short = r["answer"][:100].replace("\n", " ") + ("…" if len(r["answer"]) > 100 else "")
        lines.append(
            f"| {r['id']} | {r['type']} | {r['question'][:60]} "
            f"| {r['correctness']} | {r['grounding']} | {r['refusal_appropriate']} "
            f"| {ans_short} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Analysis",
        "",
        "### Working Examples",
        "",
        "*(Fill in after reviewing results — pick 3 questions where retrieval + answer were correct)*",
        "",
        "### Failing Examples",
        "",
        "*(Fill in after reviewing results — pick 2 failures and give one-sentence diagnosis)*",
        "",
        "> **Failure template:** Q{id} — *Probable cause: lexical retriever missed relevant chunk "
        "due to vocabulary mismatch between query and chunk text.*",
    ]

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def run_evaluation(eval_file: str = EVAL_SET_FILE) -> list[dict]:
    """Run all evaluation questions through the RAG pipeline and save results."""

    with open(eval_file, "r", encoding="utf-8") as fh:
        eval_set = json.load(fh)

    print(f"\n[eval] Running {len(eval_set)} questions…\n")

    # Build retriever once — reuse across all questions
    retriever = load_retriever()

    rows = []
    for item in eval_set:
        tag = f"Q{item['id']:02d} [{item['type']}]"
        print(f"  {tag}: {item['question'][:65]}")
        try:
            result = answer(item["question"], retriever=retriever, k=TOP_K)
        except EnvironmentError as e:
            print(f"  !! {e}")
            result = {
                "answer"           : f"ERROR: {e}",
                "retrieved_chunks" : [],
            }
        row = _flatten(result, item)
        rows.append(row)
        time.sleep(0.4)   # polite rate-limit

    # Save CSV
    os.makedirs(EVAL_RESULTS_DIR, exist_ok=True)
    with open(EVAL_RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[eval] CSV saved  → {EVAL_RESULTS_CSV}")

    # Save Markdown
    with open(EVAL_RESULTS_MD, "w", encoding="utf-8") as fh:
        fh.write(_build_markdown(rows))
    print(f"[eval] MD  saved  → {EVAL_RESULTS_MD}")

    # Quick summary
    out = [r for r in rows if r["type"] == "out_of_scope"]
    refused = sum(1 for r in out if r["refusal_appropriate"] == "yes")
    print(f"\n── Quick Summary ─────────────────────────────────")
    print(f"  Out-of-scope correctly refused: {refused}/{len(out)}")
    print(f"  (Correctness requires manual review — see {EVAL_RESULTS_CSV})")
    return rows


if __name__ == "__main__":
    run_evaluation()
