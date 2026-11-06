"""
Vision & OCR Submodule
======================
Handles document/image text extraction (OCR), cultural entity recognition,
Tulu-Tigalari manuscript pipeline, and handwriting stroke recognition.
"""

from .tulu_ocr_service import (
    extract_text_from_image,
    extract_entities_from_text,
    ocr_and_translate_document,
    preprocess_document_image,
    load_image,
)
from .stroke_recognizer import (
    CharacterStrokeRecognizer,
)

__all__ = [
    "extract_text_from_image",
    "extract_entities_from_text",
    "ocr_and_translate_document",
    "preprocess_document_image",
    "load_image",
    "CharacterStrokeRecognizer",
]
