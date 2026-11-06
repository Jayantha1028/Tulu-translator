"""
Tulu-Tigalari & Kannada Transliteration, Morphological Engine, ASR & NMT Suite
=============================================================================
Modular Architecture:
- .core: Script conversion (Kannada <-> Unicode 16.0 Tigalari <-> Latin Baraha)
- .lexicon: Tulu dictionaries, historical 1886 lexicon, 250 & 1,000 word corpora
- .nlp: Morphological parsing, declension, conjugation, and NMT alignment
- .asr: Speech-to-Text inference, 16kHz audio pipeline, Apple Silicon MPS acceleration
- .scrapers: Continuous web harvesters, AATA OCR collector, and NFC data cleaner
"""

# 1. Core Transliteration & Phonetics
from .core import (
    kannada_to_tigalari,
    tigalari_to_kannada,
    inspect_codepoints,
    latin_to_kannada,
    kannada_to_latin,
    transliterate,
    detect_script,
    latin_to_tigalari,
    tigalari_to_latin,
    KANNADA_TO_TIGALARI,
    TIGALARI_TO_KANNADA,
)

# 2. Lexicon & Datasets
from .lexicon import (
    TULU_DICTIONARY,
    lookup_tulu,
    HISTORICAL_TULU_CORPUS,
    search_historical_dictionary,
    WORDS_250_DATASET,
    WORDS_1000_DATASET,
    export_all_csvs,
)

# 3. NLP & Morphology
from .nlp import (
    FullSentenceTranslator,
    TranslationResult,
    morphological_analyze,
    analyze_sentence,
    lemmatize,
    pos_tag,
    decline_noun,
    conjugate_verb,
    export_analysis_to_dicts,
    POS, Case, Tense, Person, Number, Mood,
    MorphAnalysis, DeclensionTable, ConjugationTable,
    TuluNMTConfig,
    TuluMonolingualProcessor,
    ParallelCorpusBuilder,
    NMTMetrics,
    load_nmt_benchmark_corpus,
)

# 4. Speech-to-Text (ASR) Engine
from .asr import (
    AudioPreprocessor,
    SyntheticTuluAudioGenerator,
    TuluSpeechRecognizer,
    TuluASRResult,
    TuluASRTrainer,
    train_tulu_asr,
)

# 5. Scrapers & Data Cleaners
from .scrapers import (
    TuluWikiHarvester,
    WiktionaryTuluHarvester,
    export_harvested_to_csv,
    ContinuousScraper,
    ScraperCheckpoint,
    DataCleaner,
    DeduplicatedDataset,
    get_catalog,
    search_books,
    download_book_pdf,
    ocr_pdf_pages,
    process_book_to_corpus,
)

# 6. Vision, OCR & Handwriting Strokes
from .vision import (
    extract_text_from_image,
    extract_entities_from_text,
    ocr_and_translate_document,
    preprocess_document_image,
    CharacterStrokeRecognizer,
)

# Also expose submodules
from . import core
from . import lexicon
from . import nlp
from . import asr
from . import scrapers
from . import vision

__all__ = [
    # Submodules
    "core",
    "lexicon",
    "nlp",
    "asr",
    "scrapers",
    "vision",
    # Core
    "kannada_to_tigalari",
    "tigalari_to_kannada",
    "inspect_codepoints",
    "latin_to_kannada",
    "kannada_to_latin",
    "transliterate",
    "detect_script",
    "latin_to_tigalari",
    "tigalari_to_latin",
    "KANNADA_TO_TIGALARI",
    "TIGALARI_TO_KANNADA",
    # Lexicon
    "TULU_DICTIONARY",
    "lookup_tulu",
    "HISTORICAL_TULU_CORPUS",
    "search_historical_dictionary",
    "WORDS_250_DATASET",
    "WORDS_1000_DATASET",
    "export_all_csvs",
    # NLP
    "morphological_analyze",
    "analyze_sentence",
    "lemmatize",
    "pos_tag",
    "decline_noun",
    "conjugate_verb",
    "export_analysis_to_dicts",
    "POS",
    "Case",
    "Tense",
    "Person",
    "Number",
    "Mood",
    "MorphAnalysis",
    "DeclensionTable",
    "ConjugationTable",
    "TuluNMTConfig",
    "TuluMonolingualProcessor",
    "ParallelCorpusBuilder",
    "NMTMetrics",
    "load_nmt_benchmark_corpus",
    # ASR
    "AudioPreprocessor",
    "SyntheticTuluAudioGenerator",
    "TuluSpeechRecognizer",
    "TuluASRResult",
    "TuluASRTrainer",
    "train_tulu_asr",
    # Scrapers
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
    # Vision & OCR
    "extract_text_from_image",
    "extract_entities_from_text",
    "ocr_and_translate_document",
    "preprocess_document_image",
    "CharacterStrokeRecognizer",
]
