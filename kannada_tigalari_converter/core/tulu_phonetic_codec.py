"""
Tulu Custom Phonetic Codec & Discrete Symbol Engine
===================================================
A standalone, zero-dependency discrete phonetic codec that isolates all
model, token, and linguistic processing from Microsoft / OS-level Unicode
complex-text shaping engines (Uniscribe, DirectWrite, OpenType GSUB/GPOS).

Architectural Principle:
1. INPUT BOUNDARY : Ingests Roman ASCII, Kannada, or Unicode 16.0 Tigalari.
2. INTERNAL ENGINE: Converts all phonemes, vowels, consonants, conjuncts, and
                    diacritics into our own atomic, 1-byte discrete integer IDs
                    (TuluCodes: 0 to 255). No multi-byte UTF-8 bloat, no token
                    fragmentation, 100% deterministic math.
3. OUTPUT BOUNDARY: Decodes custom IDs back to official Unicode 16.0 Tigalari,
                    Kannada script, or Roman ASCII strictly for screen display.
"""

from typing import List, Dict, Optional, Union, Tuple, Any
import unicodedata
import numpy as np


class TuluSymbol:
    """Discrete symbol definitions mapped to compact integer IDs (0 - 255)."""
    # Special & Control Tokens (0 - 9)
    PAD = 0
    UNK = 1
    BOS = 2
    EOS = 3
    SPACE = 4
    NEWLINE = 5

    # Independent Vowels (10 - 29)
    VOWEL_A = 10
    VOWEL_AA = 11
    VOWEL_I = 12
    VOWEL_II = 13
    VOWEL_U = 14
    VOWEL_UU = 15
    VOWEL_VOCALIC_R = 16
    VOWEL_VOCALIC_RR = 17
    VOWEL_E = 18
    VOWEL_EE = 19
    VOWEL_AI = 20
    VOWEL_O = 21
    VOWEL_OO = 22
    VOWEL_AU = 23
    VOWEL_TULU_AE = 24       # Tulu unique open-e (Kannada ೆ್ / Baraha 'ae')
    VOWEL_TULU_AAE = 25      # Tulu long open-e

    # Dependent Vowels / Matras (30 - 49)
    MATRA_AA = 30
    MATRA_I = 31
    MATRA_II = 32
    MATRA_U = 33
    MATRA_UU = 34
    MATRA_VOCALIC_R = 35
    MATRA_VOCALIC_RR = 36
    MATRA_E = 37
    MATRA_EE = 38
    MATRA_AI = 39
    MATRA_O = 40
    MATRA_OO = 41
    MATRA_AU = 42
    MATRA_TULU_AE = 43       # Dependent Tulu open-e matra
    MATRA_TULU_AAE = 44

    # Consonants - Pure base consonants without inherent vowel (50 - 99)
    # Velar (ಕ-ವರ್ಗ)
    CONS_K = 50
    CONS_KH = 51
    CONS_G = 52
    CONS_GH = 53
    CONS_NG = 54
    # Palatal (ಚ-ವರ್ಗ)
    CONS_CH = 55
    CONS_CHH = 56
    CONS_J = 57
    CONS_JH = 58
    CONS_NY = 59
    # Retroflex (ಟ-ವರ್ಗ)
    CONS_T_RETRO = 60
    CONS_TH_RETRO = 61
    CONS_D_RETRO = 62
    CONS_DH_RETRO = 63
    CONS_N_RETRO = 64
    # Dental (ತ-ವರ್ಗ)
    CONS_T = 65
    CONS_TH = 66
    CONS_D = 67
    CONS_DH = 68
    CONS_N = 69
    # Labial (ಪ-ವರ್ಗ)
    CONS_P = 70
    CONS_PH = 71
    CONS_B = 72
    CONS_BH = 73
    CONS_M = 74
    # Semivowels, Liquids & Sibilants
    CONS_Y = 75
    CONS_R = 76
    CONS_RR_DRAVIDIAN = 77   # ಱ (Alveolar trill)
    CONS_L = 78
    CONS_L_RETRO = 79        # ಳ (Retroflex lateral)
    CONS_ZH_DRAVIDIAN = 80   # ೞ (Retroflex approximant)
    CONS_V = 81
    CONS_SH_PALATAL = 82     # ಶ
    CONS_SH_RETRO = 83       # ಷ
    CONS_S = 84              # ಸ
    CONS_H = 85              # ಹ

    # Modifiers & Structural Markers (100 - 119)
    ANUSVARA = 100           # ಂ / M
    VISARGA = 101            # ಃ / H
    VIRAMA = 102             # Pure consonant deadener (್ / halant)
    CONJOINER = 103          # Tigalari conjunct stacking conjoiner (U+113D0)
    TULU_HALF_U = 104        # Tulu Half-U / Pu-vowel (KTSA proposed U+113CB, Kannada ು್)

    # Digits (120 - 129)
    DIGIT_0 = 120
    DIGIT_1 = 121
    DIGIT_2 = 122
    DIGIT_3 = 123
    DIGIT_4 = 124
    DIGIT_5 = 125
    DIGIT_6 = 126
    DIGIT_7 = 127
    DIGIT_8 = 128
    DIGIT_9 = 129

    # Common Punctuation (130 - 149)
    PUNCT_PERIOD = 130
    PUNCT_COMMA = 131
    PUNCT_EXCLAMATION = 132
    PUNCT_QUESTION = 133
    PUNCT_COLON = 134
    PUNCT_SEMICOLON = 135
    PUNCT_HYPHEN = 136
    PUNCT_QUOTE_SINGLE = 137
    PUNCT_QUOTE_DOUBLE = 138

    # Additional Numerical Signs (140 - 149, KTSA L2/25-063, L2/25-095)
    NUMBER_10 = 140          # Tulu-Tigalari Number Ten (U+113FA)
    NUMBER_100 = 141         # Tulu-Tigalari Number Hundred (U+113FB)


