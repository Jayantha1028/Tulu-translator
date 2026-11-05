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


def _norm_phonetic(s: str) -> str:
    """Normalize short/long vowels for forgiving phonetic matching."""
    return (s.lower()
            .replace("aa", "a").replace("ee", "e").replace("ii", "i")
            .replace("oo", "o").replace("uu", "u").replace("sh", "s"))


def lookup_tulu(query: str, category: Optional[str] = None, enable_morphology: bool = True) -> List[Dict]:
    """
    Looks up a word in the Tulu dictionary by English meaning, Kannada text,
    or Tulu phonetic string with substring and category filtering.

    When enable_morphology=True (default), if an exact match is not found or
    for inflected wordforms (e.g. ಇಲ್ಲಡ್ -> ಇಲ್ಲ, ಕುಡ್ಲರ್ದ್ -> ಕುಡ್ಲ, ಬರ್ಪೆ -> ಬಲೆ),
    it runs the Tulu Morphological Analyzer to recover the lemma and returns
    the matched lexical entry annotated with morphological tags.
    """
    raw_q = (query or "").strip()
    q = raw_q.lower()
    if not q:
        return []

    cat_filter = category.lower() if category and category.lower() != "all" else None
    matches = []
    norm_q = _norm_phonetic(q)

    for item in TULU_DICTIONARY:
        if cat_filter and item["category"].lower() != cat_filter:
            continue
        item_latin = item["tulu_latin"].lower()
        if (q in item["english"].lower() or
            raw_q in item["tulu_kannada"] or
            q in item_latin or
            norm_q == _norm_phonetic(item_latin)):
            matches.append(dict(item))

    # If direct matches found without inflection analysis, return them
    if matches and any(raw_q == m["tulu_kannada"] or q == m["tulu_latin"].lower() for m in matches):
        return matches

    # Morphological fallback: attempt lemmatization if no exact match
    if enable_morphology and raw_q:
        try:
            from .tulu_morphology import analyze
            analysis = analyze(raw_q)
            lemma_kn = analysis.lemma_kannada
            if lemma_kn and lemma_kn != raw_q:
                # Search for the lemma in dictionary
                for item in TULU_DICTIONARY:
                    if cat_filter and item["category"].lower() != cat_filter:
                        continue
                    if item["tulu_kannada"] == lemma_kn:
                        enriched = dict(item)
                        enriched["inflected_form"] = raw_q
                        enriched["morph_tag"] = analysis.tag_string()
                        enriched["morph_details"] = analysis.to_dict()
                        if enriched not in matches:
                            matches.insert(0, enriched)
        except Exception:
            pass

    return matches
