"""
Kannada <-> Tulu-Tigalari Transliteration Module
Based on the Unicode 16.0 Standard (Tulu-Tigalari block: U+11380 - U+113FF).
Fully supports short/long E & O distinctions, conjuncts (conjoiner vs virama),
and Tulu phonetic combinations.
"""

import unicodedata
from typing import Dict, List, Tuple

# -------------------------------------------------------------
# Character Sets & Mappings (Unicode 16.0 Tulu-Tigalari Block)
# -------------------------------------------------------------

KANNADA_CONSONANTS = {
    'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ',
    'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ',
    'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ',
    'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ',
    'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ',
    'ಯ', 'ರ', 'ಱ', 'ಲ', 'ವ',
    'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ', 'ೞ'
}

KANNADA_TO_TIGALARI: Dict[str, str] = {
    # --- Independent Vowels (ಸ್ವರಗಳು) ---
    'ಅ': '\U00011380',  # TULU-TIGALARI LETTER A
    'ಆ': '\U00011381',  # TULU-TIGALARI LETTER AA
    'ಇ': '\U00011382',  # TULU-TIGALARI LETTER I
    'ಈ': '\U00011383',  # TULU-TIGALARI LETTER II
    'ಉ': '\U00011384',  # TULU-TIGALARI LETTER U
    'ಊ': '\U00011385',  # TULU-TIGALARI LETTER UU
    'ಋ': '\U00011386',  # TULU-TIGALARI LETTER VOCALIC R
    'ೠ': '\U00011387',  # TULU-TIGALARI LETTER VOCALIC RR
    'ಌ': '\U00011388',  # TULU-TIGALARI LETTER VOCALIC L
    'ೡ': '\U00011389',  # TULU-TIGALARI LETTER VOCALIC LL
    'ಎ': '\U0001138A',  # TULU-TIGALARI LETTER E (Short E)
    'ಏ': '\U0001138B',  # TULU-TIGALARI LETTER EE (Long E)
    'ಐ': '\U0001138E',  # TULU-TIGALARI LETTER AI
    'ಒ': '\U0001138F',  # TULU-TIGALARI LETTER O (Short O)
    'ಓ': '\U00011390',  # TULU-TIGALARI LETTER OO (Long O)
    'ಔ': '\U00011391',  # TULU-TIGALARI LETTER AU

    # --- Consonants (ವ್ಯಂಜನಗಳು) ---
    # Velar (ಕ-ವರ್ಗ)
    'ಕ': '\U00011392',
    'ಖ': '\U00011393',
    'ಗ': '\U00011394',
    'ಘ': '\U00011395',
    'ಙ': '\U00011396',
    # Palatal (ಚ-ವರ್ಗ)
    'ಚ': '\U00011397',
    'ಛ': '\U00011398',
    'ಜ': '\U00011399',
    'ಝ': '\U0001139A',
    'ಞ': '\U0001139B',
    # Retroflex (ಟ-ವರ್ಗ)
    'ಟ': '\U0001139C',
    'ಠ': '\U0001139D',
    'ಡ': '\U0001139E',
    'ಢ': '\U0001139F',
    'ಣ': '\U000113A0',
    # Dental (ತ-ವರ್ಗ)
    'ತ': '\U000113A1',
    'ಥ': '\U000113A2',
    'ದ': '\U000113A3',
    'ಧ': '\U000113A4',
    'ನ': '\U000113A5',
    # Labial (ಪ-ವರ್ಗ)
    'ಪ': '\U000113A6',
    'ಫ': '\U000113A7',
    'ಬ': '\U000113A8',
    'ಭ': '\U000113A9',
    'ಮ': '\U000113AA',
    # Non-varga / Approximants & Sibilants
    'ಯ': '\U000113AB',
    'ರ': '\U000113AC',
    'ಱ': '\U000113B4',
    'ಲ': '\U000113AD',
    'ಳ': '\U000113B3',
    'ವ': '\U000113AE',
    'ಶ': '\U000113AF',
    'ಷ': '\U000113B0',
    'ಸ': '\U000113B1',
    'ಹ': '\U000113B2',
    'ೞ': '\U000113B5',

    # --- Vowel Signs / Matras (ಮಾತ್ರೆಗಳು) ---
    'ಾ': '\U000113B8',  # VOWEL SIGN AA
    'ಿ': '\U000113B9',  # VOWEL SIGN I
    'ೀ': '\U000113BA',  # VOWEL SIGN II
    'ು': '\U000113BB',  # VOWEL SIGN U
    'ೂ': '\U000113BC',  # VOWEL SIGN UU
    'ೃ': '\U000113BD',  # VOWEL SIGN VOCALIC R
    'ೄ': '\U000113BE',  # VOWEL SIGN VOCALIC RR
    'ೢ': '\U000113BF',  # VOWEL SIGN VOCALIC L
    'ೣ': '\U000113C0',  # VOWEL SIGN VOCALIC LL
    'ೆ': '\U000113C1',  # VOWEL SIGN E (Short E)
    'ೇ': '\U000113C2',  # VOWEL SIGN EE (Long E)
    'ೈ': '\U000113C5',  # VOWEL SIGN AI
    'ೊ': '\U000113C6',  # VOWEL SIGN O (Short O)
    'ೋ': '\U000113C7',  # VOWEL SIGN OO (Long O)
    'ೌ': '\U000113C8',  # VOWEL SIGN AU

    # --- Yogavahakagalu & Punctuation Signs ---
    'ಂ': '\U000113CC',  # SIGN ANUSVARA
    'ಃ': '\U000113CD',  # SIGN VISARGA
    'ಁ': '\U000113CA',  # SIGN CANDRABINDU
    'ಽ': '\U000113B7',  # SIGN AVAGRAHA
    '।': '\U000113D4',  # DANDA
    '॥': '\U000113D5',  # DOUBLE DANDA
}

