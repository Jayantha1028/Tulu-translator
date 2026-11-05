"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.asr.tulu_audio_pipeline"""
try:
    from .asr.tulu_audio_pipeline import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.asr.tulu_audio_pipeline import *
    except (ImportError, ModuleNotFoundError):
        from asr.tulu_audio_pipeline import *

__all__ = ['AudioPreprocessor', 'SyntheticTuluAudioGenerator']