# Symbolic name lookup table
CODE_TO_NAME: Dict[int, str] = {
    getattr(TuluSymbol, attr): attr
    for attr in dir(TuluSymbol)
    if not attr.startswith("_") and isinstance(getattr(TuluSymbol, attr), int)
}


# ---------------------------------------------------------------------------
# Bidirectional Mappings for Discrete Tulu Codec
# ---------------------------------------------------------------------------

# Kannada char -> Custom ID
KANNADA_TO_CODE: Dict[str, int] = {
    # Independent Vowels
    'ಅ': TuluSymbol.VOWEL_A,
    'ಆ': TuluSymbol.VOWEL_AA,
    'ಇ': TuluSymbol.VOWEL_I,
    'ಈ': TuluSymbol.VOWEL_II,
    'ಉ': TuluSymbol.VOWEL_U,
    'ಊ': TuluSymbol.VOWEL_UU,
    'ಋ': TuluSymbol.VOWEL_VOCALIC_R,
    'ೠ': TuluSymbol.VOWEL_VOCALIC_RR,
    'ಎ': TuluSymbol.VOWEL_E,
    'ಏ': TuluSymbol.VOWEL_EE,
    'ಐ': TuluSymbol.VOWEL_AI,
    'ಒ': TuluSymbol.VOWEL_O,
    'ಓ': TuluSymbol.VOWEL_OO,
    'ಔ': TuluSymbol.VOWEL_AU,
    'ಎ್': TuluSymbol.VOWEL_TULU_AE,

    # Matras
    'ಾ': TuluSymbol.MATRA_AA,
    'ಿ': TuluSymbol.MATRA_I,
    'ೀ': TuluSymbol.MATRA_II,
    'ು': TuluSymbol.MATRA_U,
    'ೂ': TuluSymbol.MATRA_UU,
    'ೃ': TuluSymbol.MATRA_VOCALIC_R,
    'ೄ': TuluSymbol.MATRA_VOCALIC_RR,
    'ೆ': TuluSymbol.MATRA_E,
    'ೇ': TuluSymbol.MATRA_EE,
    'ೈ': TuluSymbol.MATRA_AI,
    'ೊ': TuluSymbol.MATRA_O,
    'ೋ': TuluSymbol.MATRA_OO,
    'ೌ': TuluSymbol.MATRA_AU,
    'ೆ್': TuluSymbol.MATRA_TULU_AE,

    # Consonants
    'ಕ': TuluSymbol.CONS_K,
    'ಖ': TuluSymbol.CONS_KH,
    'ಗ': TuluSymbol.CONS_G,
    'ಘ': TuluSymbol.CONS_GH,
    'ಙ': TuluSymbol.CONS_NG,
    'ಚ': TuluSymbol.CONS_CH,
    'ಛ': TuluSymbol.CONS_CHH,
    'ಜ': TuluSymbol.CONS_J,
    'ಝ': TuluSymbol.CONS_JH,
    'ಞ': TuluSymbol.CONS_NY,
    'ಟ': TuluSymbol.CONS_T_RETRO,
    'ಠ': TuluSymbol.CONS_TH_RETRO,
    'ಡ': TuluSymbol.CONS_D_RETRO,
    'ಢ': TuluSymbol.CONS_DH_RETRO,
    'ಣ': TuluSymbol.CONS_N_RETRO,
    'ತ': TuluSymbol.CONS_T,
    'ಥ': TuluSymbol.CONS_TH,
    'ದ': TuluSymbol.CONS_D,
    'ಧ': TuluSymbol.CONS_DH,
    'ನ': TuluSymbol.CONS_N,
    'ಪ': TuluSymbol.CONS_P,
    'ಫ': TuluSymbol.CONS_PH,
    'ಬ': TuluSymbol.CONS_B,
    'ಭ': TuluSymbol.CONS_BH,
    'ಮ': TuluSymbol.CONS_M,
    'ಯ': TuluSymbol.CONS_Y,
    'ರ': TuluSymbol.CONS_R,
    'ಱ': TuluSymbol.CONS_RR_DRAVIDIAN,
    'ಲ': TuluSymbol.CONS_L,
    'ಳ': TuluSymbol.CONS_L_RETRO,
    'ೞ': TuluSymbol.CONS_ZH_DRAVIDIAN,
    'ವ': TuluSymbol.CONS_V,
    'ಶ': TuluSymbol.CONS_SH_PALATAL,
    'ಷ': TuluSymbol.CONS_SH_RETRO,
    'ಸ': TuluSymbol.CONS_S,
    'ಹ': TuluSymbol.CONS_H,

    # Signs
    'ಂ': TuluSymbol.ANUSVARA,
    'ಃ': TuluSymbol.VISARGA,
    '್': TuluSymbol.VIRAMA,
    'ು್': TuluSymbol.TULU_HALF_U,  # Tulu Half-U / Pu-vowel (KTSA U+113CB)

    # Digits
    '0': TuluSymbol.DIGIT_0, '1': TuluSymbol.DIGIT_1, '2': TuluSymbol.DIGIT_2,
    '3': TuluSymbol.DIGIT_3, '4': TuluSymbol.DIGIT_4, '5': TuluSymbol.DIGIT_5,
    '6': TuluSymbol.DIGIT_6, '7': TuluSymbol.DIGIT_7, '8': TuluSymbol.DIGIT_8,
    '9': TuluSymbol.DIGIT_9,
    '೦': TuluSymbol.DIGIT_0, '೧': TuluSymbol.DIGIT_1, '೨': TuluSymbol.DIGIT_2,
    '೩': TuluSymbol.DIGIT_3, '೪': TuluSymbol.DIGIT_4, '೫': TuluSymbol.DIGIT_5,
    '೬': TuluSymbol.DIGIT_6, '೭': TuluSymbol.DIGIT_7, '೮': TuluSymbol.DIGIT_8,
    '೯': TuluSymbol.DIGIT_9,

    # Punctuation
    '.': TuluSymbol.PUNCT_PERIOD,
    ',': TuluSymbol.PUNCT_COMMA,
    '!': TuluSymbol.PUNCT_EXCLAMATION,
    '?': TuluSymbol.PUNCT_QUESTION,
    ':': TuluSymbol.PUNCT_COLON,
    ';': TuluSymbol.PUNCT_SEMICOLON,
    '-': TuluSymbol.PUNCT_HYPHEN,
    "'": TuluSymbol.PUNCT_QUOTE_SINGLE,
    '"': TuluSymbol.PUNCT_QUOTE_DOUBLE,
    ' ': TuluSymbol.SPACE,
    '\n': TuluSymbol.NEWLINE,
}

