#!/usr/bin/env python3
"""
Tulu Web Corpus Quality Segregator
==================================
Linguistic quality evaluation and segregation engine for web-scraped Tulu text
(Wikipedia, Wiktionary, OCR, and internet crawls).

Separates raw collected data into:
  - High-Quality Dataset: Fluent, complete, authentic Tulu sentences for LLM & NMT fine-tuning.
  - Low-Quality Dataset: Quarantined noise (wikitext markup, table splits, broken fragments,
    pure administrative Kannada, number lists, and unbalanced brackets).

Engineered for zero system strain: O(1) memory streaming (< 15MB RAM) and sub-second execution.
"""

import os
import re
import csv
import json
import unicodedata
from typing import Dict, Any, Tuple, List, Optional

# Authentic Tulu morphological suffixes, auxiliary verbs, and frequent lexical markers
TULU_LINGUISTIC_MARKERS = {
    # Auxiliary & conjugated verb endings
    "ಉಂಡು", "ಇತ್ತ್ಂಡ್", "ಬತ್ತ್ಂಡ್", "ಆಪುಂಡು", "ಇಪ್ಪುಂಡು", "ಆತ್ಂಡ್", "ಆತ್‌ಜಿ",
    "ಪೋಪುಂಡು", "ಕೊರ್ಪುಂಡು", "ಬರ್ಪುಂಡು", "ತಿನ್ಪುಂಡು", "ಪಾತೆರುಂಡು",
    "ಮಾಲ್ತೆರ್", "ಮಲ್ತೆರ್", "ಬರ್ಪೆರ್", "ಪೋಪೆರ್", "ಕೊರಿಯೆರ್", "ತೆರಿಯಿಜಿ",
    "ಬರ್ಪೆ", "ಪೋಪೆ", "ಮಾಲ್ಪೆ", "ಮಲ್ಪೆ", "ತಿನ್ಪೆ", "ಬಲೆ", "ತೂಲೆ", "ಪೋಲೆ",
    "ಬೋಡು", "ಬೋಡಾಪುಂಡು", "ಬಲ್ಲಿ", "ವಡ್", "ಆವಡ್",
    # Case & postposition markers
    "ಇಲ್ಲಗ್", "ಇಲ್ಲಡ್", "ಕುಡ್ಲಗ್", "ಕುಡ್ಲಡ್", "ತುಳುನಾಡ್", "ತುಳುನಾಡ್‌ಡ್",
    # Pronouns & interrogatives
    "ಯಾನ್", "ಎಂಕ್", "ಎನ್ನ", "ನಮ", "ಈರ್", "ಈರೆನ", "ಈರೆಗ್", "ಆಯೆ", "ಆಲ್", "ಅಕುಲು", "ಅಕ್ಲೆನ", "ಅಕ್ಲೆಗ್",
    "ಏರ್", "ಒಲ್ಪ", "ದಾದ", "ದಾಯೆ", "ಎಂಚ", "ಏತ್", "ಒಂಜಿ", "ರಡ್ಡ್", "ಮುಜಿ", "ನಾಲ್",
    # Conjunctions & adverbs
    "ಬುಕ್ಕೊ", "ಬುಕ್ಕ", "ಆಂಡ", "ಅಪಗ", "ಅಂಚನೆ", "ಇಂಚನೆ", "ಬೊಕ್ಕ", "ಇನಿ", "ಎಲ್ಲೆ", "ಕೋಡೆ್",
    # Core Tulu nouns & adjectives
    "ಬಾಸೆ", "ಅಪ್ಪೆ", "ಅಮ್ಮೆ", "ಇಲ್ಲ", "ಪೊರ್ಲು", "ಎಡ್ಡೆ", "ಮಾತ", "ಜನೊ", "ಪರ್ಬೊ",
    "ಸೊಲ್ಮೆಲು", "ಕಂಡೊ", "ಬಾರ್", "ಪೆತ್ತ", "ತಾರಾಯಿ", "ಬೂತೊ", "ದೈವೊ"
}

# Regex patterns for detecting noisy wikitext leaks and artifacts
WIKI_MARKUP_PATTERNS = [
    re.compile(r"scope\s*=\s*[\"']?col[\"']?", re.IGNORECASE),
    re.compile(r"alt\s*=\s*[^\|]+\|", re.IGNORECASE),
    re.compile(r"thumb\s*\|", re.IGNORECASE),
    re.compile(r"Category\s*:", re.IGNORECASE),
    re.compile(r"ವರ್ಗ\s*:", re.IGNORECASE),
    re.compile(r"ವರ್ಗೊ\s*:", re.IGNORECASE),
    re.compile(r"&[a-z]+;", re.IGNORECASE),  # HTML entities like &nbsp;
    re.compile(r"\[\[|\]\]|\{\{|\}\}"),
    re.compile(r"^=+[^=]+=+$"),             # Header like = References ==
    re.compile(r"https?://|www\.", re.IGNORECASE),
    re.compile(r"\|\s*([a-z0-9_\-]+)\s*=", re.IGNORECASE), # Template param like |width=
]

