"""
Tulu-Tigalari & Kannada Transliteration Package
"""

from .kannada_tigalari import (
    kannada_to_tigalari,
    tigalari_to_kannada,
    inspect_codepoints,
)
from .tulu_phonetic import (
    latin_to_kannada,
    kannada_to_latin,
)
from .transliterator import (
    transliterate,
    detect_script,
    latin_to_tigalari,
    tigalari_to_latin,
)
from .tulu_dictionary import (
    TULU_DICTIONARY,
    lookup_tulu,
)
from .historical_dictionary import (
    HISTORICAL_TULU_CORPUS,
    search_historical_dictionary,
)
from .aatana_library_collector import (
    get_catalog,
    search_books,
    download_book_pdf,
    ocr_pdf_pages,
    process_book_to_corpus,
)
from .tulu_nmt_pipeline import (
    TuluNMTConfig,
    TuluMonolingualProcessor,
    ParallelCorpusBuilder,
    NMTMetrics,
    load_nmt_benchmark_corpus,
)
from .export_datasets_to_csv import export_all_csvs
from .tulu_web_scraper import (
    TuluWikiHarvester,
    WiktionaryTuluHarvester,
    export_harvested_to_csv,
)

__all__ = [
    "kannada_to_tigalari",
    "tigalari_to_kannada",
    "inspect_codepoints",
    "latin_to_kannada",
    "kannada_to_latin",
    "transliterate",
    "detect_script",
    "latin_to_tigalari",
    "tigalari_to_latin",
    "TULU_DICTIONARY",
    "lookup_tulu",
    "HISTORICAL_TULU_CORPUS",
    "search_historical_dictionary",
    "get_catalog",
    "search_books",
    "download_book_pdf",
    "ocr_pdf_pages",
    "process_book_to_corpus",
    "TuluNMTConfig",
    "TuluMonolingualProcessor",
    "ParallelCorpusBuilder",
    "NMTMetrics",
    "load_nmt_benchmark_corpus",
    "export_all_csvs",
    "TuluWikiHarvester",
    "WiktionaryTuluHarvester",
    "export_harvested_to_csv",
]