# Unicode 16.0 Tigalari char -> Custom ID
TIGALARI_TO_CODE: Dict[str, int] = {
    # Independent Vowels
    '\U00011380': TuluSymbol.VOWEL_A,
    '\U00011381': TuluSymbol.VOWEL_AA,
    '\U00011382': TuluSymbol.VOWEL_I,
    '\U00011383': TuluSymbol.VOWEL_II,
    '\U00011384': TuluSymbol.VOWEL_U,
    '\U00011385': TuluSymbol.VOWEL_UU,
    '\U00011386': TuluSymbol.VOWEL_VOCALIC_R,
    '\U00011387': TuluSymbol.VOWEL_VOCALIC_RR,
    '\U0001138A': TuluSymbol.VOWEL_E,
    '\U0001138B': TuluSymbol.VOWEL_EE,
    '\U0001138E': TuluSymbol.VOWEL_AI,
    '\U0001138F': TuluSymbol.VOWEL_O,
    '\U00011390': TuluSymbol.VOWEL_OO,
    '\U00011391': TuluSymbol.VOWEL_AU,

    # Dependent Vowels / Matras
    '\U000113B8': TuluSymbol.MATRA_AA,
    '\U000113B9': TuluSymbol.MATRA_I,
    '\U000113BA': TuluSymbol.MATRA_II,
    '\U000113BB': TuluSymbol.MATRA_U,
    '\U000113BC': TuluSymbol.MATRA_UU,
    '\U000113BD': TuluSymbol.MATRA_VOCALIC_R,
    '\U000113BE': TuluSymbol.MATRA_VOCALIC_RR,
    '\U000113C0': TuluSymbol.MATRA_E,
    '\U000113C1': TuluSymbol.MATRA_EE,
    '\U000113C2': TuluSymbol.MATRA_AI,
    '\U000113C5': TuluSymbol.MATRA_O,
    '\U000113C6': TuluSymbol.MATRA_OO,
    '\U000113C7': TuluSymbol.MATRA_AU,

    # Consonants
    '\U00011392': TuluSymbol.CONS_K,
    '\U00011393': TuluSymbol.CONS_KH,
    '\U00011394': TuluSymbol.CONS_G,
    '\U00011395': TuluSymbol.CONS_GH,
    '\U00011396': TuluSymbol.CONS_NG,
    '\U00011397': TuluSymbol.CONS_CH,
    '\U00011398': TuluSymbol.CONS_CHH,
    '\U00011399': TuluSymbol.CONS_J,
    '\U0001139A': TuluSymbol.CONS_JH,
    '\U0001139B': TuluSymbol.CONS_NY,
    '\U0001139C': TuluSymbol.CONS_T_RETRO,
    '\U0001139D': TuluSymbol.CONS_TH_RETRO,
    '\U0001139E': TuluSymbol.CONS_D_RETRO,
    '\U0001139F': TuluSymbol.CONS_DH_RETRO,
    '\U000113A0': TuluSymbol.CONS_N_RETRO,
    '\U000113A1': TuluSymbol.CONS_T,
    '\U000113A2': TuluSymbol.CONS_TH,
    '\U000113A3': TuluSymbol.CONS_D,
    '\U000113A4': TuluSymbol.CONS_DH,
    '\U000113A5': TuluSymbol.CONS_N,
    '\U000113A6': TuluSymbol.CONS_P,
    '\U000113A7': TuluSymbol.CONS_PH,
    '\U000113A8': TuluSymbol.CONS_B,
    '\U000113A9': TuluSymbol.CONS_BH,
    '\U000113AA': TuluSymbol.CONS_M,
    '\U000113AB': TuluSymbol.CONS_Y,
    '\U000113AC': TuluSymbol.CONS_R,
    '\U000113B4': TuluSymbol.CONS_RR_DRAVIDIAN,
    '\U000113AD': TuluSymbol.CONS_L,
    '\U000113B3': TuluSymbol.CONS_L_RETRO,
    '\U000113AE': TuluSymbol.CONS_V,
    '\U000113AF': TuluSymbol.CONS_SH_PALATAL,
    '\U000113B0': TuluSymbol.CONS_SH_RETRO,
    '\U000113B1': TuluSymbol.CONS_S,
    '\U000113B2': TuluSymbol.CONS_H,

    # Signs
    '\U000113B7': TuluSymbol.ANUSVARA,
    '\U000113C9': TuluSymbol.VISARGA,
    '\U000113CE': TuluSymbol.VIRAMA,
    '\U000113D0': TuluSymbol.CONJOINER,
    '\U000113CB': TuluSymbol.TULU_HALF_U,  # KTSA U+113CB Tulu Half-U sign

    # Numerals (KTSA U+113F0 - U+113FB)
    '\U000113F0': TuluSymbol.DIGIT_0,
    '\U000113F1': TuluSymbol.DIGIT_1,
    '\U000113F2': TuluSymbol.DIGIT_2,
    '\U000113F3': TuluSymbol.DIGIT_3,
    '\U000113F4': TuluSymbol.DIGIT_4,
    '\U000113F5': TuluSymbol.DIGIT_5,
    '\U000113F6': TuluSymbol.DIGIT_6,
    '\U000113F7': TuluSymbol.DIGIT_7,
    '\U000113F8': TuluSymbol.DIGIT_8,
    '\U000113F9': TuluSymbol.DIGIT_9,
    '\U000113FA': TuluSymbol.NUMBER_10,
    '\U000113FB': TuluSymbol.NUMBER_100,
    ' ': TuluSymbol.SPACE,
    '\n': TuluSymbol.NEWLINE,
}

