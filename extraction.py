"""
extraction.py — Stage 1a: Extract raw text from all PDFs in data/raw/.

Writes: data/processed/pdf_text.txt
"""
import pymupdf
import glob
import os
from config import RAW_DIR, PDF_TEXT_FILE


def extract_pdfs(input_folder: str = RAW_DIR, output_file: str = PDF_TEXT_FILE) -> str:
    """
    Iterate over every PDF in input_folder, concatenate page text, and write
    the combined result to output_file.

    Returns the output file path.
    """
    pdf_files = sorted(glob.glob(os.path.join(input_folder, "*.pdf")))

    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in '{input_folder}'")

    all_text = ""
    for pdf_path in pdf_files:
        print(f"  [extraction] Reading: {os.path.basename(pdf_path)}")
        try:
            doc = pymupdf.open(pdf_path)
            for page in doc:
                all_text += page.get_text() + "\n"
        except Exception as exc:
            print(f"  [extraction] WARNING — skipping {pdf_path}: {exc}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(all_text)

    print(f"  [extraction] Extracted {len(pdf_files)} PDF(s) → {output_file}")
    return output_file


if __name__ == "__main__":
    extract_pdfs()