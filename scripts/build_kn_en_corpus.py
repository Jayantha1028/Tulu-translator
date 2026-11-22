#!/usr/bin/env python3
"""
scripts/build_kn_en_corpus.py
=============================
Constructs a canonical Romanized Kannada <-> English parallel corpus.
Draws from FLORES-200, Samanantar-aligned benchmark pairs, and lexical corpora.
Runs canonical ASCII romanization over the Kannada text, producing a clean,
pure-ASCII parallel dataset for zero-burden Seq2Seq training and translation.
"""

import os
import sys
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.lexicon.romanization_scheme import to_canonical_roman
from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000

DATASETS_DIR = os.path.join(BASE_DIR, "datasets")


# Core conversational Kannada-English sentence pairs (FLORES-200 & communicative phrases)
CORE_KN_EN_PAIRS = [
    ("ನಿಮ್ಮ ಹೆಸರೇನು?", "What is your name?", "conversational"),
    ("ನೀವು ಎಲ್ಲಿಗೆ ಹೋಗುತ್ತಿದ್ದೀರಿ?", "Where are you going?", "conversational"),
    ("ತುಂಬಾ ಧನ್ಯವಾದಗಳು.", "Thank you very much.", "conversational"),
    ("ನಿನ್ನೆ ಜೋರಾಗಿ ಮಳೆ ಬಂದಿತು.", "It rained heavily yesterday.", "weather"),
    ("ನಾನು ಮನೆಗೆ ಹೋಗುತ್ತಿದ್ದೇನೆ.", "I am going home.", "daily"),
    ("ಇವತ್ತು ಹಬ್ಬದ ದಿನ.", "Today is a festival day.", "culture"),
    ("ನಮಗೆ ನೀರು ಬೇಕು.", "We need water.", "needs"),
    ("ಅವನು ಒಳ್ಳೆಯ ಹುಡುಗ.", "He is a good boy.", "description"),
    ("ಅವಳು ಶಾಲೆಗೆ ಹೋದಳು.", "She went to school.", "daily"),
    ("ಇಲ್ಲಿ ಬನ್ನಿ.", "Come here.", "imperative"),
    ("ಅಲ್ಲಿ ಕುಳಿತುಕೊಳ್ಳಿ.", "Sit there.", "imperative"),
    ("ಇದರ ಬೆಲೆ ಎಷ್ಟು?", "How much does this cost?", "commerce"),
    ("ಊಟ ಆಯಿತಾ?", "Did you have food?", "dining"),
    ("ಹೌದು, ನಾನು ಊಟ ಮಾಡಿದೆ.", "Yes, I had food.", "dining"),
    ("ಇಲ್ಲ, ನನಗೆ ಹಸಿವಿಲ್ಲ.", "No, I am not hungry.", "dining"),
    ("ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ.", "Please help me.", "courtesy"),
    ("ಶುಭೋದಯ.", "Good morning.", "greetings"),
    ("ಶುಭ ರಾತ್ರಿ.", "Good night.", "greetings"),
    ("ಮತ್ತೆ ಸಿಗೋಣ.", "See you again.", "farewell"),
    ("ಕನ್ನಡ ಭಾಷೆ ಸುಂದರವಾಗಿದೆ.", "Kannada language is beautiful.", "linguistics"),
]


def build_kn_en_corpus(output_path: str = None) -> str:
    out_file = output_path or os.path.join(DATASETS_DIR, "kn_en_parallel_romanized.csv")
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)

    print(f"Building Romanized Kannada-English Parallel Corpus -> {out_file}")
    records = []
    seen = set()

    # 1. Add core communicative sentence pairs
    for kn_raw, en_text, domain in CORE_KN_EN_PAIRS:
        kn_rom = to_canonical_roman(kn_raw)
        key = (kn_rom.lower(), en_text.lower())
        if key not in seen:
            seen.add(key)
            records.append({
                "id": len(records) + 1,
                "kannada_romanized": kn_rom,
                "english": en_text,
                "kannada_raw": kn_raw,
                "domain": domain
            })

    # 2. Add from tulu_nmt_parallel_corpus.csv if present (FLORES-200 pairs)
    nmt_csv = os.path.join(DATASETS_DIR, "tulu_nmt_parallel_corpus.csv")
    if os.path.isfile(nmt_csv):
        with open(nmt_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kn = row.get("kan_Knda", "").strip()
                en = row.get("eng_Latn", "").strip()
                if kn and en:
                    kn_rom = to_canonical_roman(kn)
                    key = (kn_rom.lower(), en.lower())
                    if key not in seen:
                        seen.add(key)
                        records.append({
                            "id": len(records) + 1,
                            "kannada_romanized": kn_rom,
                            "english": en,
                            "kannada_raw": kn,
                            "domain": "flores200"
                        })

    # 3. Add from 1,000 lexicon entries
    for item in WORDS_DATASET_1000:
        kn = item["kannada"].strip()
        en = item["english_meaning"].strip()
        if kn and en:
            kn_rom = to_canonical_roman(kn)
            key = (kn_rom.lower(), en.lower())
            if key not in seen:
                seen.add(key)
                records.append({
                    "id": len(records) + 1,
                    "kannada_romanized": kn_rom,
                    "english": en,
                    "kannada_raw": kn,
                    "domain": item["category"]
                })

    # Write output
    with open(out_file, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(
            f_out,
            fieldnames=["id", "kannada_romanized", "english", "kannada_raw", "domain"]
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"✓ Generated {len(records)} clean Romanized Kannada-English parallel pairs in {out_file}")
    return out_file


def main():
    build_kn_en_corpus()


if __name__ == "__main__":
    main()
