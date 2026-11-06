"""
kannada_tigalari_converter.vision.tulu_ocr_service
==================================================
Optical Character Recognition (OCR), manuscript & document image preprocessing,
historical inscription entity extraction, and automatic Tulu-Tigalari translation pipeline.
"""

from __future__ import annotations

import base64
import io
import re
from typing import Any, Dict, List, Optional, Union
from PIL import Image, ImageEnhance, ImageFilter

try:
    import pytesseract
    _HAS_PYTESSERACT = True
except ImportError:
    _HAS_PYTESSERACT = False

from ..core import detect_script, kannada_to_tigalari, kannada_to_latin, latin_to_kannada
from ..nlp.sentence_translator import FullSentenceTranslator


# Historical & Cultural Tulu Named Entities
TULU_CULTURAL_KEYWORDS = [
    "ಮಂಜುನಾಥ", "ಕದ್ರಿ", "ಪಂಜುರ್ಲಿ", "ಗುಳಿಗ", "ಬಬ್ಬುಸ್ವಾಮಿ", "ಕೊರಗಜ್ಜ", "ಜಾರಂದಾಯ",
    "ಕುಡ್ಲ", "ಉಡುಪಿ", "ಕಾಸರಗೋಡು", "ಮಂಗಳೂರು", "ಕಾರ್ಕಳ", "ಪುತ್ತೂರು", "ಬಂಟ್ವಾಳ", "ಬೆಳ್ತಂಗಡಿ",
    "ತುಳುನಾಡು", "ಆಲಿ ಕಟ್ಟು", "ನೇಮ", "ಕೋಲ", "ಕಂಬಳ"
]


def preprocess_document_image(image: Image.Image) -> Image.Image:
    """Enhance contrast and sharpness for manuscript and camera OCR."""
    # Convert to grayscale
    gray = image.convert("L")
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)
    # Slight sharpening to clean glyph edges
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    return sharpened


def load_image(image_input: Union[str, bytes, Image.Image]) -> Image.Image:
    """Load an image from filepath, raw bytes, base64 data string, or PIL Image."""
    if isinstance(image_input, Image.Image):
        return image_input

    if isinstance(image_input, str):
        # Base64 data URI check
        if image_input.startswith("data:image"):
            header, encoded = image_input.split(",", 1)
            raw_bytes = base64.b64decode(encoded)
            return Image.open(io.BytesIO(raw_bytes))
        # Raw base64 string check
        elif len(image_input) > 200 and not image_input.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff")):
            try:
                raw_bytes = base64.b64decode(image_input)
                return Image.open(io.BytesIO(raw_bytes))
            except Exception:
                pass
        # Filepath
        return Image.open(image_input)

    elif isinstance(image_input, bytes):
        return Image.open(io.BytesIO(image_input))

    raise ValueError("Unsupported image input type. Provide filepath, bytes, or PIL.Image.")


def extract_text_from_image(
    image_input: Union[str, bytes, Image.Image],
    lang: str = "kan+eng",
    preprocess: bool = True
) -> str:
    """Extract raw text from an image using Tesseract OCR with Kannada/English models."""
    img = load_image(image_input)
    if preprocess:
        img = preprocess_document_image(img)

    if _HAS_PYTESSERACT:
        try:
            text = pytesseract.image_to_string(img, lang=lang)
            return text.strip()
        except Exception:
            # Fallback to English if specified language data isn't installed
            try:
                text = pytesseract.image_to_string(img, lang="eng")
                return text.strip()
            except Exception:
                pass

    return ""


def extract_entities_from_text(text: str) -> Dict[str, List[str]]:
    """Extract dates, amounts, contact info, and Tulu cultural/regional entities."""
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))
    phones = list(set(re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)))
    amounts = list(set(re.findall(r"[\$€£₹]\s?[\d,]+(?:\.\d{2})?", text)))
    dates = list(set(re.findall(r"\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b", text)))

    # Saka era or Indian historic years (e.g. ಶಕ ೧೪೩೨ or Saka 1520)
    saka_matches = list(set(re.findall(r"(?:ಶಕ|ಶಾಲಿವಾಹನ|Saka)\s*[\d೧-೯]+", text, re.IGNORECASE)))

    # Cultural & geographic places in Tulunadu
    found_cultural = [term for term in TULU_CULTURAL_KEYWORDS if term in text]

    return {
        "emails": emails,
        "phone_numbers": phones,
        "monetary_amounts": amounts,
        "dates": dates,
        "historical_eras": saka_matches,
        "tulu_cultural_entities": found_cultural,
    }


def ocr_and_translate_document(
    image_input: Union[str, bytes, Image.Image],
    lang: str = "kan+eng",
    source_lang: Optional[str] = None
) -> Dict[str, Any]:
    """End-to-end OCR pipeline:

    1. Ingest image & preprocess.
    2. Extract raw text.
    3. Detect script & extract entities.
    4. Transliterate to Tigalari & Latin.
    5. Translate to English or Tulu using FullSentenceTranslator.
    """
    img = load_image(image_input)
    w, h = img.size
    img_format = img.format or "UNKNOWN"

    raw_text = extract_text_from_image(img, lang=lang, preprocess=True)
    entities = extract_entities_from_text(raw_text)

    script = detect_script(raw_text) if raw_text else "latin"

    translator = FullSentenceTranslator()
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    translated_lines: List[Dict[str, Any]] = []
    for line in lines:
        tr = translator.translate(line, source_lang=source_lang)
        translated_lines.append({
            "source_text": tr.source_text,
            "source_lang": tr.source_lang,
            "translated_text": tr.translated_text,
            "tulu_kannada": tr.tulu_kannada,
            "tulu_tigalari": tr.tulu_tigalari,
            "confidence": tr.confidence,
        })

    # Combined full script versions
    tigalari_full = kannada_to_tigalari(raw_text) if script == "kannada" else ""
    latin_full = kannada_to_latin(raw_text) if script == "kannada" else raw_text

    return {
        "dimensions": {"width": w, "height": h, "format": img_format},
        "raw_text": raw_text,
        "script": script,
        "transliterations": {
            "tigalari": tigalari_full,
            "latin": latin_full,
        },
        "entities": entities,
        "translations": translated_lines,
        "line_count": len(lines),
    }
