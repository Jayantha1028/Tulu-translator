"""
Unified Tulu Transliterator Engine
Supports 3 scripts:
  - 'latin': English / Latin script (Phonetic / Baraha / Tulu conventions)
  - 'kannada': Kannada script (ಕನ್ನಡ ಲಿಪಿ)
  - 'tigalari': Tulu-Tigalari script (Unicode 16.0 standard U+11380–U+113FF)
"""

from typing import Tuple, List
from .kannada_tigalari import (
    kannada_to_tigalari,
    tigalari_to_kannada,
    inspect_codepoints,
)
from .tulu_phonetic import (
    latin_to_kannada,
    kannada_to_latin,
)


from .custom_script import (
    SCRIPT_MODE_UNICODE,
    SCRIPT_MODE_CUSTOM,
    is_unicode_tigalari,
    is_custom_tigalari,
    unicode_to_custom,
    custom_to_unicode,
)


def detect_script(text: str) -> str:
    """
    Auto-detects whether the input text is in Tigalari, Custom Tigalari, Kannada, or Latin script.
    """
    for ch in text:
        cp = ord(ch)
        if 0x11380 <= cp <= 0x113FF:
            return 'tigalari'
        if 0xE880 <= cp <= 0xE8DF:
            return 'tigalari_custom'
        if 0x0C80 <= cp <= 0x0CFF:
            return 'kannada'
    return 'latin'


def latin_to_tigalari(text: str, form_conjuncts: bool = True, script_mode: str = "unicode") -> str:
    """
    Converts Latin text to Tulu-Tigalari script via Kannada phonetic mapping.
    
    :param text: Phonetic Latin input string.
    :param form_conjuncts: Use conjoiner for stacked ligatures.
    :param script_mode: "unicode" for Unicode 16.0 standard (default), "custom" for Custom PUA.
    """
    kannada = latin_to_kannada(text)
    return kannada_to_tigalari(kannada, form_conjuncts=form_conjuncts, script_mode=script_mode)


def tigalari_to_latin(text: str) -> str:
    """
    Converts Tulu-Tigalari script (Unicode 16.0 or Custom PUA) to Latin / English phonetic representation.
    """
    kannada = tigalari_to_kannada(text)
    return kannada_to_latin(kannada)


def transliterate(
    text: str,
    from_script: str = 'auto',
    to_script: str = 'tigalari',
    form_conjuncts: bool = True,
    script_mode: str = 'unicode',
) -> str:
    """
    Transliterates text between Latin, Kannada, and Tulu-Tigalari scripts.

    :param text: Input string.
    :param from_script: 'latin', 'kannada', 'tigalari', 'tigalari_custom', or 'auto'.
    :param to_script: 'latin', 'kannada', 'tigalari', or 'tigalari_custom'.
    :param form_conjuncts: Uses Tigalari conjoiner U+113D0 if True.
    :param script_mode: 'unicode' (main standard font, default) or 'custom' (custom PUA scripting).
    :return: Transliterated output string.
    """
    if not text:
        return ""

    src = detect_script(text) if from_script == 'auto' else from_script.lower()
    tgt = to_script.lower()

    if tgt == 'tigalari_custom':
        tgt = 'tigalari'
        script_mode = 'custom'

    if src == tgt and (src != 'tigalari' or script_mode == 'unicode'):
        return text

    if src == 'latin':
        if tgt == 'kannada':
            return latin_to_kannada(text)
        elif tgt == 'tigalari':
            return latin_to_tigalari(text, form_conjuncts=form_conjuncts, script_mode=script_mode)

    elif src == 'kannada':
        if tgt == 'latin':
            return kannada_to_latin(text)
        elif tgt == 'tigalari':
            return kannada_to_tigalari(text, form_conjuncts=form_conjuncts, script_mode=script_mode)

    elif src in ('tigalari', 'tigalari_custom'):
        if tgt == 'kannada':
            return tigalari_to_kannada(text)
        elif tgt == 'latin':
            return tigalari_to_latin(text)
        elif tgt == 'tigalari':
            if script_mode == 'custom' and src == 'tigalari':
                return unicode_to_custom(text)
            elif script_mode == 'unicode' and src == 'tigalari_custom':
                return custom_to_unicode(text)
            return text

    raise ValueError(f"Unsupported transliteration from '{src}' to '{tgt}'")