# Reverse Code -> Native Scripts for screen display
CODE_TO_KANNADA: Dict[int, str] = {
    # Independent Vowels
    TuluSymbol.VOWEL_A: 'ಅ',
    TuluSymbol.VOWEL_AA: 'ಆ',
    TuluSymbol.VOWEL_I: 'ಇ',
    TuluSymbol.VOWEL_II: 'ಈ',
    TuluSymbol.VOWEL_U: 'ಉ',
    TuluSymbol.VOWEL_UU: 'ಊ',
    TuluSymbol.VOWEL_VOCALIC_R: 'ಋ',
    TuluSymbol.VOWEL_VOCALIC_RR: 'ೠ',
    TuluSymbol.VOWEL_E: 'ಎ',
    TuluSymbol.VOWEL_EE: 'ಏ',
    TuluSymbol.VOWEL_AI: 'ಐ',
    TuluSymbol.VOWEL_O: 'ಒ',
    TuluSymbol.VOWEL_OO: 'ಓ',
    TuluSymbol.VOWEL_AU: 'ಔ',
    TuluSymbol.VOWEL_TULU_AE: 'ಎ್',
    TuluSymbol.VOWEL_TULU_AAE: 'ಆೆ್',

    # Matras
    TuluSymbol.MATRA_AA: 'ಾ',
    TuluSymbol.MATRA_I: 'ಿ',
    TuluSymbol.MATRA_II: 'ೀ',
    TuluSymbol.MATRA_U: 'ು',
    TuluSymbol.MATRA_UU: 'ೂ',
    TuluSymbol.MATRA_VOCALIC_R: 'ೃ',
    TuluSymbol.MATRA_VOCALIC_RR: 'ೄ',
    TuluSymbol.MATRA_E: 'ೆ',
    TuluSymbol.MATRA_EE: 'ೇ',
    TuluSymbol.MATRA_AI: 'ೈ',
    TuluSymbol.MATRA_O: 'ೊ',
    TuluSymbol.MATRA_OO: 'ೋ',
    TuluSymbol.MATRA_AU: 'ೌ',
    TuluSymbol.MATRA_TULU_AE: 'ೆ್',
    TuluSymbol.MATRA_TULU_AAE: 'ಾೆ್',

    # Consonants
    TuluSymbol.CONS_K: 'ಕ',
    TuluSymbol.CONS_KH: 'ಖ',
    TuluSymbol.CONS_G: 'ಗ',
    TuluSymbol.CONS_GH: 'ಘ',
    TuluSymbol.CONS_NG: 'ಙ',
    TuluSymbol.CONS_CH: 'ಚ',
    TuluSymbol.CONS_CHH: 'ಛ',
    TuluSymbol.CONS_J: 'ಜ',
    TuluSymbol.CONS_JH: 'ಝ',
    TuluSymbol.CONS_NY: 'ಞ',
    TuluSymbol.CONS_T_RETRO: 'ಟ',
    TuluSymbol.CONS_TH_RETRO: 'ಠ',
    TuluSymbol.CONS_D_RETRO: 'ಡ',
    TuluSymbol.CONS_DH_RETRO: 'ಢ',
    TuluSymbol.CONS_N_RETRO: 'ಣ',
    TuluSymbol.CONS_T: 'ತ',
    TuluSymbol.CONS_TH: 'ಥ',
    TuluSymbol.CONS_D: 'ದ',
    TuluSymbol.CONS_DH: 'ಧ',
    TuluSymbol.CONS_N: 'ನ',
    TuluSymbol.CONS_P: 'ಪ',
    TuluSymbol.CONS_PH: 'ಫ',
    TuluSymbol.CONS_B: 'ಬ',
    TuluSymbol.CONS_BH: 'ಭ',
    TuluSymbol.CONS_M: 'ಮ',
    TuluSymbol.CONS_Y: 'ಯ',
    TuluSymbol.CONS_R: 'ರ',
    TuluSymbol.CONS_RR_DRAVIDIAN: 'ಱ',
    TuluSymbol.CONS_L: 'ಲ',
    TuluSymbol.CONS_L_RETRO: 'ಳ',
    TuluSymbol.CONS_ZH_DRAVIDIAN: 'ೞ',
    TuluSymbol.CONS_V: 'ವ',
    TuluSymbol.CONS_SH_PALATAL: 'ಶ',
    TuluSymbol.CONS_SH_RETRO: 'ಷ',
    TuluSymbol.CONS_S: 'ಸ',
    TuluSymbol.CONS_H: 'ಹ',

    # Modifiers
    TuluSymbol.ANUSVARA: 'ಂ',
    TuluSymbol.VISARGA: 'ಃ',
    TuluSymbol.VIRAMA: '್',
    TuluSymbol.CONJOINER: '್',  # Maps to virama in Kannada script
    TuluSymbol.TULU_HALF_U: 'ು್',  # Tulu Half-U / Pu-vowel (KTSA U+113CB)
    TuluSymbol.NUMBER_10: '೧೦',
    TuluSymbol.NUMBER_100: '೧೦೦',

    # Space & Punctuation
    TuluSymbol.SPACE: ' ',
    TuluSymbol.NEWLINE: '\n',
    TuluSymbol.PUNCT_PERIOD: '.',
    TuluSymbol.PUNCT_COMMA: ',',
    TuluSymbol.PUNCT_EXCLAMATION: '!',
    TuluSymbol.PUNCT_QUESTION: '?',
    TuluSymbol.PUNCT_COLON: ':',
    TuluSymbol.PUNCT_SEMICOLON: ';',
    TuluSymbol.PUNCT_HYPHEN: '-',
    TuluSymbol.PUNCT_QUOTE_SINGLE: "'",
    TuluSymbol.PUNCT_QUOTE_DOUBLE: '"',
    TuluSymbol.DIGIT_0: '0', TuluSymbol.DIGIT_1: '1', TuluSymbol.DIGIT_2: '2',
    TuluSymbol.DIGIT_3: '3', TuluSymbol.DIGIT_4: '4', TuluSymbol.DIGIT_5: '5',
    TuluSymbol.DIGIT_6: '6', TuluSymbol.DIGIT_7: '7', TuluSymbol.DIGIT_8: '8',
    TuluSymbol.DIGIT_9: '9',
}

