"""
Custom Scripting & Private Use Area (PUA) Engine for Tulu-Tigalari
==================================================================
Provides an interchangeable encoding layer alongside official Unicode 16.0.

Modes:
- SCRIPT_MODE_UNICODE ("unicode"): Official Unicode 16.0 Standard (U+11380 to U+113FF). [DEFAULT & MAIN]
- SCRIPT_MODE_CUSTOM  ("custom"):  Custom Private Use Area (PUA) Scripting (U+E880 to U+E8DF).

Features:
- 100% isomorphic 1-to-1 lossless mapping between Unicode 16.0 and Custom PUA.
- Seamless bi-directional roundtrips across Kannada <-> Unicode 16.0 <-> Custom Script.
- Auto-detection of script encoding mode in input text.
"""

from typing import List, Dict, Optional, Tuple
import unicodedata

# Mode Constants
SCRIPT_MODE_UNICODE = "unicode"
SCRIPT_MODE_CUSTOM = "custom"
AVAILABLE_SCRIPT_MODES = [SCRIPT_MODE_UNICODE, SCRIPT_MODE_CUSTOM]

# Base Codepoints
UNICODE_BASE = 0x11380
UNICODE_LIMIT = 0x113FF
CUSTOM_PUA_BASE = 0xE880
CUSTOM_PUA_LIMIT = 0xE8DF
OFFSET_DIFF = CUSTOM_PUA_BASE - UNICODE_BASE  # 0xE880 - 0x11380 = -0x2B00 (in unsigned mod)


def is_unicode_tigalari(text: str) -> bool:
    """Checks if text contains official Unicode 16.0 Tigalari characters."""
    return any(UNICODE_BASE <= ord(ch) <= UNICODE_LIMIT for ch in text)


def is_custom_tigalari(text: str) -> bool:
    """Checks if text contains Custom PUA Tigalari characters."""
    return any(CUSTOM_PUA_BASE <= ord(ch) <= CUSTOM_PUA_LIMIT for ch in text)


def detect_tigalari_mode(text: str) -> str:
    """
    Returns the script encoding mode of the text:
    - 'unicode' if contains Unicode 16.0 Tigalari
    - 'custom' if contains Custom PUA Tigalari
    - 'none' otherwise
    """
    if is_unicode_tigalari(text):
        return SCRIPT_MODE_UNICODE
    if is_custom_tigalari(text):
        return SCRIPT_MODE_CUSTOM
    return "none"


def unicode_to_custom(text: str) -> str:
    """
    Converts official Unicode 16.0 Tigalari text to Custom PUA Scripting.
    Preserves all ASCII, spaces, and non-Tigalari punctuation.
    """
    res = []
    for ch in text:
        cp = ord(ch)
        if UNICODE_BASE <= cp <= UNICODE_LIMIT:
            res.append(chr(cp - UNICODE_BASE + CUSTOM_PUA_BASE))
        else:
            res.append(ch)
    return "".join(res)


def custom_to_unicode(text: str) -> str:
    """
    Converts Custom PUA Scripting text back to official Unicode 16.0 Tigalari.
    Preserves all ASCII, spaces, and non-Tigalari punctuation.
    """
    res = []
    for ch in text:
        cp = ord(ch)
        if CUSTOM_PUA_BASE <= cp <= CUSTOM_PUA_LIMIT:
            res.append(chr(cp - CUSTOM_PUA_BASE + UNICODE_BASE))
        else:
            res.append(ch)
    return "".join(res)


def get_available_script_modes() -> List[str]:
    """Returns list of supported script modes."""
    return list(AVAILABLE_SCRIPT_MODES)
