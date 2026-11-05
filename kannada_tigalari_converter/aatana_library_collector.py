"""
AATA Digital Book Library Collector & OCR Facility
Accesses digitized Tulu literature from https://aatana.org/book-library/
and performs high-accuracy Kannada / Tulu OCR with text cleaning and
Unicode 16.0 Tulu-Tigalari script transliteration.
"""

import os
import sys
import json
import re
import io
import ssl
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Tuple

import unicodedata
from PIL import Image
import pymupdf
import pytesseract

# Ensure parent and package paths are available
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari
    from kannada_tigalari_converter.tulu_phonetic import kannada_to_latin
except ImportError:
    from kannada_tigalari import kannada_to_tigalari
    from tulu_phonetic import kannada_to_latin


CATALOG_FILE = os.path.join(CURRENT_DIR, "aatana_books_catalog.json")
DEFAULT_CACHE_DIR = os.path.join(CURRENT_DIR, "downloads")


def get_catalog() -> List[Dict]:
    """Loads the catalog of 210 books from AATA Digital Library."""
    if os.path.isfile(CATALOG_FILE):
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def search_books(query: str) -> List[Dict]:
    """Searches the catalog by keyword or book ID."""
    q = (query or "").strip().lower()
    catalog = get_catalog()
    if not q:
        return catalog
    if q.isdigit():
        target_id = int(q)
        return [b for b in catalog if b["id"] == target_id]
    return [b for b in catalog if q in b["title"].lower() or q in b["pdf_path"].lower()]


def download_book_pdf(book_id_or_title, output_dir: Optional[str] = None) -> str:
    """
    Downloads a book PDF from AATA Digital Book Library.
    Returns the local file path.
    """
    catalog = get_catalog()
    target_book = None

    if isinstance(book_id_or_title, int) or (isinstance(book_id_or_title, str) and book_id_or_title.isdigit()):
        bid = int(book_id_or_title)
        for b in catalog:
            if b["id"] == bid:
                target_book = b
                break
    else:
        results = search_books(str(book_id_or_title))
        if results:
            target_book = results[0]

    if not target_book:
        raise ValueError(f"Book '{book_id_or_title}' not found in AATA library catalog.")

    out_dir = output_dir or DEFAULT_CACHE_DIR
    os.makedirs(out_dir, exist_ok=True)

    pdf_filename = os.path.basename(target_book["pdf_path"])
    local_path = os.path.join(out_dir, pdf_filename)

    if os.path.isfile(local_path) and os.path.getsize(local_path) > 1000:
        return local_path

    pdf_url = target_book["pdf_url"]
    # Handle URL encoding of spaces
    parts = list(urllib.parse.urlsplit(pdf_url))
    parts[2] = urllib.parse.quote(parts[2])
    encoded_url = urllib.parse.urlunsplit(parts)

    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        content = resp.read()

    with open(local_path, "wb") as f:
        f.write(content)

    return local_path


def ocr_pdf_pages(
    pdf_path: str,
    page_numbers: Optional[List[int]] = None,
    dpi: int = 200,
    lang: str = "kan"
) -> List[Dict[str, any]]:
    """
    Performs Tesseract OCR on specified pages of a PDF.
    Returns list of {'page': int, 'text': str, 'confidence': float}.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = pymupdf.open(pdf_path)
    results = []
    try:
        total_pages = len(doc)
        pages_to_process = page_numbers if page_numbers else list(range(1, total_pages + 1))

        for p_num in pages_to_process:
            if p_num < 1 or p_num > total_pages:
                continue
            page = doc[p_num - 1]
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            # Perform OCR with Tesseract
            extracted_text = pytesseract.image_to_string(img, lang=lang)
            cleaned_text = clean_raw_ocr_text(extracted_text)

            results.append({
                "page": p_num,
                "raw_text": extracted_text,
                "text": cleaned_text,
                "char_count": len(cleaned_text)
            })
    finally:
        doc.close()

    return results


def clean_raw_ocr_text(raw_text: str) -> str:
    """
    Cleans raw OCR text: removes watermarks, noise artifacts, and aligns Kannada diacritics.
    """
    if not raw_text:
        return ""

    lines = raw_text.splitlines()
    cleaned_lines = []

    for line in lines:
        l = line.strip()
        # Remove common header/footer watermarks
        if re.search(r"(AATA|aatana|Digital Book Library|Flipbook|Page\s*\d+|\b\d+\b$)", l, re.IGNORECASE) and len(l) < 30:
            continue
        # Remove standalone punctuation or stray ASCII symbols
        if len(l) <= 2 and not any("KANNADA" in unicodedata.name(c, "") for c in l):
            continue
        cleaned_lines.append(l)

    result = "\n".join(cleaned_lines)
    # Normalize multiple newlines
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def segment_tulu_sentences(text: str) -> List[str]:
    """
    Segments Kannada/Tulu text into grammatically sound sentences.
    Applies criteria from Tulu-NMT research to discard noisy/non-Dravidian lines.
    """
    if not text:
        return []

    # Split on sentence boundaries: period, question mark, exclamation, danda (। or ॥), or double newline
    raw_sentences = re.split(r"[.?!।॥\n\r]+", text)
    valid_sentences = []

    for s in raw_sentences:
        clean = " ".join(s.split()).strip()
        # Sentence must have at least 2 words
        words = clean.split()
        if len(words) < 2:
            continue

        # Check Kannada character ratio (from Tulu-NMT criteria)
        kannada_chars = sum(1 for c in clean if "KANNADA" in unicodedata.name(c, ""))
        if kannada_chars >= len(clean) * 0.40:
            valid_sentences.append(clean)

    return valid_sentences


def process_book_to_corpus(
    book_id_or_title,
    page_numbers: Optional[List[int]] = None,
    output_json: Optional[str] = None
) -> Dict[str, any]:
    """
    Full pipeline: Downloads book -> Runs Kannada OCR -> Segments sentences ->
    Transliterates to Tulu-Tigalari (Unicode 16.0) & Latin phonetic ->
    Saves clean corpus.
    """
    local_pdf = download_book_pdf(book_id_or_title)
    ocr_results = ocr_pdf_pages(local_pdf, page_numbers=page_numbers, dpi=200, lang="kan")

    full_text = "\n".join(r["text"] for r in ocr_results)
    sentences = segment_tulu_sentences(full_text)

    corpus_entries = []
    for idx, s in enumerate(sentences, 1):
        tig = kannada_to_tigalari(s)
        lat = kannada_to_latin(s)
        corpus_entries.append({
            "id": idx,
            "kannada": s,
            "tigalari": tig,
            "phonetic": lat,
            "word_count": len(s.split()),
            "char_count": len(s)
        })

    result_data = {
        "book_path": local_pdf,
        "pages_processed": len(ocr_results),
        "total_sentences": len(corpus_entries),
        "sentences": corpus_entries
    }

    if output_json:
        os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

    return result_data
