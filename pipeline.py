"""
pipeline.py — Master orchestrator.

Runs the complete RAG pipeline end-to-end in the correct order:
  Stage 1  extraction.py        PDF → pdf_text.txt
  Stage 2  preprocess.py        txt → chunks.json + preprocess.txt
  Stage 3  retriever.py         smoke-test BM25 retriever
  Stage 4  evaluation/run_eval.py  full evaluation suite

Usage:
  python pipeline.py                # run all stages
  python pipeline.py --skip-eval    # skip evaluation (faster dev loop)
  python pipeline.py --from stage2  # resume from a specific stage
  
"""
import argparse
import sys
import time

STAGES = ["stage1", "stage2", "stage3", "stage4"]


def _header(title: str):
    bar = "─" * 60
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def run_stage1():
    _header("Stage 1 — PDF Extraction")
    from extraction import extract_pdfs
    extract_pdfs()


def run_stage2():
    _header("Stage 2 — Chunking & Preprocessing")
    from preprocess import preprocess
    preprocess()


def run_stage3():
    _header("Stage 3 — Retriever Smoke-Test")
    from retriever import load_retriever
    retriever = load_retriever()
    test_queries = [
        "What is the definition of uniform motion?",
        "State Newton's second law of motion.",
        "How does gravitational force depend on mass?",
    ]
    for q in test_queries:
        print(f"\n  Query: {q}")
        for r in retriever.retrieve(q, k=3):
            print(f"    [score={r.get('similarity_score', 0):.4f}] [{r['section']}] {r['text'][:90]}…")


def run_stage4():
    _header("Stage 4 — Evaluation Suite")
    from evaluation.run_eval import run_evaluation
    run_evaluation()


STAGE_FNS = {
    "stage1": run_stage1,
    "stage2": run_stage2,
    "stage3": run_stage3,
    "stage4": run_stage4,
}


def main():
    parser = argparse.ArgumentParser(description="NCERT RAG Pipeline")
    parser.add_argument(
        "--from",
        dest="start_stage",
        choices=STAGES,
        default="stage1",
        help="Resume from a specific stage (default: stage1)",
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="Skip Stage 4 (evaluation)",
    )
    args = parser.parse_args()

    start_idx = STAGES.index(args.start_stage)
    stages_to_run = STAGES[start_idx:]
    if args.skip_eval and "stage4" in stages_to_run:
        stages_to_run.remove("stage4")

    t0 = time.time()
    for stage in stages_to_run:
        try:
            STAGE_FNS[stage]()
        except FileNotFoundError as exc:
            print(f"\n  ✗ {exc}")
            sys.exit(1)
        except Exception as exc:
            print(f"\n  ✗ Unexpected error in {stage}: {exc}")
            raise

    elapsed = time.time() - t0
    print(f"\n{'─'*60}")
    print(f"  ✓ Pipeline complete  ({elapsed:.1f}s)")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
