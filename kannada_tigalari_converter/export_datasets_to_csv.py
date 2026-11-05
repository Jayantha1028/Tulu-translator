"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.lexicon.export_datasets_to_csv"""
try:
    from .lexicon.export_datasets_to_csv import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.lexicon.export_datasets_to_csv import *
    except (ImportError, ModuleNotFoundError):
        from lexicon.export_datasets_to_csv import *

__all__ = ['export_all_csvs']
