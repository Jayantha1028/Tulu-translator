"""Backward-compatible re-export shim. Canonical location: kannada_tigalari_converter.core.kannada_tigalari"""
try:
    from .core.kannada_tigalari import *
except (ImportError, ValueError):
    try:
        from kannada_tigalari_converter.core.kannada_tigalari import *
    except (ImportError, ModuleNotFoundError):
        from core.kannada_tigalari import *

__all__ = ['KANNADA_TO_TIGALARI', 'TIGALARI_TO_KANNADA', 'kannada_to_tigalari', 'tigalari_to_kannada', 'inspect_codepoints']
