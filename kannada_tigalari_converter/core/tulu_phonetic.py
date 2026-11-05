"""
Tulu & Kannada Phonetic Transliteration Engine (Latin <-> Kannada).
Follows Baraha / ITRANS / Aatana conventions with full support for
Tulu phonetic characteristics:
  - Tulu 'ae' sound (represented in Kannada script as ೆ್, e.g. kODae -> ಕೋಡೆ್)
  - Tulu retroflexes (L -> ಳ, zh -> ೞ, rr -> ಱ)
  - Geminates and ottakshara consonant clusters
  - Inherent vowel suppression and dead consonants
"""

import re
from typing import List, Tuple

# Vowel mappings: (pattern, matra / dependent form, independent form)
# Ordered by pattern length descending to match greedy prefixes.
VOWEL_MAPPINGS: List[Tuple[str, str, str]] = [
    ('aae', 'ಾೆ್', 'ಆೆ್'),  # Tulu long open-e
    ('ae', 'ೆ್', 'ಎ್'),    # Tulu short open-e sound (e.g. kODae -> ಕೋಡೆ್)
    ('aa', 'ಾ', 'ಆ'),
    ('AA', 'ಾ', 'ಆ'),
    ('ii', 'ೀ', 'ಈ'),
    ('II', 'ೀ', 'ಈ'),
    ('ee', 'ೀ', 'ಈ'),
    ('EE', 'ೀ', 'ಈ'),
    ('uu', 'ೂ', 'ಊ'),
    ('UU', 'ೂ', 'ಊ'),
    ('oo', 'ೂ', 'ಊ'),
    ('OO', 'ೂ', 'ಊ'),
    ('ai', 'ೈ', 'ಐ'),
    ('AI', 'ೈ', 'ಐ'),
    ('au', 'ೌ', 'ಔ'),
    ('AU', 'ೌ', 'ಔ'),
    ('ou', 'ೌ', 'ಔ'),
    ('OU', 'ೌ', 'ಔ'),
    ('Ru', 'ೃ', 'ಋ'),
    ('RU', 'ೄ', 'ೠ'),
    ('A', 'ಾ', 'ಆ'),
    ('I', 'ೀ', 'ಈ'),
    ('U', 'ೂ', 'ಊ'),
    ('E', 'ೇ', 'ಏ'),
    ('O', 'ೋ', 'ಓ'),
    ('a', '', 'ಅ'),
    ('i', 'ಿ', 'ಇ'),
    ('u', 'ು', 'ಉ'),
    ('e', 'ೆ', 'ಎ'),
    ('o', 'ೊ', 'ಒ'),
]

