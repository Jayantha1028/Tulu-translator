"""
NLP & Morphological Engine Submodule
====================================
Contains morphological segmentation, lemmatization, POS tagging,
declension & conjugation paradigms, and NMT parallel corpus processing.
"""

from .tulu_morphology import (
    TuluMorphAnalyzer,
    analyze as morphological_analyze,
    analyze_sentence,
    lemmatize,
    pos_tag,
    decline_noun,
    conjugate_verb,
    export_analysis_to_dicts,
    POS, Case, Tense, Person, Number, Mood,
    MorphAnalysis, DeclensionTable, ConjugationTable,
)
from .tulu_nmt_pipeline import (
    TuluNMTConfig,
    TuluMonolingualProcessor,
    ParallelCorpusBuilder,
    NMTMetrics,
    load_nmt_benchmark_corpus,
)
from .sentence_translator import (
    FullSentenceTranslator,
    TranslationResult,
)
from .neural_translator import (
    NeuralTuluTranslator,
    NeuralTranslationResult,
)

__all__ = [
    "FullSentenceTranslator",
    "TranslationResult",
    "NeuralTuluTranslator",
    "NeuralTranslationResult",
    "TuluMorphAnalyzer",
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
]
