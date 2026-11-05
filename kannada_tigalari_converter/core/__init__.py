"""
Core Transliteration & Script Conversion Submodule
==================================================
Handles bidirectional mapping between Kannada, Tulu-Tigalari (Unicode 16.0),
and Latin phonetic (Baraha/ITRANS) representations.
"""

from .kannada_tigalari import (
    kannada_to_tigalari,
    tigalari_to_kannada,
    inspect_codepoints,
    KANNADA_TO_TIGALARI,
    TIGALARI_TO_KANNADA,
)
from .tulu_phonetic import (
    latin_to_kannada,
    kannada_to_latin,
)
from .transliterator import (
    transliterate,
    detect_script,
    latin_to_tigalari,
    tigalari_to_latin,
)

__all__ = [
    "kannada_to_tigalari",
    "tigalari_to_kannada",
    "inspect_codepoints",
    "latin_to_kannada",
    "kannada_to_latin",
    "transliterate",
    "detect_script",
    "latin_to_tigalari",
    "tigalari_to_latin",
    "KANNADA_TO_TIGALARI",
    "TIGALARI_TO_KANNADA",
]