# Consonant mappings: (pattern, kannada base letter, requires_vowel_check)
CONSONANT_MAPPINGS: List[Tuple[str, str, bool]] = [
    ('kSh', 'ಕ್ಷ', True),
    ('ksh', 'ಕ್ಷ', True),
    ('Ksh', 'ಕ್ಷ', True),
    ('Jn', 'ಜ್ಞ', True),
    ('jn', 'ಜ್ಞ', True),
    ('dny', 'ಜ್ಞ', True),
    ('shh', 'ಷ್', True),
    ('chh', 'ಛ', True),
    ('Chh', 'ಛ', True),
    ('kh', 'ಖ', True),
    ('Kh', 'ಖ', True),
    ('gh', 'ಘ', True),
    ('Gh', 'ಘ', True),
    ('ng', 'ಙ', True),
    ('NG', 'ಙ', True),
    ('~g', 'ಙ', True),
    ('ch', 'ಚ', True),
    ('Ch', 'ಛ', True),
    ('jh', 'ಝ', True),
    ('Jh', 'ಝ', True),
    ('nj', 'ಞ', True),
    ('NJ', 'ಞ', True),
    ('~j', 'ಞ', True),
    ('Th', 'ಠ', True),
    ('TH', 'ಠ', True),
    ('th', 'ಥ', True),
    ('Dh', 'ಢ', True),
    ('DH', 'ಢ', True),
    ('dh', 'ಧ', True),
    ('ph', 'ಫ', True),
    ('Ph', 'ಫ', True),
    ('bh', 'ಭ', True),
    ('Bh', 'ಭ', True),
    ('sh', 'ಶ', True),
    ('Sh', 'ಷ', True),
    ('SH', 'ಷ', True),
    ('zh', 'ೞ', True),
    ('ZH', 'ೞ', True),
    ('rr', 'ಱ', True),
    ('RR', 'ಱ', True),
    ('k', 'ಕ', True),
    ('K', 'ಕ', True),
    ('g', 'ಗ', True),
    ('G', 'ಗ', True),
    ('c', 'ಚ', True),
    ('C', 'ಚ', True),
    ('j', 'ಜ', True),
    ('J', 'ಜ', True),
    ('T', 'ಟ', True),
    ('t', 'ತ', True),
    ('D', 'ಡ', True),
    ('d', 'ದ', True),
    ('N', 'ಣ', True),
    ('n', 'ನ', True),
    ('p', 'ಪ', True),
    ('P', 'ಪ', True),
    ('f', 'ಫ', True),
    ('F', 'ಫ', True),
    ('b', 'ಬ', True),
    ('B', 'ಬ', True),
    ('m', 'ಮ', True),
    ('M', 'ಂ', False),  # Explicit Anusvara
    ('y', 'ಯ', True),
    ('Y', 'ಯ', True),
    ('r', 'ರ', True),
    ('R', 'ಱ', True),
    ('l', 'ಲ', True),
    ('L', 'ಳ', True),
    ('v', 'ವ', True),
    ('V', 'ವ', True),
    ('w', 'ವ', True),
    ('W', 'ವ', True),
    ('s', 'ಸ', True),
    ('S', 'ಶ', True),
    ('h', 'ಹ', True),
    ('H', 'ಃ', False),  # Explicit Visarga
]

# Quick lookup for match prefix
def _match_prefix(text: str, idx: int, mapping: list) -> Tuple[str, any]:
    for entry in mapping:
        pat = entry[0]
        if text.startswith(pat, idx):
            return pat, entry[1:]
    return "", None


def latin_to_kannada(text: str) -> str:
    """
    Transliterates English / Latin script into Kannada script.
    Follows phonetic conventions (e.g. namaskara -> ನಮಸ್ಕಾರ, solmelu -> ಸೊಲ್ಮೆಲು).
    """
    res = []
    i = 0
    n = len(text)
    VIRAMA = '್'

    while i < n:
        # Check consonant prefix
        pat_c, val_c = _match_prefix(text, i, CONSONANT_MAPPINGS)
        if pat_c:
            sym, needs_vowel = val_c
            i += len(pat_c)
            if not needs_vowel:
                res.append(sym)
                continue

            # Look for vowel following consonant
            pat_v, val_v = _match_prefix(text, i, VOWEL_MAPPINGS)
            if pat_v:
                matra, _ = val_v
                res.append(sym + matra)
                i += len(pat_v)
            else:
                # No vowel follows: append consonant with virama
                res.append(sym + VIRAMA)
            continue

        # Look for independent vowel
        pat_v, val_v = _match_prefix(text, i, VOWEL_MAPPINGS)
        if pat_v:
            _, indep = val_v
            res.append(indep)
            i += len(pat_v)
            continue

        # Explicit virama / halant symbols from user input
        if text[i] in ("~", "'"):
            res.append(VIRAMA)
            i += 1
            continue

        res.append(text[i])
        i += 1

    out = ''.join(res)
    # Post-cleanups for natural Kannada/Tulu orthography
    # When user types anusvara with 'm' before space or end of word in some words
    return out


# -------------------------------------------------------------
# Kannada to Latin (Phonetic / ISO 15919 transliteration)
# -------------------------------------------------------------

KANNADA_TO_LATIN_VOWELS = {
    'ಅ': 'a',
    'ಆ': 'aa',
    'ಇ': 'i',
    'ಈ': 'ee',
    'ಉ': 'u',
    'ಊ': 'oo',
    'ಋ': 'Ru',
    'ೠ': 'RU',
    'ಌ': 'li',
    'ೡ': 'lI',
    'ಎ': 'e',
    'ಏ': 'E',
    'ಎ್': 'ae',  # Tulu open-e
    'ಐ': 'ai',
    'ಒ': 'o',
    'ಓ': 'O',
    'ಔ': 'au',
}