# Structural fragment indicators
DANGLING_STARTS = (",", ";", ":", ")", "]", "}", "»", "-", "—")
DANGLING_ENDS = (",", ";", ":", "(", "[", "{", "«", "-", "—")


class TuluQualityScorer:
    """Evaluates linguistic quality and identifies defects in Tulu text."""

    @classmethod
    def evaluate(cls, text: str) -> Tuple[float, str, Dict[str, Any]]:
        """
        Evaluates a candidate text string.
        Returns:
            (quality_score, status_or_reason, breakdown_metrics)
        """
        if not text or not text.strip():
            return 0.0, "empty_text", {"reason": "Empty string"}

        raw = text.strip()
        char_len = len(raw)
        words = raw.split()
        word_count = len(words)

        # ── 1. Hard Disqualifications (Immediate Low Quality) ──
        if word_count < 4:
            return 0.15, "fragment_too_short", {"words": word_count, "chars": char_len}

        if word_count > 60:
            return 0.35, "unsegmented_runon", {"words": word_count, "chars": char_len}

        if raw.startswith(DANGLING_STARTS):
            return 0.20, "broken_start_fragment", {"first_char": raw[0]}

        if raw.endswith(DANGLING_ENDS):
            return 0.20, "broken_end_fragment", {"last_char": raw[-1]}

        # Unbalanced brackets/parentheses
        if raw.count("(") != raw.count(")") or raw.count("[") != raw.count("]"):
            return 0.25, "unbalanced_brackets", {"open_p": raw.count("("), "close_p": raw.count(")")}

        # Check for wikitext/HTML leaks
        for pat in WIKI_MARKUP_PATTERNS:
            if pat.search(raw):
                return 0.20, "wiki_markup_leak", {"matched_pattern": pat.pattern}

        # Check digit and symbol density
        digits = sum(1 for c in raw if c.isdigit())
        if (digits / char_len) > 0.22:
            return 0.25, "excessive_digits_or_table_data", {"digit_ratio": digits / char_len}

        # Kannada Unicode script density
        kannada_chars = sum(1 for c in raw if "\u0C80" <= c <= "\u0CFF")
        kannada_ratio = kannada_chars / char_len
        if kannada_ratio < 0.45:
            return 0.30, "low_kannada_density", {"kannada_ratio": kannada_ratio}

        # ── 2. Quality Scoring Component Weights ──
        score = 0.0

        # Component A: Authentic Tulu Morphological & Lexical Marker Count (Max 0.40)
        # Check tokens against canonical Tulu markers
        tulu_matches = 0
        for marker in TULU_LINGUISTIC_MARKERS:
            if marker in raw:
                tulu_matches += 1

        if tulu_matches >= 3:
            score += 0.40
        elif tulu_matches == 2:
            score += 0.30
        elif tulu_matches == 1:
            score += 0.18
        else:
            # 0 markers: Might be pure Kannada without Tulu morphology
            score += 0.05

        # Component B: Sentence Structure & Terminal Completeness (Max 0.30)
        has_terminal_punct = raw.endswith((".", "!", "?", "।", "॥"))
        ends_with_finite_verb = any(
            raw.endswith(sfx) for sfx in (
                "ಂಡ್", "ಂಡು", "ೆರ್", "ರ್", "ೆ", "ಿಜಿ", "ೊಡು", "ವಡ್", "ಆತ್ಂಡ್", "ಉಂಡು"
            )
        )
        if has_terminal_punct or ends_with_finite_verb:
            score += 0.30
        else:
            score += 0.15

        # Component C: Length Sweet Spot (Max 0.15)
        if 6 <= word_count <= 35:
            score += 0.15
        elif 4 <= word_count <= 50:
            score += 0.10
        else:
            score += 0.05

        # Component D: Lexical Richness & Unique Ratio (Max 0.15)
        unique_ratio = len(set(w.lower() for w in words)) / word_count
        if unique_ratio >= 0.75:
            score += 0.15
        elif unique_ratio >= 0.55:
            score += 0.10
        else:
            score += 0.05

        final_score = round(min(1.0, score), 4)

        if final_score >= 0.60:
            status = "high_quality_fluent"
        elif final_score >= 0.45:
            status = "medium_quality"
        else:
            status = "low_quality_insufficient_tulu_features"

        breakdown = {
            "score": final_score,
            "words": word_count,
            "tulu_markers_found": tulu_matches,
            "kannada_density": round(kannada_ratio, 2),
            "lexical_richness": round(unique_ratio, 2),
        }
        return final_score, status, breakdown


