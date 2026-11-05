"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.asr.tulu_asr_engine"""
try:
    from .asr.tulu_asr_engine import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.asr.tulu_asr_engine import *
    except (ImportError, ModuleNotFoundError):
        from asr.tulu_asr_engine import *

__all__ = ['TuluSpeechRecognizer', 'TuluASRResult']
