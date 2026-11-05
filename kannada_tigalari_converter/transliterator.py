"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.core.transliterator"""
try:
    from .core.transliterator import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.core.transliterator import *
    except (ImportError, ModuleNotFoundError):
        from core.transliterator import *

__all__ = ['transliterate', 'detect_script', 'latin_to_tigalari', 'tigalari_to_latin']
