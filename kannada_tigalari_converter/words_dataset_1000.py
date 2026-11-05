"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.lexicon.words_dataset_1000"""
try:
    from .lexicon.words_dataset_1000 import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.lexicon.words_dataset_1000 import *
    except (ImportError, ModuleNotFoundError):
        from lexicon.words_dataset_1000 import *

__all__ = ['WORDS_1000_DATASET', 'WORDS_DATASET_1000', 'RAW_WORDS_1000', 'get_words_by_category', 'get_all_categories']
