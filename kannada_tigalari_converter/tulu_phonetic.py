"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.core.tulu_phonetic"""
try:
    from .core.tulu_phonetic import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.core.tulu_phonetic import *
    except (ImportError, ModuleNotFoundError):
        from core.tulu_phonetic import *

__all__ = ['latin_to_kannada', 'kannada_to_latin']
