"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.lexicon.words_dataset_250"""
try:
    from .lexicon.words_dataset_250 import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.lexicon.words_dataset_250 import *
    except (ImportError, ModuleNotFoundError):
        from lexicon.words_dataset_250 import *

__all__ = ['WORDS_250_DATASET', 'WORDS_DATASET_250', 'RAW_WORDS_250', 'get_words_by_category', 'get_all_categories']
