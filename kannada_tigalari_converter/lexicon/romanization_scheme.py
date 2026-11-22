"""
Canonical ASCII Romanization Scheme for Tulu and Kannada.
=========================================================
Single source of truth for the phonetic ASCII representation covering:
  - Short vs long vowels: a, aa, i, ii, u, uu, e, ee, o, oo, ai, au, R
  - Tulu-specific open vowel: 'ae' (Kannada ೆ್ / ಎ್, e.g. kODae, barpae)
  - Retroflexes: T, Th, D, Dh, N, L
  - Aspirates: kh, gh, Ch, jh, Th, Dh, th, dh, ph, bh
  - Sibilants: sh (palatal), Sh (retroflex), s (dental)
  - Nasals & Anusvara: ng (ಙ), ny/nj (ಞ), N (ಣ), n (ನ), m (ಮ), M (ಂ)
  - Visarga: H (ಃ)
  - Archaic Dravidian: rr (ಱ), zh (ೞ)
  - Geminates & Conjunct clusters: kk, tt, dd, pp, mm, etc.

This module provides:
  1. `to_canonical_roman(text, from_script="auto")`: converts any native script (Kannada, Tigalari) or loose Latin into strictly normalized canonical ASCII.
  2. `from_canonical_roman(text, to_script="kannada")`: cosmetic-only rendering back to Kannada/Tigalari for display.
  3. `CANONICAL_PHONEME_TOKENS`: canonical alphabet of tokens for tokenizer vocabularies.
"""

from typing import List, Dict, Set, Tuple
import re

# ---------------------------------------------------------------------------
# Canonical Token Inventory
# ---------------------------------------------------------------------------

VOWELS_CANONICAL = [
    "a", "aa", "i", "ii", "u", "uu", "R", "RR",
    "e", "ee", "ai", "o", "oo", "au",
    "ae", "aae"  # Tulu open-e and long open-e
]

CONSONANTS_CANONICAL = [
    "k", "kh", "g", "gh", "ng",
    "ch", "Ch", "j", "jh", "nj",
    "T", "Th", "D", "Dh", "N",
    "t", "th", "d", "dh", "n",
    "p", "ph", "b", "bh", "m",
    "y", "r", "rr", "l", "v",
    "sh", "Sh", "s", "h",
    "L", "zh"
]

SPECIAL_SIGNS = ["M", "H"]

# Full set of canonical sub-word tokens
CANONICAL_PHONEME_TOKENS: List[str] = sorted(
    list(set(VOWELS_CANONICAL + CONSONANTS_CANONICAL + SPECIAL_SIGNS)),
    key=lambda x: (-len(x), x)
)

# ---------------------------------------------------------------------------
# Native Kannada Script to Canonical ASCII Mapping
# ---------------------------------------------------------------------------

KN_VOWEL_TO_ROMAN = {
    'ಅ': 'a',   'ಆ': 'aa',  'ಇ': 'i',   'ಈ': 'ee',
    'ಉ': 'u',   'ಊ': 'oo',  'ಋ': 'Ru',   'ೠ': 'RU',
    'ಎ': 'e',   'ಏ': 'E',   'ಐ': 'ai',
    'ಒ': 'o',   'ಓ': 'O',   'ಔ': 'au',
    'ಎ್': 'ae'
}

KN_MATRA_TO_ROMAN = {
    'ಾ': 'aa',  'ಿ': 'i',   'ೀ': 'ee',
    'ು': 'u',   'ೂ': 'oo',  'ೃ': 'Ru',   'ೄ': 'RU',
    'ೆ': 'e',   'ೇ': 'E',   'ೈ': 'ai',
    'ೊ': 'o',   'ೋ': 'O',   'ೌ': 'au'
}

