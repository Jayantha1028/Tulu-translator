"""
Lexicon, Datasets & Historical Dictionaries Submodule
=====================================================
Contains modern Tulu vocabulary, 1886 Manner historical dictionary,
benchmarked 250 & 1,000 word corpora, and CSV export utilities.
"""

from .tulu_dictionary import (
    TULU_DICTIONARY,
    lookup_tulu,
)
from .historical_dictionary import (
    HISTORICAL_TULU_CORPUS,
    search_historical_dictionary,
)
from .words_dataset_250 import (
    WORDS_DATASET_250,
    WORDS_250_DATASET,
    RAW_WORDS_250,
)
from .words_dataset_1000 import (
    WORDS_DATASET_1000,
    WORDS_1000_DATASET,
    RAW_WORDS_1000,
)
from .export_datasets_to_csv import export_all_csvs

__all__ = [
    "TULU_DICTIONARY",
    "lookup_tulu",
    "HISTORICAL_TULU_CORPUS",
    "search_historical_dictionary",
    "WORDS_DATASET_250",
    "WORDS_250_DATASET",
    "RAW_WORDS_250",
    "WORDS_DATASET_1000",
    "WORDS_1000_DATASET",
    "RAW_WORDS_1000",
    "export_all_csvs",
]
