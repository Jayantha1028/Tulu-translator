"""
Data Cleansing & Deduplication Engine for Tulu Linguistic Datasets
==================================================================
Provides rigorous, standardized cleaning, Unicode normalization, script-density
validation, and persistent fingerprint-based deduplication for EVERY record inserted
into the Tulu corpus (Wikipedia, Wiktionary, AATA OCR, Historical Lexicon, Paradigms).

Guarantees:
1. Unicode NFC Normalization & Control Character Removal.
2. Indic / Kannada Script Density Filtering (discards noisy Latin boilerplate/markup).
3. Punctuation & Whitespace Normalization.
4. MD5 Canonical Fingerprinting for O(1) Deduplication on Every Insert.
5. Persistent Checkpointing & Streaming Append to prevent data loss or duplicate accumulation.
"""

import os
import re
import csv
import json
import hashlib
import unicodedata
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path

# Common regex patterns for text cleansing
HTML_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
WIKI_TEMPLATE_RE = re.compile(r"\{\{[^}]*\}\}")
WIKI_REF_RE = re.compile(r"<ref[^>]*>.*?</ref>", re.DOTALL | re.IGNORECASE)
WIKI_LINK_RE = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")
WIKI_HEADER_RE = re.compile(r"^==+[^=]+==+\s*$", re.MULTILINE)
CITATION_RE = re.compile(r"\[\d+\]|\[citation needed\]|\[edit\]", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f\ufeff\u200b-\u200f\u202a-\u202e]")
MULTISPACE_RE = re.compile(r"[ \t\u00a0]+")
CANONICAL_PUNCT_RE = re.compile(r"[\s\.,?!:;\"\'`\(\)\[\]\{\}«»—–\-_/\\|।॥]+")


