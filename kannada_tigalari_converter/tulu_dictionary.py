"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.lexicon.tulu_dictionary"""
try:
    from .lexicon.tulu_dictionary import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.lexicon.tulu_dictionary import *
    except (ImportError, ModuleNotFoundError):
        from lexicon.tulu_dictionary import *

__all__ = ['TULU_DICTIONARY', 'lookup_tulu']
