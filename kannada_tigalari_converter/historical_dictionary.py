"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.lexicon.historical_dictionary"""
try:
    from .lexicon.historical_dictionary import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.lexicon.historical_dictionary import *
    except (ImportError, ModuleNotFoundError):
        from lexicon.historical_dictionary import *

__all__ = ['HISTORICAL_TULU_CORPUS', 'search_historical_dictionary', 'get_sample_historical_entries']