CODE_TO_TIGALARI: Dict[int, str] = {
    # Independent Vowels
    TuluSymbol.VOWEL_A: '\U00011380',
    TuluSymbol.VOWEL_AA: '\U00011381',
    TuluSymbol.VOWEL_I: '\U00011382',
    TuluSymbol.VOWEL_II: '\U00011383',
    TuluSymbol.VOWEL_U: '\U00011384',
    TuluSymbol.VOWEL_UU: '\U00011385',
    TuluSymbol.VOWEL_VOCALIC_R: '\U00011386',
    TuluSymbol.VOWEL_VOCALIC_RR: '\U00011387',
    TuluSymbol.VOWEL_E: '\U0001138A',
    TuluSymbol.VOWEL_EE: '\U0001138B',
    TuluSymbol.VOWEL_AI: '\U0001138E',
    TuluSymbol.VOWEL_O: '\U0001138F',
    TuluSymbol.VOWEL_OO: '\U00011390',
    TuluSymbol.VOWEL_AU: '\U00011391',
    TuluSymbol.VOWEL_TULU_AE: '\U0001138A\U000113CE',
    TuluSymbol.VOWEL_TULU_AAE: '\U00011381\U000113C1\U000113CE',

    # Matras
    TuluSymbol.MATRA_AA: '\U000113B8',
    TuluSymbol.MATRA_I: '\U000113B9',
    TuluSymbol.MATRA_II: '\U000113BA',
    TuluSymbol.MATRA_U: '\U000113BB',
    TuluSymbol.MATRA_UU: '\U000113BC',
    TuluSymbol.MATRA_VOCALIC_R: '\U000113BD',
    TuluSymbol.MATRA_VOCALIC_RR: '\U000113BE',
    TuluSymbol.MATRA_E: '\U000113C0',
    TuluSymbol.MATRA_EE: '\U000113C1',
    TuluSymbol.MATRA_AI: '\U000113C2',
    TuluSymbol.MATRA_O: '\U000113C5',
    TuluSymbol.MATRA_OO: '\U000113C6',
    TuluSymbol.MATRA_AU: '\U000113C7',
    TuluSymbol.MATRA_TULU_AE: '\U000113C1\U000113CE',
    TuluSymbol.MATRA_TULU_AAE: '\U000113B8\U000113C1\U000113CE',

    # Consonants
    TuluSymbol.CONS_K: '\U00011392',
    TuluSymbol.CONS_KH: '\U00011393',
    TuluSymbol.CONS_G: '\U00011394',
    TuluSymbol.CONS_GH: '\U00011395',
    TuluSymbol.CONS_NG: '\U00011396',
    TuluSymbol.CONS_CH: '\U00011397',
    TuluSymbol.CONS_CHH: '\U00011398',
    TuluSymbol.CONS_J: '\U00011399',
    TuluSymbol.CONS_JH: '\U0001139A',
    TuluSymbol.CONS_NY: '\U0001139B',
    TuluSymbol.CONS_T_RETRO: '\U0001139C',
    TuluSymbol.CONS_TH_RETRO: '\U0001139D',
    TuluSymbol.CONS_D_RETRO: '\U0001139E',
    TuluSymbol.CONS_DH_RETRO: '\U0001139F',
    TuluSymbol.CONS_N_RETRO: '\U000113A0',
    TuluSymbol.CONS_T: '\U000113A1',
    TuluSymbol.CONS_TH: '\U000113A2',
    TuluSymbol.CONS_D: '\U000113A3',
    TuluSymbol.CONS_DH: '\U000113A4',
    TuluSymbol.CONS_N: '\U000113A5',
    TuluSymbol.CONS_P: '\U000113A6',
    TuluSymbol.CONS_PH: '\U000113A7',
    TuluSymbol.CONS_B: '\U000113A8',
    TuluSymbol.CONS_BH: '\U000113A9',
    TuluSymbol.CONS_M: '\U000113AA',
    TuluSymbol.CONS_Y: '\U000113AB',
    TuluSymbol.CONS_R: '\U000113AC',
    TuluSymbol.CONS_RR_DRAVIDIAN: '\U000113B4',
    TuluSymbol.CONS_L: '\U000113AD',
    TuluSymbol.CONS_L_RETRO: '\U000113B3',
    TuluSymbol.CONS_ZH_DRAVIDIAN: '\U000113B4',
    TuluSymbol.CONS_V: '\U000113AE',
    TuluSymbol.CONS_SH_PALATAL: '\U000113AF',
    TuluSymbol.CONS_SH_RETRO: '\U000113B0',
    TuluSymbol.CONS_S: '\U000113B1',
    TuluSymbol.CONS_H: '\U000113B2',

    # Modifiers & KTSA Extensions
    TuluSymbol.ANUSVARA: '\U000113B7',
    TuluSymbol.VISARGA: '\U000113C9',
    TuluSymbol.VIRAMA: '\U000113CE',
    TuluSymbol.CONJOINER: '\U000113D0',
    TuluSymbol.TULU_HALF_U: '\U000113CB',  # KTSA U+113CB Tulu Half-U sign

    # Space & Punctuation
    TuluSymbol.SPACE: ' ',
    TuluSymbol.NEWLINE: '\n',
    TuluSymbol.PUNCT_PERIOD: '.',
    TuluSymbol.PUNCT_COMMA: ',',
    TuluSymbol.PUNCT_EXCLAMATION: '!',
    TuluSymbol.PUNCT_QUESTION: '?',
    TuluSymbol.PUNCT_COLON: ':',
    TuluSymbol.PUNCT_SEMICOLON: ';',
    TuluSymbol.PUNCT_HYPHEN: '-',
    TuluSymbol.PUNCT_QUOTE_SINGLE: "'",
    TuluSymbol.PUNCT_QUOTE_DOUBLE: '"',
    TuluSymbol.DIGIT_0: '\U000113F0', TuluSymbol.DIGIT_1: '\U000113F1', TuluSymbol.DIGIT_2: '\U000113F2',
    TuluSymbol.DIGIT_3: '\U000113F3', TuluSymbol.DIGIT_4: '\U000113F4', TuluSymbol.DIGIT_5: '\U000113F5',
    TuluSymbol.DIGIT_6: '\U000113F6', TuluSymbol.DIGIT_7: '\U000113F7', TuluSymbol.DIGIT_8: '\U000113F8',
    TuluSymbol.DIGIT_9: '\U000113F9',
    TuluSymbol.NUMBER_10: '\U000113FA',
    TuluSymbol.NUMBER_100: '\U000113FB',
}