KN_CONSONANT_TO_ROMAN = {
    'ಕ': 'k',   'ಖ': 'kh',  'ಗ': 'g',   'ಘ': 'gh',  'ಙ': 'ng',
    'ಚ': 'ch',  'ಛ': 'Ch',  'ಜ': 'j',   'ಝ': 'jh',  'ಞ': 'nj',
    'ಟ': 'T',   'ಠ': 'Th',  'ಡ': 'D',   'ಢ': 'Dh',  'ಣ': 'N',
    'ತ': 't',   'ಥ': 'th',  'ದ': 'd',   'ಧ': 'dh',  'ನ': 'n',
    'ಪ': 'p',   'ಫ': 'ph',  'ಬ': 'b',   'ಭ': 'bh',  'ಮ': 'm',
    'ಯ': 'y',   'ರ': 'r',   'ಱ': 'rr',  'ಲ': 'l',   'ವ': 'v',
    'ಶ': 'sh',  'ಷ': 'Sh',  'ಸ': 's',   'ಹ': 'h',   'ಳ': 'L',
    'ೞ': 'zh'
}

KN_SIGNS_TO_ROMAN = {
    'ಂ': 'M',
    'ಃ': 'H'
}

# ---------------------------------------------------------------------------
# Reverse Mapping (Canonical ASCII to Kannada Script for cosmetic display)
# ---------------------------------------------------------------------------

ROMAN_TO_KN_INDEPENDENT_VOWEL = {
    'a': 'ಅ',   'aa': 'ಆ',  'i': 'ಇ',   'ii': 'ಈ',
    'u': 'ಉ',   'uu': 'ಊ',  'R': 'ಋ',   'RR': 'ೠ',
    'e': 'ಎ',   'ee': 'ಏ',  'ai': 'ಐ',
    'o': 'ಒ',   'oo': 'ಓ',  'au': 'ಔ',
    'ae': 'ಎ್', 'aae': 'ಆೆ್'
}

ROMAN_TO_KN_MATRA = {
    'a': '',    'aa': 'ಾ',  'i': 'ಿ',   'ii': 'ೀ',
    'u': 'ು',   'uu': 'ೂ',  'R': 'ೃ',   'RR': 'ೄ',
    'e': 'ೆ',   'ee': 'ೇ',  'ai': 'ೈ',
    'o': 'ೊ',   'oo': 'ೋ',  'au': 'ೌ',
    'ae': 'ೆ್', 'aae': 'ಾೆ್'
}

ROMAN_TO_KN_CONSONANT = {
    'k': 'ಕ',   'kh': 'ಖ',  'g': 'ಗ',   'gh': 'ಘ',  'ng': 'ಙ',
    'ch': 'ಚ',  'Ch': 'ಛ',  'c': 'ಚ',   'j': 'ಜ',   'jh': 'ಝ',  'nj': 'ಞ',
    'T': 'ಟ',   'Th': 'ಠ',  'D': 'ಡ',   'Dh': 'ಢ',  'N': 'ಣ',
    't': 'ತ',   'th': 'ಥ',  'd': 'ದ',   'dh': 'ಧ',  'n': 'ನ',
    'p': 'ಪ',   'ph': 'ಫ',  'b': 'ಬ',   'bh': 'ಭ',  'm': 'ಮ',
    'y': 'ಯ',   'r': 'ರ',   'rr': 'ಱ',  'l': 'ಲ',   'v': 'ವ',
    'sh': 'ಶ',  'Sh': 'ಷ',  's': 'ಸ',   'h': 'ಹ',   'L': 'ಳ',
    'zh': 'ೞ'
}

# List of consonant patterns sorted longest first for prefix parsing
ROMAN_CONSONANT_PATTERNS = sorted(ROMAN_TO_KN_CONSONANT.keys(), key=lambda x: -len(x))
ROMAN_VOWEL_PATTERNS = sorted(ROMAN_TO_KN_MATRA.keys(), key=lambda x: -len(x))


