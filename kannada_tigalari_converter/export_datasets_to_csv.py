#!/usr/bin/env python3
"""
Exports all Tulu language datasets, historical lexicons, AATA catalog,
and NMT parallel corpora to standardized CSV files in `datasets/`.
"""

import os
import sys
import csv
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.words_dataset_1000 import WORDS_DATASET_1000
from kannada_tigalari_converter.words_dataset_250 import WORDS_DATASET_250
from kannada_tigalari_converter.historical_dictionary import HISTORICAL_TULU_CORPUS
from kannada_tigalari_converter.aatana_library_collector import get_catalog, process_book_to_corpus
from kannada_tigalari_converter.tulu_nmt_pipeline import load_nmt_benchmark_corpus


def export_all_csvs(output_dir: str = None) -> dict:
    if output_dir is None:
        output_dir = os.path.join(PARENT_DIR, "datasets")
    os.makedirs(output_dir, exist_ok=True)

    exported_files = {}

    # 1. Tulu 1,000 Words Lexicon Dataset
    csv_1000 = os.path.join(output_dir, "tulu_lexicon_1000.csv")
    with open(csv_1000, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "category", "english_meaning", "tulu_kannada", "tulu_tigalari", "tulu_latin_phonetic"])
        for idx, row in enumerate(WORDS_DATASET_1000, 1):
            writer.writerow([
                idx,
                row.get("category", ""),
                row.get("english_meaning", row.get("english", "")),
                row.get("kannada", row.get("tulu_kannada", "")),
                row.get("expected_tigalari", row.get("tulu_tigalari", "")),
                row.get("latin_phonetic", row.get("tulu_latin", ""))
            ])
    exported_files["tulu_lexicon_1000.csv"] = len(WORDS_DATASET_1000)

    # 2. Tulu 250 Words Lexicon Dataset
    csv_250 = os.path.join(output_dir, "tulu_lexicon_250.csv")
    with open(csv_250, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "category", "english_meaning", "tulu_kannada", "tulu_tigalari", "tulu_latin_phonetic"])
        for idx, row in enumerate(WORDS_DATASET_250, 1):
            writer.writerow([
                idx,
                row.get("category", ""),
                row.get("english_meaning", row.get("english", "")),
                row.get("kannada", row.get("tulu_kannada", "")),
                row.get("expected_tigalari", row.get("tulu_tigalari", "")),
                row.get("latin_phonetic", row.get("tulu_latin", ""))
            ])
    exported_files["tulu_lexicon_250.csv"] = len(WORDS_DATASET_250)

    # 3. 1886 Basel Mission Historical Tulu Dictionary (Rev. August Männer)
    csv_hist = os.path.join(output_dir, "tulu_historical_dictionary_1886.csv")
    with open(csv_hist, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "tulu_kannada", "tulu_tigalari", "tulu_latin", "english_definition", "part_of_speech", "domain", "source"])
        for row in HISTORICAL_TULU_CORPUS:
            writer.writerow([
                row.get("id", ""),
                row.get("tulu_kannada", ""),
                row.get("tulu_tigalari", ""),
                row.get("tulu_latin", ""),
                row.get("english", ""),
                row.get("part_of_speech", ""),
                row.get("domain", ""),
                row.get("source", "")
            ])
    exported_files["tulu_historical_dictionary_1886.csv"] = len(HISTORICAL_TULU_CORPUS)

    # 4. AATA Digital Book Library Catalog (210 Books)
    csv_books = os.path.join(output_dir, "aatana_books_catalog.csv")
    catalog = get_catalog()
    with open(csv_books, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "pdf_path", "pdf_url"])
        for row in catalog:
            writer.writerow([
                row.get("id", ""),
                row.get("title", ""),
                row.get("pdf_path", ""),
                row.get("pdf_url", "")
            ])
    exported_files["aatana_books_catalog.csv"] = len(catalog)

    # 5. Tulu-NMT FLORES-200 Parallel Benchmark Corpus
    csv_nmt = os.path.join(output_dir, "tulu_nmt_parallel_corpus.csv")
    nmt_corpus = load_nmt_benchmark_corpus()
    with open(csv_nmt, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "eng_Latn", "kan_Knda", "tcy_Knda", "tcy_Tglr", "tcy_Phonetic"])
        for row in nmt_corpus.data:
            writer.writerow([
                row.get("id", ""),
                row.get("eng_Latn", ""),
                row.get("kan_Knda", ""),
                row.get("tcy_Knda", ""),
                row.get("tcy_Tglr", ""),
                row.get("tcy_Phonetic", "")
            ])
    exported_files["tulu_nmt_parallel_corpus.csv"] = len(nmt_corpus.data)

    # 6. Sample OCR Extracted Corpus (Sodara Habba)
    csv_ocr = os.path.join(output_dir, "aatana_ocr_sodara_habba.csv")
    try:
        ocr_res = process_book_to_corpus(1, page_numbers=[3, 4])
        with open(csv_ocr, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "source_book", "kannada", "tigalari", "phonetic", "word_count", "char_count"])
            for row in ocr_res.get("sentences", []):
                writer.writerow([
                    row.get("id", ""),
                    "Sodara Habba (K.L. Kundanthaya)",
                    row.get("kannada", ""),
                    row.get("tigalari", ""),
                    row.get("phonetic", ""),
                    row.get("word_count", ""),
                    row.get("char_count", "")
                ])
        exported_files["aatana_ocr_sodara_habba.csv"] = len(ocr_res.get("sentences", []))
    except Exception as e:
        print(f"Warning: OCR export skipped ({e})")

    return exported_files


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else None
    results = export_all_csvs(out_dir)
    print("=" * 60)
    print("  Tulu Datasets CSV Export Completed")
    print("=" * 60)
    for fname, count in results.items():
        print(f"  ✓ {fname:<36} : {count:>5} records")
    print(f"\nAll files saved in: {os.path.join(PARENT_DIR, 'datasets')}")
