"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.scrapers.tulu_web_scraper"""
try:
    from .scrapers.tulu_web_scraper import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.scrapers.tulu_web_scraper import *
    except (ImportError, ModuleNotFoundError):
        from scrapers.tulu_web_scraper import *

__all__ = ['TuluWikiHarvester', 'WiktionaryTuluHarvester', 'export_harvested_to_csv']
