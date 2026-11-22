#!/usr/bin/env python3
"""
Batch Romanization Tool for Tulu and Kannada Text Assets.
=========================================================
Converts existing native-script text corpora into canonical ASCII romanized datasets.
These romanized files become the primary training and inference representations.
Native script is retained only as raw source material for offline inspection or
cosmetic post-processing.
"""

import os
import sys
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.lexicon.romanization_scheme import to_canonical_roman

DATASETS_DIR = os.path.join(BASE_DIR, "datasets")


def romanize_master_corpus():
    src = os.path.join(DATASETS_DIR, "tulu_master_consolidated_corpus.csv")
    dst = os.path.join(DATASETS_DIR, "tulu_master_corpus_romanized.csv")
    if not os.path.exists(src):
        print(f"Skipping master corpus: {src} not found")
        return

    print(f"Romanizing master corpus: {src} -> {dst}")
    with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = [
            "id", "corpus_source", "category_or_domain",
            "tulu_romanized", "kannada_romanized", "english_translation",
            "tulu_kannada_raw"
        ]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            raw_kn = row.get("tulu_kannada", "")
            tulu_rom = to_canonical_roman(raw_kn)
            # In master corpus, tulu_kannada is Tulu in Kannada script;
            # generate standard romanized version
            writer.writerow({
                "id": row.get("id", count + 1),
                "corpus_source": row.get("corpus_source", ""),
                "category_or_domain": row.get("category_or_domain", ""),
                "tulu_romanized": tulu_rom,
                "kannada_romanized": tulu_rom,
                "english_translation": row.get("english_translation", row.get("english_meaning", "")),
                "tulu_kannada_raw": raw_kn
            })
            count += 1
    print(f"Successfully romanized {count} rows in {dst}")


def romanize_lexicon_1000():
    src = os.path.join(DATASETS_DIR, "tulu_lexicon_1000.csv")
    dst = os.path.join(DATASETS_DIR, "tulu_lexicon_1000_romanized.csv")
    if not os.path.exists(src):
        print(f"Skipping lexicon 1000: {src} not found")
        return

    print(f"Romanizing lexicon 1000: {src} -> {dst}")
    with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = ["id", "category", "english_meaning", "tulu_romanized", "tulu_kannada_raw"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            raw_kn = row.get("tulu_kannada", "")
            tulu_rom = to_canonical_roman(raw_kn)
            writer.writerow({
                "id": row.get("id", count + 1),
                "category": row.get("category", ""),
                "english_meaning": row.get("english_meaning", ""),
                "tulu_romanized": tulu_rom,
                "tulu_kannada_raw": raw_kn
            })
            count += 1
    print(f"Successfully romanized {count} rows in {dst}")


def romanize_lexicon_250():
    src = os.path.join(DATASETS_DIR, "tulu_lexicon_250.csv")
    dst = os.path.join(DATASETS_DIR, "tulu_lexicon_250_romanized.csv")
    if not os.path.exists(src):
        print(f"Skipping lexicon 250: {src} not found")
        return

    print(f"Romanizing lexicon 250: {src} -> {dst}")
    with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = ["id", "category", "english_meaning", "tulu_romanized", "tulu_kannada_raw"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for row in reader:
            raw_kn = row.get("tulu_kannada", "")
            tulu_rom = to_canonical_roman(raw_kn)
            writer.writerow({
                "id": row.get("id", count + 1),
                "category": row.get("category", ""),
                "english_meaning": row.get("english_meaning", ""),
                "tulu_romanized": tulu_rom,
                "tulu_kannada_raw": raw_kn
            })
            count += 1
    print(f"Successfully romanized {count} rows in {dst}")


def main():
    print("=" * 60)
    print("  Starting One-Time Batch Romanization of Text Assets")
    print("=" * 60)
    romanize_master_corpus()
    romanize_lexicon_1000()
    romanize_lexicon_250()
    print("=" * 60)
    print("  Batch Romanization Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
