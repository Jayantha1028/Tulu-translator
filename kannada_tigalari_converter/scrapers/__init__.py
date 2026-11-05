"""
Web Scraping, OCR & Dataset Cleansing Submodule
===============================================
Harvests text from Wikipedia, Wiktionary, and AATA Digital Library PDFs.
Provides persistent continuous scraping and strict deduplication with NFC cleansing.
"""

from .tulu_web_scraper import (
    TuluWikiHarvester,
    WiktionaryTuluHarvester,
    export_harvested_to_csv,
)
from .continuous_scraper import (
    ContinuousScraper,
    ScraperCheckpoint,
)
from .data_cleaner import (
    DataCleaner,
    DeduplicatedDataset,
)
from .aatana_library_collector import (
    get_catalog,
    search_books,
    download_book_pdf,
    ocr_pdf_pages,
    process_book_to_corpus,
)

__all__ = [
    "TuluWikiHarvester",
    "WiktionaryTuluHarvester",
    "export_harvested_to_csv",
    "ContinuousScraper",
    "ScraperCheckpoint",
    "DataCleaner",
    "DeduplicatedDataset",
    "get_catalog",
    "search_books",
    "download_book_pdf",
    "ocr_pdf_pages",
    "process_book_to_corpus",
]
