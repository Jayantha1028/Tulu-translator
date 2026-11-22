"""
kannada_tigalari_converter.nlp.tulu_tokenizer_tool
==================================================
Vocabulary and tokenizer manager for Canonical ASCII Romanized Tulu and Kannada.
Patches Hugging Face / SLM tokenizers with the canonical ASCII phoneme tokens
(retroflexes, aspirates, long vowels, Tulu open-e 'ae', geminates, and grammatical suffixes).
Guarantees NO native Kannada or Tigalari codepoints in the model vocabulary.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (ROOT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.lexicon.romanization_scheme import (
    CANONICAL_PHONEME_TOKENS,
    VOWELS_CANONICAL,
    CONSONANTS_CANONICAL,
    SPECIAL_SIGNS,
)


class TuluTokenizerTool:
    """Manages canonical ASCII romanized tokens for zero-burden model tokenizers."""

    # Frequent morphological suffix tokens in romanized Tulu & Kannada
    COMMON_ROMAN_AFFIXES = [
        "-g", "-D", "-d", "-da", "-de", "-rd", "-rdu",
        "-e", "-er", "-ar", "-par", "-per", "-pe",
        "-puMdu", "-tMD", "-ttMD", "-iji", "-oDu",
        "-yere", "-naga", "-ondu", "-aver", "-aadu",
        "ae", "aae", "kODae", "barsae"
    ]

    @classmethod
    def get_canonical_roman_tokens(cls) -> List[str]:
        """Returns the full list of canonical ASCII tokens with zero Indic/Tigalari codepoints."""
        seen = set()
        out = []

        # 1. Phoneme atoms (vowels, consonants, retroflexes, aspirates)
        for tok in CANONICAL_PHONEME_TOKENS:
            if tok not in seen and all(ord(c) < 128 for c in tok):
                seen.add(tok)
                out.append(tok)

        # 2. Frequent romanized morphological affixes and Tulu-specific phonemes
        for tok in cls.COMMON_ROMAN_AFFIXES:
            if tok not in seen and all(ord(c) < 128 for c in tok):
                seen.add(tok)
                out.append(tok)

        return out

    @classmethod
    def get_full_tulu_token_list(cls) -> List[str]:
        """Backward-compatible alias returning the pure ASCII romanized token set."""
        return cls.get_canonical_roman_tokens()

    @classmethod
    def export_token_catalog(cls, output_path: Optional[str] = None) -> str:
        """Exports JSON catalog of canonical ASCII tokens (<10 KB)."""
        path = output_path or os.path.join(ROOT_DIR, "datasets", "tulu_roman_custom_tokens.json")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        token_list = cls.get_canonical_roman_tokens()
        catalog = {
            "version": "Canonical ASCII Romanization (Tulu-Kannada Standard)",
            "encoding": "ASCII-only (Zero Indic/Tigalari Codepoints)",
            "total_tokens": len(token_list),
            "tokens": token_list,
            "vowels": VOWELS_CANONICAL,
            "consonants": CONSONANTS_CANONICAL,
            "signs": SPECIAL_SIGNS,
            "affixes": cls.COMMON_ROMAN_AFFIXES,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=True, indent=2)

        return path

    @classmethod
    def add_tokens_to_hf_tokenizer(cls, tokenizer: Any) -> int:
        """Adds canonical ASCII romanized tokens to any Hugging Face PreTrainedTokenizer

        without full tokenizer retraining. Returns count of newly added tokens.
        """
        token_list = cls.get_canonical_roman_tokens()
        num_added = tokenizer.add_tokens(token_list)
        return num_added


def main():
    path = TuluTokenizerTool.export_token_catalog()
    tokens = TuluTokenizerTool.get_canonical_roman_tokens()
    print(f"✓ Generated Canonical ASCII vocabulary catalog: {len(tokens)} tokens at {path}")
    print(f"  All tokens pure ASCII: {all(all(ord(c) < 128 for c in t) for t in tokens)}")
    print(f"  Sample tokens: {tokens[:12]}")


if __name__ == "__main__":
    main()
