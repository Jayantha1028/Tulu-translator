"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.scrapers.aatana_library_collector"""
try:
    from .scrapers.aatana_library_collector import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.scrapers.aatana_library_collector import *
    except (ImportError, ModuleNotFoundError):
        from scrapers.aatana_library_collector import *

__all__ = ['get_catalog', 'search_books', 'download_book_pdf', 'ocr_pdf_pages', 'process_book_to_corpus']