class DatasetQualitySegregator:
    """
    Streams through web-scraped datasets and segregates them into
    high-quality and low-quality partitions with full audit telemetry.
    """

    def __init__(self, quality_threshold: float = 0.60):
        self.quality_threshold = quality_threshold

    def segregate_file(
        self,
        input_csv_path: str,
        high_quality_output: str,
        low_quality_output: str,
        text_column: str = "tulu_kannada",
    ) -> Dict[str, Any]:
        """
        Processes input CSV row by row with O(1) memory and outputs segregated datasets.
        """
        if not os.path.exists(input_csv_path):
            raise FileNotFoundError(f"Input file not found: {input_csv_path}")

        os.makedirs(os.path.dirname(os.path.abspath(high_quality_output)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(low_quality_output)), exist_ok=True)

        stats = {
            "input_file": input_csv_path,
            "total_records": 0,
            "high_quality_count": 0,
            "low_quality_count": 0,
            "high_quality_percent": 0.0,
            "rejection_reasons": {},
            "avg_quality_score": 0.0,
        }

        total_score = 0.0

        with open(input_csv_path, "r", encoding="utf-8", errors="replace") as fin, \
             open(high_quality_output, "w", encoding="utf-8", newline="") as fhigh, \
             open(low_quality_output, "w", encoding="utf-8", newline="") as flow:

            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames or ["id", "tulu_kannada", "tulu_tigalari", "tulu_latin"]

            # Append audit columns
            out_fields = list(fieldnames)
            for extra in ("quality_score", "quality_tier", "quality_reason"):
                if extra not in out_fields:
                    out_fields.append(extra)

            high_writer = csv.DictWriter(fhigh, fieldnames=out_fields)
            low_writer = csv.DictWriter(flow, fieldnames=out_fields)

            high_writer.writeheader()
            low_writer.writeheader()

            for row in reader:
                stats["total_records"] += 1
                text = row.get(text_column, "")
                score, reason, _ = TuluQualityScorer.evaluate(text)
                total_score += score

                row_copy = dict(row)
                row_copy["quality_score"] = f"{score:.2f}"
                row_copy["quality_reason"] = reason

                if score >= self.quality_threshold:
                    row_copy["quality_tier"] = "HIGH"
                    high_writer.writerow(row_copy)
                    stats["high_quality_count"] += 1
                else:
                    row_copy["quality_tier"] = "LOW"
                    low_writer.writerow(row_copy)
                    stats["low_quality_count"] += 1
                    stats["rejection_reasons"][reason] = stats["rejection_reasons"].get(reason, 0) + 1

        total = stats["total_records"]
        if total > 0:
            stats["high_quality_percent"] = round((stats["high_quality_count"] / total) * 100.0, 2)
            stats["avg_quality_score"] = round(total_score / total, 4)

        return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Segregate web-scraped dataset into high and low quality tiers")
    parser.add_argument("--input", type=str, default="datasets/tulu_wikipedia_corpus.csv", help="Input raw CSV path")
    parser.add_argument("--high-out", type=str, default="datasets/tulu_web_corpus_high_quality.csv", help="Output high quality CSV")
    parser.add_argument("--low-out", type=str, default="datasets/tulu_web_corpus_low_quality.csv", help="Output low quality CSV")
    parser.add_argument("--threshold", type=float, default=0.60, help="Quality threshold (default: 0.60)")
    args = parser.parse_args()

    segregator = DatasetQualitySegregator(quality_threshold=args.threshold)
    print(f"🔍 Analyzing and segregating web corpus: {args.input}")
    stats = segregator.segregate_file(args.input, args.high_out, args.low_out)

    print("\n" + "=" * 65)
    print("  TULU WEB CORPUS QUALITY SEGREGATION RESULTS")
    print("=" * 65)
    print(f"  Total Records Examined   : {stats['total_records']:,}")
    print(f"  ⭐ High-Quality Dataset : {stats['high_quality_count']:,} ({stats['high_quality_percent']}%)")
    print(f"  ⚠️  Low-Quality Quarantined: {stats['low_quality_count']:,} ({100 - stats['high_quality_percent']:.2f}%)")
    print(f"  Average Quality Score    : {stats['avg_quality_score']:.2f} / 1.00")
    print(f"  High-Quality Path        : {args.high_out}")
    print(f"  Low-Quality Path         : {args.low_out}")
    print("\n  Top Rejection Reasons in Low-Quality Data:")
    for reason, count in sorted(stats["rejection_reasons"].items(), key=lambda x: x[1], reverse=True)[:6]:
        print(f"    - {reason:<35} : {count:>5} records")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
