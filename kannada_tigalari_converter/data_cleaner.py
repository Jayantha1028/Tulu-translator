"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.scrapers.data_cleaner"""
try:
    from .scrapers.data_cleaner import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.scrapers.data_cleaner import *
    except (ImportError, ModuleNotFoundError):
        from scrapers.data_cleaner import *

__all__ = ['DataCleaner', 'DeduplicatedDataset']
