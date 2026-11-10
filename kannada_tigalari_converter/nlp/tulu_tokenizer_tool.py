"""
kannada_tigalari_converter.nlp.tulu_tokenizer_tool
==================================================
Lightweight vocabulary and tokenizer analyzer for Unicode 16.0 Tigalari and Tulu-Kannada aksharas.
Allows instant vocabulary expansion for standard LLM tokenizers with zero retraining cost.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure project paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (ROOT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.core.kannada_tigalari import (
    KANNADA_TO_TIGALARI,
    TIGALARI_TO_KANNADA,
)


class TuluTokenizerTool:
    """Extracts and provides Unicode 16.0 Tigalari and Tulu phonemes for LLM tokenizers."""

    # Special Tulu phonemes not in standard Kannada
    SPECIAL_TULU_CHARACTERS = [
        "ೆ್",   # Tulu open-e / ae vowel diacritic
        "ಱ",   # Alveolar Ra (U+0CA1)
        "ೞ",   # Retroflex Liquid Zha (U+0CDE)
        "ಞ",   # Palatal Nasal Nya (U+0C9E)
        "ಙ",   # Velar Nasal Nga (U+0C99)
        "್",   # Halant / Virama (U+0CCD)
    ]

    @classmethod
    def get_unicode_16_tigalari_tokens(cls) -> List[str]:
        """Collects all allocated official Unicode 16.0 Tigalari codepoints (U+11380 to U+113FF)."""
        tokens = []
        for cp in range(0x11380, 0x113E3):
            char = chr(cp)
            tokens.append(char)
        return tokens

    @classmethod
    def get_full_tulu_token_list(cls) -> List[str]:
        """Returns unified list of special Tulu and Unicode 16.0 Tigalari tokens."""
        seen = set()
        out = []

        for ch in cls.SPECIAL_TULU_CHARACTERS + cls.get_unicode_16_tigalari_tokens():
            if ch not in seen:
                seen.add(ch)
                out.append(ch)

        return out

    @classmethod
    def export_token_catalog(cls, output_path: Optional[str] = None) -> str:
        """Exports JSON catalog of custom tokens (<10 KB)."""
        path = output_path or os.path.join(ROOT_DIR, "datasets", "tulu_custom_tokens.json")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        token_list = cls.get_full_tulu_token_list()
        catalog = {
            "version": "Unicode 16.0 (Tulu-Tigalari Standard)",
            "total_tokens": len(token_list),
            "tokens": token_list,
            "special_tulu_phonemes": cls.SPECIAL_TULU_CHARACTERS,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        return path

    @classmethod
    def add_tokens_to_hf_tokenizer(cls, tokenizer: Any) -> int:
        """Adds Tulu-Tigalari tokens to any Hugging Face PreTrainedTokenizer

        without full tokenizer retraining. Returns count of newly added tokens.
        """
        token_list = cls.get_full_tulu_token_list()
        num_added = tokenizer.add_tokens(token_list)
        return num_added


def main():
    path = TuluTokenizerTool.export_token_catalog()
    tokens = TuluTokenizerTool.get_full_tulu_token_list()
    print(f"✓ Generated Tulu-Tigalari vocabulary catalog: {len(tokens)} tokens at {path}")
    print(f"  Sample codepoints: {[f'U+{ord(c):04X}' for c in tokens[:5]]}")


if __name__ == "__main__":
    main()
