"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.scrapers.continuous_scraper"""
try:
    from .scrapers.continuous_scraper import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.scrapers.continuous_scraper import *
    except (ImportError, ModuleNotFoundError):
        from scrapers.continuous_scraper import *

__all__ = ['ContinuousScraper', 'ScraperCheckpoint']