# Canonical Roman representation for internal debugging / ASCII rendering
CODE_TO_ROMAN: Dict[int, str] = {
    TuluSymbol.VOWEL_A: 'a', TuluSymbol.VOWEL_AA: 'aa',
    TuluSymbol.VOWEL_I: 'i', TuluSymbol.VOWEL_II: 'ee',
    TuluSymbol.VOWEL_U: 'u', TuluSymbol.VOWEL_UU: 'oo',
    TuluSymbol.VOWEL_VOCALIC_R: 'Ru', TuluSymbol.VOWEL_VOCALIC_RR: 'RU',
    TuluSymbol.VOWEL_E: 'e', TuluSymbol.VOWEL_EE: 'E',
    TuluSymbol.VOWEL_AI: 'ai', TuluSymbol.VOWEL_O: 'o',
    TuluSymbol.VOWEL_OO: 'O', TuluSymbol.VOWEL_AU: 'au',
    TuluSymbol.VOWEL_TULU_AE: 'ae', TuluSymbol.VOWEL_TULU_AAE: 'aae',

    TuluSymbol.MATRA_AA: 'aa', TuluSymbol.MATRA_I: 'i',
    TuluSymbol.MATRA_II: 'ee', TuluSymbol.MATRA_U: 'u',
    TuluSymbol.MATRA_UU: 'oo', TuluSymbol.MATRA_VOCALIC_R: 'Ru',
    TuluSymbol.MATRA_VOCALIC_RR: 'RU', TuluSymbol.MATRA_E: 'e',
    TuluSymbol.MATRA_EE: 'E', TuluSymbol.MATRA_AI: 'ai',
    TuluSymbol.MATRA_O: 'o', TuluSymbol.MATRA_OO: 'O',
    TuluSymbol.MATRA_AU: 'au', TuluSymbol.MATRA_TULU_AE: 'ae',
    TuluSymbol.MATRA_TULU_AAE: 'aae',

    TuluSymbol.CONS_K: 'k', TuluSymbol.CONS_KH: 'kh',
    TuluSymbol.CONS_G: 'g', TuluSymbol.CONS_GH: 'gh',
    TuluSymbol.CONS_NG: 'ng', TuluSymbol.CONS_CH: 'ch',
    TuluSymbol.CONS_CHH: 'Ch', TuluSymbol.CONS_J: 'j',
    TuluSymbol.CONS_JH: 'jh', TuluSymbol.CONS_NY: 'nj',
    TuluSymbol.CONS_T_RETRO: 'T', TuluSymbol.CONS_TH_RETRO: 'Th',
    TuluSymbol.CONS_D_RETRO: 'D', TuluSymbol.CONS_DH_RETRO: 'Dh',
    TuluSymbol.CONS_N_RETRO: 'N', TuluSymbol.CONS_T: 't',
    TuluSymbol.CONS_TH: 'th', TuluSymbol.CONS_D: 'd',
    TuluSymbol.CONS_DH: 'dh', TuluSymbol.CONS_N: 'n',
    TuluSymbol.CONS_P: 'p', TuluSymbol.CONS_PH: 'ph',
    TuluSymbol.CONS_B: 'b', TuluSymbol.CONS_BH: 'bh',
    TuluSymbol.CONS_M: 'm', TuluSymbol.CONS_Y: 'y',
    TuluSymbol.CONS_R: 'r', TuluSymbol.CONS_RR_DRAVIDIAN: 'rr',
    TuluSymbol.CONS_L: 'l', TuluSymbol.CONS_L_RETRO: 'L',
    TuluSymbol.CONS_ZH_DRAVIDIAN: 'zh', TuluSymbol.CONS_V: 'v',
    TuluSymbol.CONS_SH_PALATAL: 'sh', TuluSymbol.CONS_SH_RETRO: 'Sh',
    TuluSymbol.CONS_S: 's', TuluSymbol.CONS_H: 'h',

    TuluSymbol.ANUSVARA: 'M', TuluSymbol.VISARGA: 'H',
    TuluSymbol.VIRAMA: '', TuluSymbol.CONJOINER: '',
    TuluSymbol.TULU_HALF_U: 'u*',
    TuluSymbol.SPACE: ' ', TuluSymbol.NEWLINE: '\n',
    TuluSymbol.PUNCT_PERIOD: '.', TuluSymbol.PUNCT_COMMA: ',',
    TuluSymbol.PUNCT_EXCLAMATION: '!', TuluSymbol.PUNCT_QUESTION: '?',
    TuluSymbol.PUNCT_COLON: ':', TuluSymbol.PUNCT_SEMICOLON: ';',
    TuluSymbol.PUNCT_HYPHEN: '-', TuluSymbol.PUNCT_QUOTE_SINGLE: "'",
    TuluSymbol.PUNCT_QUOTE_DOUBLE: '"',
    TuluSymbol.DIGIT_0: '0', TuluSymbol.DIGIT_1: '1', TuluSymbol.DIGIT_2: '2',
    TuluSymbol.DIGIT_3: '3', TuluSymbol.DIGIT_4: '4', TuluSymbol.DIGIT_5: '5',
    TuluSymbol.DIGIT_6: '6', TuluSymbol.DIGIT_7: '7', TuluSymbol.DIGIT_8: '8',
    TuluSymbol.DIGIT_9: '9',
    TuluSymbol.NUMBER_10: '10',
    TuluSymbol.NUMBER_100: '100',
}