def to_canonical_roman(text: str, from_script: str = "auto") -> str:
    """
    Converts native script (Kannada or Tigalari) or loose Latin into strictly
    canonical ASCII romanization.

    Examples:
      - 'ಸೊಲ್ಮೆಲು' -> 'solmelu'
      - 'ಕೋಡೆ್' -> 'kODae'
      - 'ಬರ್ಪೆರ್' -> 'barper'
      - 'ನಮಸ್ಕಾರ' -> 'namaskaara'
      - 'ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ' -> 'yaan illag barpe'
    """
    if not text:
        return ""

    # First, if input is Tigalari, convert to Kannada using offline converter
    if from_script == "tigalari" or any(0x11380 <= ord(c) <= 0x113FF for c in text):
        from ..core.kannada_tigalari import tigalari_to_kannada
        text = tigalari_to_kannada(text)

    # If already Latin, normalize common variations to canonical scheme
    has_kannada = any(0x0C80 <= ord(c) <= 0x0CFF for c in text)
    if not has_kannada:
        return _normalize_latin_to_canonical(text)

    # Process Kannada script characters
    result: List[str] = []
    n = len(text)
    i = 0

    while i < n:
        ch = text[i]

        # Check for Tulu 'ae' digraph (ೆ followed by ್)
        if i + 1 < n and text[i] == 'ೆ' and text[i + 1] == '್':
            result.append('ae')
            i += 2
            continue

        # Independent Vowels
        if ch in KN_VOWEL_TO_ROMAN:
            # Check if followed by virama (rare ligature)
            if i + 1 < n and text[i + 1] == '್' and ch == 'ಎ':
                result.append('ae')
                i += 2
            else:
                result.append(KN_VOWEL_TO_ROMAN[ch])
                i += 1
            continue

        # Consonants
        if ch in KN_CONSONANT_TO_ROMAN:
            con_roman = KN_CONSONANT_TO_ROMAN[ch]
            # Look ahead for virama, matra, or inherent vowel
            if i + 1 < n:
                nxt = text[i + 1]
                # Check for Tulu 'ae' matra (ೆ + ್)
                if nxt == 'ೆ' and i + 2 < n and text[i + 2] == '್':
                    result.append(con_roman + 'ae')
                    i += 3
                    continue
                # Virama: suppresses inherent vowel
                if nxt == '್':
                    result.append(con_roman)
                    i += 2
                    continue
                # Dependent vowel matra
                if nxt in KN_MATRA_TO_ROMAN:
                    result.append(con_roman + KN_MATRA_TO_ROMAN[nxt])
                    i += 2
                    continue

            # Inherent vowel 'a'
            result.append(con_roman + 'a')
            i += 1
            continue

        # Signs
        if ch in KN_SIGNS_TO_ROMAN:
            result.append(KN_SIGNS_TO_ROMAN[ch])
            i += 1
            continue

        # Virama alone (should be handled with consonant, but if stray, skip)
        if ch == '್':
            i += 1
            continue

        # Other characters (whitespace, punctuation, ASCII)
        result.append(ch)
        i += 1

    return "".join(result)


def _normalize_latin_to_canonical(text: str) -> str:
    """
    Normalizes arbitrary Baraha/ITRANS Latin into canonical ASCII scheme:
      - long E -> ee
      - long O -> oo
      - retroflex L -> L
      - standardizes tulu open vowel 'ae'
    """
    t = text
    # Standardize long vowel casing if using E / O
    # If text is written like 'sOlmelu' -> 'solmelu'
    # Retain capital retroflexes T, D, N, L, Sh, Ch
    # Normalize Baraha 'E' -> 'ee', 'O' -> 'oo' where applicable
    t = re.sub(r'([kKgGcjJtTdDnpPbmMyrlvshL])E', r'\1ee', t)
    t = re.sub(r'([kKgGcjJtTdDnpPbmMyrlvshL])O', r'\1oo', t)
    t = re.sub(r'([kKgGcjJtTdDnpPbmMyrlvshL])A', r'\1aa', t)
    t = re.sub(r'([kKgGcjJtTdDnpPbmMyrlvshL])I', r'\1ii', t)
    t = re.sub(r'([kKgGcjJtTdDnpPbmMyrlvshL])U', r'\1uu', t)
    return t


def from_canonical_roman(text: str, to_script: str = "kannada") -> str:
    """
    Cosmetic-only rendering from canonical ASCII romanization to Kannada script
    (or Tigalari script via Kannada). Never used in the computational model.
    """
    if not text:
        return ""

    from ..core.tulu_phonetic import latin_to_kannada
    kn = latin_to_kannada(text)

    if to_script == "tigalari":
        from ..core.kannada_tigalari import kannada_to_tigalari
        return kannada_to_tigalari(kn)

    return kn
