"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.nlp.tulu_morphology"""
try:
    from .nlp.tulu_morphology import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.nlp.tulu_morphology import *
    except (ImportError, ModuleNotFoundError):
        from nlp.tulu_morphology import *

__all__ = ['analyze', 'analyze_sentence', 'lemmatize', 'pos_tag', 'decline_noun', 'conjugate_verb', 'export_paradigms_to_csv', 'POS', 'Case', 'Tense', 'Person', 'Number', 'Mood', 'MorphAnalysis', 'DeclensionTable', 'ConjugationTable']
