"""
Tulu Dictionary & Word Translator Module
Provides translations between English / Kannada and native Tulu words (ತುಳು ಶಬ್ದಕೋಶ).
Includes phonetic Latin, Kannada script, and Tulu-Tigalari script representations
powered by the 1,000-word linguistic validation dataset.
"""

from typing import Dict, List, Optional
from .words_dataset_1000 import WORDS_DATASET_1000

TULU_DICTIONARY: List[Dict[str, str]] = [
    {
        "id": item["id"],
        "english": item["english_meaning"],
        "kannada_meaning": item["kannada"],
        "tulu_kannada": item["kannada"],
        "tulu_latin": item["latin_phonetic"],
        "tulu_tigalari": item["expected_tigalari"],
        "category": item["category"]
    }
    for item in WORDS_DATASET_1000
]


def lookup_tulu(query: str, category: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Looks up a word in the Tulu dictionary by English meaning, Kannada text,
    or Tulu phonetic string with substring and category filtering.
    """
    q = (query or "").strip().lower()
    if not q:
        return []

    cat_filter = category.lower() if category and category.lower() != "all" else None
    matches = []

    for item in TULU_DICTIONARY:
        if cat_filter and item["category"].lower() != cat_filter:
            continue
        if (q in item["english"].lower() or
            q in item["tulu_kannada"] or
            q in item["tulu_latin"].lower()):
            matches.append(item)

    return matches