# Bidirectional Reverse Mapping
TIGALARI_TO_KANNADA: Dict[str, str] = {
    v: k for k, v in KANNADA_TO_TIGALARI.items()
}

# Control characters reverse mapping
TIGALARI_TO_KANNADA['\U000113CE'] = '್'  # SIGN VIRAMA
TIGALARI_TO_KANNADA['\U000113D0'] = '್'  # CONJOINER
# Legacy / alternative Tigalari characters if encountered
TIGALARI_TO_KANNADA['\U0001138C'] = 'ಎ'  # Tulu-Tigalari archaic letter
TIGALARI_TO_KANNADA['\U000113C3'] = 'ೆ'  # Tulu-Tigalari archaic vowel sign
TIGALARI_TO_KANNADA['\U000113CF'] = '್'  # LOOPED VIRAMA


def kannada_to_tigalari(text: str, form_conjuncts: bool = True) -> str:
    """
    Converts Kannada script text to Tulu-Tigalari script (Unicode 16.0).
    
    :param text: Input string in Kannada script.
    :param form_conjuncts: When True, uses TULU-TIGALARI CONJOINER (U+113D0)
                           for consonant clusters / ottakshara;
                           otherwise uses VIRAMA (U+113CE).
    :return: Transliterated string in Tulu-Tigalari Unicode.
    """
    # 1. Normalize unicode characters (NFC form)
    text = unicodedata.normalize('NFC', text)

    # 2. Canonicalize split/composite Kannada matra keystrokes
    text = text.replace('\u0CC6\u0CD5', 'ೇ')  # ೆ + ೕ -> ೇ
    text = text.replace('\u0CC6\u0CD6', 'ೈ')  # ೆ + ೖ -> ೈ
    text = text.replace('\u0CCA\u0CD5', 'ೋ')  # ೊ + ೕ -> ೋ
    text = text.replace('\u0CC6\u0CC2', 'ೊ')  # ೆ + ೂ -> ೊ
    text = text.replace('\u0CC6\u0CCC', 'ೌ')  # ೆ + ೌ -> ೌ

    result = []
    n = len(text)

    for i, ch in enumerate(text):
        if ch == '್':  # Kannada Virama / Halant
            # Look ahead: if next character is a consonant, use CONJOINER (U+113D0)
            next_is_consonant = (i + 1 < n and text[i + 1] in KANNADA_CONSONANTS)
            if form_conjuncts and next_is_consonant:
                result.append('\U000113D0')  # Conjoiner creates stacked ligature
            else:
                result.append('\U000113CE')  # Standalone visible virama
        else:
            result.append(KANNADA_TO_TIGALARI.get(ch, ch))

    return ''.join(result)


def tigalari_to_kannada(text: str) -> str:
    """
    Converts Tulu-Tigalari Unicode text back to Kannada script.
    """
    return ''.join(TIGALARI_TO_KANNADA.get(ch, ch) for ch in text)


def inspect_codepoints(text: str) -> List[Tuple[str, str]]:
    """Returns a list of (character, hex_codepoint) pairs."""
    return [(ch, f"U+{ord(ch):04X}") for ch in text]