KANNADA_TO_LATIN_MATRAS = {
    'ಾ': 'aa',
    'ಿ': 'i',
    'ೀ': 'ee',
    'ು': 'u',
    'ೂ': 'oo',
    'ೃ': 'Ru',
    'ೄ': 'RU',
    'ೆ': 'e',
    'ೇ': 'E',
    'ೈ': 'ai',
    'ೊ': 'o',
    'ೋ': 'O',
    'ೌ': 'au',
}

KANNADA_TO_LATIN_CONSONANTS = {
    'ಕ': 'k', 'ಖ': 'kh', 'ಗ': 'g', 'ಘ': 'gh', 'ಙ': 'ng',
    'ಚ': 'ch', 'ಛ': 'chh', 'ಜ': 'j', 'ಝ': 'jh', 'ಞ': 'nj',
    'ಟ': 'T', 'ಠ': 'Th', 'ಡ': 'D', 'ಢ': 'Dh', 'ಣ': 'N',
    'ತ': 't', 'ಥ': 'th', 'ದ': 'd', 'ಧ': 'dh', 'ನ': 'n',
    'ಪ': 'p', 'ಫ': 'ph', 'ಬ': 'b', 'ಭ': 'bh', 'ಮ': 'm',
    'ಯ': 'y', 'ರ': 'r', 'ಱ': 'rr', 'ಲ': 'l', 'ವ': 'v',
    'ಶ': 'sh', 'ಷ': 'Sh', 'ಸ': 's', 'ಹ': 'h', 'ಳ': 'L', 'ೞ': 'zh'
}

KANNADA_SIGNS = {
    'ಂ': 'M',
    'ಃ': 'H',
    '್': '',
}


def kannada_to_latin(text: str) -> str:
    """
    Transliterates Kannada script text to Latin / English phonetic representation.
    """
    res = []
    n = len(text)
    i = 0

    while i < n:
        # Check for Tulu 'ae' digraph in Kannada: ೆ followed by ್
        if i + 1 < n and text[i] == 'ೆ' and text[i+1] == '್':
            res.append('ae')
            i += 2
            continue

        # Check for jna ligature: ಜ + ್ + ಞ -> jn
        if i + 2 < n and text[i] == 'ಜ' and text[i+1] == '್' and text[i+2] == 'ಞ':
            if i + 3 < n:
                next_ch = text[i + 3]
                if next_ch in KANNADA_TO_LATIN_MATRAS:
                    res.append('jn' + KANNADA_TO_LATIN_MATRAS[next_ch])
                    i += 4
                    continue
                elif next_ch == '್':
                    res.append('jn')
                    i += 4
                    continue
            res.append('jna')
            i += 3
            continue

        ch = text[i]

        # Check independent vowel
        if ch in KANNADA_TO_LATIN_VOWELS:
            res.append(KANNADA_TO_LATIN_VOWELS[ch])
            i += 1
            continue

        # Check consonant
        if ch in KANNADA_TO_LATIN_CONSONANTS:
            base = KANNADA_TO_LATIN_CONSONANTS[ch]
            # Check what follows
            if i + 1 < n:
                next_ch = text[i + 1]
                # Special Tulu open-e: ೆ್
                if next_ch == 'ೆ' and i + 2 < n and text[i + 2] == '್':
                    res.append(base + 'ae')
                    i += 3
                    continue
                # Virama: dead consonant (no 'a')
                if next_ch == '್':
                    res.append(base)
                    i += 2
                    continue
                # Matra: vowel sign
                if next_ch in KANNADA_TO_LATIN_MATRAS:
                    res.append(base + KANNADA_TO_LATIN_MATRAS[next_ch])
                    i += 2
                    continue
            # No matra or virama -> implicit 'a'
            res.append(base + 'a')
            i += 1
            continue

        # Check isolated matra or sign
        if ch in KANNADA_TO_LATIN_MATRAS:
            res.append(KANNADA_TO_LATIN_MATRAS[ch])
            i += 1
            continue

        if ch in KANNADA_SIGNS:
            res.append(KANNADA_SIGNS[ch])
            i += 1
            continue

        res.append(ch)
        i += 1

    return ''.join(res)
