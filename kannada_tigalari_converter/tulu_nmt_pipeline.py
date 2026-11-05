"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.nlp.tulu_nmt_pipeline"""
try:
    from .nlp.tulu_nmt_pipeline import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.nlp.tulu_nmt_pipeline import *
    except (ImportError, ModuleNotFoundError):
        from nlp.tulu_nmt_pipeline import *

__all__ = ['TuluNMTConfig', 'TuluMonolingualProcessor', 'ParallelCorpusBuilder', 'NMTMetrics', 'load_nmt_benchmark_corpus']