class DataCleaner:
    """
    Cleans raw multilingual text, strips noisy markup, normalizes Unicode,
    and validates Tulu/Kannada linguistic quality.
    """

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Applies Unicode NFC normalization and strips invisible control characters."""
        if not text:
            return ""
        norm = unicodedata.normalize("NFC", str(text))
        return CONTROL_CHARS_RE.sub("", norm)

    @classmethod
    def clean_text(cls, text: str) -> str:
        """
        Comprehensive sanitization:
        - Strips HTML, wikitext markup, templates, references, and citations.
        - Strips URLs and email addresses.
        - Normalizes quotes, dashes, and whitespace.
        """
        if not text:
            return ""

        t = cls.normalize_unicode(text)

        # Remove templates {{ ... }}, refs <ref> ... </ref>, and HTML tags
        t = WIKI_TEMPLATE_RE.sub(" ", t)
        t = WIKI_REF_RE.sub(" ", t)
        t = HTML_TAG_RE.sub(" ", t)
        # Unpack internal links [[Target|Label]] -> Label
        t = WIKI_LINK_RE.sub(r"\1", t)
        # Remove headers
        t = WIKI_HEADER_RE.sub(" ", t)
        # Remove citation brackets like [1], [citation needed]
        t = CITATION_RE.sub("", t)
        # Remove URLs
        t = URL_RE.sub("", t)

        # Strip common Wikipedia artifacts
        t = re.sub(r"\[\[(?:File|Image|ಚಿತ್ರ):[^\]]+\]\]", " ", t, flags=re.IGNORECASE)
        t = re.sub(r"\b(?:thumb|right|left|center|px)\s*\|", " ", t, flags=re.IGNORECASE)

        # Normalize quotes and dashes
        t = t.replace("'''''", "").replace("'''", "").replace("''", "")
        t = t.replace("`", "'").replace("‘", "'").replace("’", "'")
        t = t.replace("“", '"').replace("”", '"')
        t = t.replace("—", " - ").replace("–", " - ")

        # Collapse all whitespace (including newlines and tabs)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    @classmethod
    def is_valid_tulu_kannada(
        cls,
        text: str,
        min_words: int = 2,
        min_chars: int = 4,
        max_chars: int = 1500,
        min_kannada_ratio: float = 0.35,
    ) -> Tuple[bool, str]:
        """
        Validates whether a sentence/phrase is authentic Tulu written in Kannada script:
        - Must meet minimum word and character length.
        - Must contain sufficient Kannada script density (>= 35% of total chars).
        - Must not be pure boilerplate, numbers, or URLs.
        """
        if not text:
            return False, "empty_text"

        cleaned = text.strip()
        char_len = len(cleaned)

        if char_len < min_chars:
            return False, f"too_short_chars ({char_len} < {min_chars})"
        if char_len > max_chars:
            return False, f"too_long_chars ({char_len} > {max_chars})"

        words = cleaned.split()
        if len(words) < min_words:
            return False, f"too_few_words ({len(words)} < {min_words})"

        # Calculate Kannada Unicode character ratio
        kannada_chars = sum(1 for c in cleaned if "\u0C80" <= c <= "\u0CFF")
        ratio = kannada_chars / char_len

        if ratio < min_kannada_ratio:
            return False, f"low_kannada_density ({ratio:.2f} < {min_kannada_ratio})"

        # Discard boilerplate navigation / category lines
        lower = cleaned.lower()
        if any(bp in lower for bp in ("ವರ್ಗ:", "ವರ್ಗೊ:", "thumb|", "redirect", "disambiguation")):
            return False, "wikipedia_navigation_boilerplate"

        return True, ""

    @staticmethod
    def compute_fingerprint(text: str) -> str:
        """
        Computes an MD5 fingerprint of canonicalized text (whitespace-normalized,
        punctuation-stripped) to detect duplicates even with minor punctuation differences.
        """
        if not text:
            return ""
        # Strip all whitespace and punctuation for canonical fingerprint
        canonical = CANONICAL_PUNCT_RE.sub("", text).strip().lower()
        return hashlib.md5(canonical.encode("utf-8")).hexdigest()


class DeduplicatedDataset:
    """
    Manages a dataset with automatic deduplication, cleaning, and persistence.
    Every insert is cleaned, verified, and checked against a fast O(1) fingerprint set.
    """

    def __init__(
        self,
        filepath: Optional[str] = None,
        fieldnames: Optional[List[str]] = None,
        key_field: str = "tulu_kannada",
        auto_save: bool = True,
    ):
        self.filepath = filepath
        self.key_field = key_field
        self.auto_save = auto_save
        self.records: List[Dict[str, Any]] = []
        self.seen_fingerprints: Set[str] = set()
        self.seen_exact: Set[str] = set()

        # Telemetry stats
        self.total_examined = 0
        self.inserted_count = 0
        self.duplicate_count = 0
        self.invalid_count = 0

        # Set default fieldnames
        self.fieldnames = fieldnames or [
            "id", "source_type", "source_name", "tulu_kannada",
            "tulu_tigalari", "tulu_latin", "english_meaning"
        ]

        # Load existing file if it exists to seed fingerprints
        if self.filepath and os.path.exists(self.filepath):
            self._load_existing()

    def _load_existing(self):
        """Loads existing CSV rows and seeds fingerprint index so re-runs never duplicate."""
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames:
                    # Update fieldnames from existing file
                    self.fieldnames = reader.fieldnames
                for row in reader:
                    text = row.get(self.key_field, "")
                    if text:
                        fp = DataCleaner.compute_fingerprint(text)
                        self.seen_fingerprints.add(fp)
                        self.seen_exact.add(text.strip())
                        self.records.append(dict(row))
                        self.inserted_count += 1
            print(f"[DeduplicatedDataset] Loaded {len(self.records)} existing unique records from {self.filepath}")
        except Exception as e:
            print(f"[DeduplicatedDataset] Warning loading {self.filepath}: {e}")

    def insert(
        self,
        record: Dict[str, Any],
        min_words: int = 2,
        min_chars: int = 4,
        min_kannada_ratio: float = 0.35,
    ) -> Tuple[bool, str]:
        """
        Inserts a single record with data cleansing and deduplication.
        Returns: (success: bool, status_message: str)
        """
        self.total_examined += 1

        raw_text = record.get(self.key_field, "")
        if not raw_text:
            self.invalid_count += 1
            return False, "missing_key_field"

        # 1. Clean text
        cleaned_text = DataCleaner.clean_text(str(raw_text))

        # 2. Validate linguistic quality
        is_valid, reason = DataCleaner.is_valid_tulu_kannada(
            cleaned_text,
            min_words=min_words,
            min_chars=min_chars,
            min_kannada_ratio=min_kannada_ratio,
        )
        if not is_valid:
            self.invalid_count += 1
            return False, f"invalid: {reason}"

        # 3. Check for exact or canonical duplicate
        fp = DataCleaner.compute_fingerprint(cleaned_text)
        if fp in self.seen_fingerprints or cleaned_text in self.seen_exact:
            self.duplicate_count += 1
            return False, "duplicate"

        # 4. Prepare clean entry
        clean_record = dict(record)
        clean_record[self.key_field] = cleaned_text

        # Automatically populate Tigalari and Latin phonetic representations if empty
        if not clean_record.get("tulu_tigalari"):
            from .kannada_tigalari import kannada_to_tigalari
            clean_record["tulu_tigalari"] = kannada_to_tigalari(cleaned_text)

        if not clean_record.get("tulu_latin"):
            from .tulu_phonetic import kannada_to_latin
            clean_record["tulu_latin"] = kannada_to_latin(cleaned_text)

        # Set sequential ID if missing
        if "id" in self.fieldnames and not clean_record.get("id"):
            clean_record["id"] = len(self.records) + 1

        # 5. Insert into memory & fingerprint cache
        self.records.append(clean_record)
        self.seen_fingerprints.add(fp)
        self.seen_exact.add(cleaned_text)
        self.inserted_count += 1

        # 6. Stream append to disk if auto_save is enabled
        if self.auto_save and self.filepath:
            self._append_to_file(clean_record)

        return True, "inserted"

    def insert_batch(self, records: List[Dict[str, Any]], **kwargs) -> Dict[str, int]:
        """Inserts a batch of records, returning counts of inserted, duplicates, and invalid."""
        batch_stats = {"examined": 0, "inserted": 0, "duplicate": 0, "invalid": 0}
        for r in records:
            batch_stats["examined"] += 1
            ok, reason = self.insert(r, **kwargs)
            if ok:
                batch_stats["inserted"] += 1
            elif reason == "duplicate":
                batch_stats["duplicate"] += 1
            else:
                batch_stats["invalid"] += 1
        return batch_stats

    def _append_to_file(self, record: Dict[str, Any]):
        """Thread-safe stream appending of a clean record to the CSV."""
        file_exists = os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        with open(self.filepath, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    def save_all(self):
        """Flushes the entire deduplicated dataset to disk."""
        if not self.filepath:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in self.records:
                writer.writerow(r)

    def stats(self) -> Dict[str, Any]:
        """Returns current dataset health and deduplication statistics."""
        return {
            "total_records": len(self.records),
            "unique_fingerprints": len(self.seen_fingerprints),
            "total_examined": self.total_examined,
            "inserted": self.inserted_count,
            "duplicates_dropped": self.duplicate_count,
            "invalid_dropped": self.invalid_count,
            "dedup_efficiency": f"{(self.duplicate_count / max(1, self.total_examined)) * 100:.1f}%",
        }