class TuluPhoneticCodec:
    """
    Unified Discrete Phonetic Codec.
    Enables zero-dependency, isolated token operations for Tulu.
    """

    @classmethod
    def encode(cls, text: str) -> List[int]:
        """
        Converts any input string (Kannada, Unicode 16.0 Tigalari, or Romanized ASCII)
        into an atomic sequence of discrete custom integer IDs (0 to 255).
        """
        if not text:
            return []

        # Detect input type: Tigalari, Kannada, or Roman
        has_tigalari = any(0x11380 <= ord(c) <= 0x113FF for c in text)
        has_kannada = any(0x0C80 <= ord(c) <= 0x0CFF for c in text)

        if has_tigalari:
            return cls._encode_tigalari(text)
        elif has_kannada:
            return cls._encode_kannada(text)
        else:
            return cls._encode_roman(text)

    @classmethod
    def _encode_kannada(cls, text: str) -> List[int]:
        codes = []
        i = 0
        n = len(text)
        while i < n:
            # Check 2-char combinations (Tulu open-e diacritics: ೆ್ or ಎ್)
            if i + 1 < n:
                two_char = text[i:i+2]
                if two_char in KANNADA_TO_CODE:
                    codes.append(KANNADA_TO_CODE[two_char])
                    i += 2
                    continue

            ch = text[i]
            if ch in KANNADA_TO_CODE:
                codes.append(KANNADA_TO_CODE[ch])
            elif ch == ' ':
                codes.append(TuluSymbol.SPACE)
            elif ch == '\n':
                codes.append(TuluSymbol.NEWLINE)
            elif ch.isascii() and ch in KANNADA_TO_CODE:
                codes.append(KANNADA_TO_CODE[ch])
            else:
                codes.append(TuluSymbol.UNK)
            i += 1
        return codes

    @classmethod
    def _encode_tigalari(cls, text: str) -> List[int]:
        codes = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch in TIGALARI_TO_CODE:
                codes.append(TIGALARI_TO_CODE[ch])
            elif ch in KANNADA_TO_CODE:
                codes.append(KANNADA_TO_CODE[ch])
            elif ch == ' ':
                codes.append(TuluSymbol.SPACE)
            elif ch == '\n':
                codes.append(TuluSymbol.NEWLINE)
            else:
                codes.append(TuluSymbol.UNK)
            i += 1
        return codes

    @classmethod
    def _encode_roman(cls, text: str) -> List[int]:
        """
        Encodes Roman phonetic ASCII (e.g. 'yaan illag barpe' or 'kODae') into custom IDs.
        """
        from kannada_tigalari_converter.lexicon.romanization_scheme import from_canonical_roman
        # Convert Roman to Kannada orthography first, then to discrete codes
        kn = from_canonical_roman(text, to_script="kannada")
        return cls._encode_kannada(kn)

    @classmethod
    def decode(cls, codes: Union[List[int], bytes, np.ndarray], target_format: str = "kannada") -> str:
        """
        Decodes a sequence of custom discrete IDs into human-readable target script.
        :param codes: List of integer IDs, bytes, or numpy array.
        :param target_format: 'kannada' (default), 'tigalari', 'roman', or 'ascii'.
        :return: Formatted text string.
        """
        if isinstance(codes, bytes):
            codes = list(codes)
        elif isinstance(codes, np.ndarray):
            codes = codes.tolist()

        target_format = target_format.lower().strip()

        if target_format in ("tigalari", "tulu", "tulu_tigalari"):
            return cls._decode_to_tigalari(codes)
        elif target_format in ("roman", "latin", "ascii"):
            return cls._decode_to_roman(codes)
        else:
            return cls._decode_to_kannada(codes)

    @classmethod
    def _decode_to_kannada(cls, codes: List[int]) -> str:
        out = []
        for code in codes:
            if code in CODE_TO_KANNADA:
                out.append(CODE_TO_KANNADA[code])
        return "".join(out)

    @classmethod
    def _decode_to_tigalari(cls, codes: List[int]) -> str:
        out = []
        i = 0
        n = len(codes)
        while i < n:
            c = codes[i]
            # Handle virama + consonant conjunct stacking for Tigalari (use U+113D0 conjoiner if following consonant)
            if c == TuluSymbol.VIRAMA and i + 1 < n:
                next_c = codes[i+1]
                if 50 <= next_c <= 85:  # Following consonant
                    out.append(CODE_TO_TIGALARI[TuluSymbol.CONJOINER])
                    i += 1
                    continue

            if c in CODE_TO_TIGALARI:
                out.append(CODE_TO_TIGALARI[c])
            elif c in CODE_TO_KANNADA:
                out.append(CODE_TO_KANNADA[c])
            i += 1
        return "".join(out)

    @classmethod
    def _decode_to_roman(cls, codes: List[int]) -> str:
        out = []
        for code in codes:
            if code in CODE_TO_ROMAN:
                out.append(CODE_TO_ROMAN[code])
        return "".join(out)

    @classmethod
    def to_bytes(cls, codes: List[int]) -> bytes:
        """Serializes custom IDs to a compact binary byte array (1 byte per symbol)."""
        return bytes([c & 0xFF for c in codes])

    @classmethod
    def from_bytes(cls, data: bytes) -> List[int]:
        """Deserializes compact binary bytes back to custom integer IDs."""
        return list(data)

    @classmethod
    def compression_ratio(cls, text: str) -> float:
        """
        Measures compression advantage of custom IDs vs standard UTF-8 multi-byte encoding.
        Ratio > 1.0 means custom codec uses fewer bytes than standard UTF-8.
        """
        utf8_bytes = len(text.encode("utf-8"))
        custom_ids = len(cls.encode(text))
        if custom_ids == 0:
            return 1.0
        return round(utf8_bytes / custom_ids, 2)


# Convenience top-level functions
def encode_to_custom_code(text: str) -> List[int]:
    """Encodes any text into our custom atomic discrete integer IDs."""
    return TuluPhoneticCodec.encode(text)


def decode_from_custom_code(codes: Union[List[int], bytes, np.ndarray], target_format: str = "kannada") -> str:
    """Decodes custom discrete integer IDs into human-readable target format."""
    return TuluPhoneticCodec.decode(codes, target_format=target_format)
