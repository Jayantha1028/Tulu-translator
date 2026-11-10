"""
kannada_tigalari_converter.nlp.tulu_dataset_builder
===================================================
Lightweight, memory-efficient multi-task instruction dataset builder for LLM training.
Streams records line-by-line from the 75k master corpus with minimal RAM footprint (<25 MB).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, Iterator, List, Optional

# Ensure project paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (ROOT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)


class TuluDatasetBuilder:
    """Stream-based multi-task instruction dataset generator with constant O(1) memory usage."""

    TASK_TRANSLATION_EN_KN = "translate_en_to_kn"
    TASK_TRANSLATION_KN_EN = "translate_kn_to_en"
    TASK_TRANSLITERATE_KN_TIG = "transliterate_kn_to_tig"
    TASK_TRANSLITERATE_TIG_KN = "transliterate_tig_to_kn"
    TASK_GRAMMAR_CASE = "grammar_case_explain"

    def __init__(self, master_csv_path: Optional[str] = None):
        self.master_csv_path = master_csv_path or os.path.join(
            ROOT_DIR, "datasets", "tulu_master_consolidated_corpus.csv"
        )

    def stream_raw_records(self) -> Iterator[Dict[str, str]]:
        """Streams records one-by-one from the master CSV without loading the file into memory."""
        if not os.path.exists(self.master_csv_path):
            return

        with open(self.master_csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    def build_instruction_records(
        self,
        max_records: int = 5000,
        include_transliteration: bool = True,
        include_translation: bool = True,
        include_grammar: bool = True,
    ) -> Iterator[Dict[str, str]]:
        """Generates instruction-tuning JSON pairs on the fly."""
        generated = 0

        for row in self.stream_raw_records():
            if generated >= max_records:
                break

            kn = (row.get("tulu_kannada") or "").strip()
            tig = (row.get("tulu_tigalari") or "").strip()
            latin = (row.get("tulu_latin") or "").strip()
            en = (row.get("english_translation") or row.get("english_meaning") or "").strip()
            source = row.get("corpus_source") or row.get("source_type") or "General"
            domain = row.get("category_or_domain") or row.get("source_name") or ""

            if not kn:
                continue

            # Task 1: Translation (if English meaning is available)
            if include_translation and en:
                # Tulu -> English
                yield {
                    "task": self.TASK_TRANSLATION_KN_EN,
                    "instruction": "Translate the following Tulu sentence into accurate English.",
                    "input": kn,
                    "output": en,
                }
                generated += 1
                if generated >= max_records:
                    break

                # English -> Tulu
                yield {
                    "task": self.TASK_TRANSLATION_EN_KN,
                    "instruction": "Translate the following English phrase into authentic Tulu in Kannada script.",
                    "input": en,
                    "output": kn,
                }
                generated += 1
                if generated >= max_records:
                    break

            # Task 2: Transliteration (Kannada <-> Unicode 16.0 Tigalari)
            if include_transliteration and tig:
                # Kannada -> Tigalari
                yield {
                    "task": self.TASK_TRANSLITERATE_KN_TIG,
                    "instruction": "Transliterate this Tulu text from Kannada script into official Unicode 16.0 Tigalari script (ತಿಗಳಾರಿ ಲಿಪಿ).",
                    "input": kn,
                    "output": tig,
                }
                generated += 1
                if generated >= max_records:
                    break

                # Tigalari -> Kannada
                yield {
                    "task": self.TASK_TRANSLITERATE_TIG_KN,
                    "instruction": "Transliterate this Tigalari script (Unicode 16.0) text into standard Kannada script.",
                    "input": tig,
                    "output": kn,
                }
                generated += 1
                if generated >= max_records:
                    break

            # Task 3: Grammar & Case Morphology
            if include_grammar and ("Declension" in domain or "Conjugation" in domain):
                yield {
                    "task": self.TASK_GRAMMAR_CASE,
                    "instruction": "Analyze the morphological inflection and grammatical category of this Tulu word.",
                    "input": kn,
                    "output": f"Inflected Tulu form. Romanized: '{latin}'. Grammatical Category: {domain}.",
                }
                generated += 1
                if generated >= max_records:
                    break

    def export_jsonl(self, output_path: str, max_records: int = 5000) -> int:
        """Exports streaming records into a JSONL file with zero memory spike."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        count = 0

        with open(output_path, "w", encoding="utf-8") as out:
            for rec in self.build_instruction_records(max_records=max_records):
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

        return count


def main():
    parser = argparse.ArgumentParser(description="Lightweight stream dataset builder for Tulu LLM training.")
    parser.add_argument("--limit", type=int, default=5000, help="Max records to generate (default: 5000, light)")
    parser.add_argument("--output", type=str, default="datasets/tulu_llm_sft_light.jsonl", help="Output JSONL path")
    args = parser.parse_args()

    builder = TuluDatasetBuilder()
    print(f"Building lightweight dataset (max {args.limit} records)...")
    count = builder.export_jsonl(args.output, max_records=args.limit)
    file_size_kb = os.path.getsize(args.output) / 1024
    print(f"✓ Created {args.output}: {count} records ({file_size_kb:.1f} KB). Zero system burden.")


if __name__ == "__main__":
    main()
