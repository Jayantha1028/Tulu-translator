"""
Universal Digital Book Library Collector & OCR Engine
Supports:
1. Any direct PDF URL / HTTPS document link (Internet Archive, Wikimedia Commons, DLI, Google Drive, direct links)
2. Local PDF files and image directories (PNG, JPG, TIFF, WebP)
3. Direct single or multi-page image OCR
4. Internet Archive (archive.org) book identifier downloads
5. Built-in AATA Digital Library catalog (210 books)
6. High-accuracy multilingual OCR (Kannada 'kan', Tulu/Sanskrit 'san', English 'eng')
7. Legacy Kannada/Tulu font encoding cleanup, header/watermark removal, and Tulu sentence segmentation
8. Automatic Unicode 16.0 Tigalari (`U+11380`-`U+113FF`) and Latin phonetic transliteration
"""

import os
import sys
import json
import re
import io
import ssl
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Tuple, Union

import unicodedata
from PIL import Image
import pymupdf
import pytesseract

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


# ==============================================================================
# 1. CATALOG & SEARCH INTERFACES (AATA + EXTENSIBLE MULTI-SOURCE)
# ==============================================================================

def get_catalog() -> List[Dict]:
    """Loads the catalog of 210 books from AATA Digital Library."""
    if os.path.isfile(CATALOG_FILE):
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def search_books(query: str) -> List[Dict]:
    """Searches the built-in catalog by keyword or book ID."""
    q = (query or "").strip().lower()
    catalog = get_catalog()
    if not q:
        return catalog
    if q.isdigit():
        target_id = int(q)
        return [b for b in catalog if b["id"] == target_id]
    return [b for b in catalog if q in b["title"].lower() or q in b.get("pdf_path", "").lower()]


# ==============================================================================
# 2. UNIVERSAL DOWNLOADER (ANY URL, ARCHIVE.ORG, AATA, LOCAL PATHS)
# ==============================================================================

def is_url(target: str) -> bool:
    """Checks whether the target is a valid HTTP/HTTPS URL."""
    if not isinstance(target, str):
        return False
    return target.strip().startswith(("http://", "https://"))


def resolve_archive_org_url(identifier: str) -> str:
    """
    Resolves an Internet Archive (archive.org) item identifier or URL
    to its direct downloadable PDF stream.
    E.g. 'tulu-english-dictionary-1886' -> 'https://archive.org/download/.../...pdf'
    """
    clean_id = identifier.strip()
    if "archive.org/details/" in clean_id:
        clean_id = clean_id.split("archive.org/details/")[-1].split("/")[0]

    meta_url = f"https://archive.org/metadata/{clean_id}"
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(meta_url, headers={"User-Agent": "Mozilla/5.0 (TuluLibraryCollector/2.0)"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    files = data.get("files", [])
    # Find preferred PDF file (prefer text-searchable or standard PDF)
    pdf_file = None
    for f in files:
        fname = f.get("name", "")
        if fname.lower().endswith(".pdf"):
            if "text" in fname.lower() or not pdf_file:
                pdf_file = fname

    if not pdf_file:
        raise ValueError(f"No PDF file found for Internet Archive item: {clean_id}")

    server = data.get("server") or "ia800000.us.archive.org"
    dir_path = data.get("dir", f"/items/{clean_id}")
    return f"https://{server}{dir_path}/{pdf_file}"


def download_book(
    source: Union[str, int],
    output_dir: Optional[str] = None,
    filename: Optional[str] = None
) -> str:
    """
    Universal book downloader supporting:
      1. A local file path -> returns normalized path if exists
      2. Any arbitrary HTTP/HTTPS PDF URL -> downloads and caches locally
      3. Internet Archive identifier (e.g. 'archive:item_id' or 'https://archive.org/details/...')
      4. AATA Library book ID (1-210) or book title -> downloads from aatana.org

    :param source: URL, archive ID, local path, or AATA catalog ID/title
    :param output_dir: Directory where files should be cached (defaults to downloads/)
    :param filename: Optional explicit output filename
    :return: Absolute path to the locally accessible PDF/document file
    """
    out_dir = output_dir or DEFAULT_CACHE_DIR
    os.makedirs(out_dir, exist_ok=True)

    # Case A: Local file already exists
    if isinstance(source, str) and os.path.isfile(source):
        return os.path.abspath(source)

    # Case B: Direct URL
    if isinstance(source, str) and is_url(source):
        # Check if it's an Internet Archive details URL
        if "archive.org/details/" in source:
            source = resolve_archive_org_url(source)

        parts = list(urllib.parse.urlsplit(source))
        # Ensure path parts are safely quoted
        parts[2] = urllib.parse.quote(urllib.parse.unquote(parts[2]))
        encoded_url = urllib.parse.urlunsplit(parts)

        base_name = filename or os.path.basename(parts[2]) or "downloaded_book.pdf"
        if not base_name.lower().endswith(".pdf"):
            base_name += ".pdf"

        local_path = os.path.join(out_dir, base_name)
        if os.path.isfile(local_path) and os.path.getsize(local_path) > 1000:
            return local_path

        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0 (TuluLibraryCollector/2.0)"})
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            content = resp.read()

        with open(local_path, "wb") as f:
            f.write(content)
        return local_path

    # Case C: Internet Archive shorthand 'archive:<item_id>'
    if isinstance(source, str) and source.startswith("archive:"):
        item_id = source.split("archive:", 1)[1].strip()
        direct_url = resolve_archive_org_url(item_id)
        return download_book(direct_url, output_dir=out_dir, filename=filename)

    # Case D: AATA Library Catalog book ID or title
    catalog = get_catalog()
    target_book = None

    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        bid = int(source)
        for b in catalog:
            if b["id"] == bid:
                target_book = b
                break
    else:
        results = search_books(str(source))
        if results:
            target_book = results[0]

    if target_book:
        pdf_url = target_book["pdf_url"]
        pdf_filename = filename or os.path.basename(target_book["pdf_path"])
        return download_book(pdf_url, output_dir=out_dir, filename=pdf_filename)

    raise ValueError(f"Could not resolve book source: '{source}'. Provide a valid URL, local PDF path, archive:id, or catalog ID/title.")


# Backward compatibility alias
download_book_pdf = download_book


# ==============================================================================
# 3. HIGH-ACCURACY UNIVERSAL OCR ENGINE (PDFs & IMAGES)
# ==============================================================================

def ocr_image(
    image_input: Union[str, Image.Image, bytes],
    lang: str = "kan+eng",
    tess_config: str = "--psm 1"
) -> str:
    """
    Performs OCR directly on a single image (file path, PIL Image, or image bytes).
    Supports multiple languages simultaneously (e.g. 'kan+eng', 'kan', 'san').
    """
    if isinstance(image_input, str):
        if not os.path.isfile(image_input):
            raise FileNotFoundError(f"Image not found: {image_input}")
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise TypeError(f"Unsupported image type: {type(image_input)}")

    try:
        # Check if tesseract supports the requested language, fallback gracefully
        text = pytesseract.image_to_string(img, lang=lang, config=tess_config)
    except pytesseract.TesseractError:
        # Fallback to kannada or english if combined dictionary is missing
        text = pytesseract.image_to_string(img, lang="kan")

    return clean_raw_ocr_text(text)


def ocr_pdf_pages(
    pdf_path: str,
    page_numbers: Optional[List[int]] = None,
    dpi: int = 200,
    lang: str = "kan"
) -> List[Dict[str, any]]:
    """
    Performs OCR on specified pages of any PDF document.
    Extracts high-resolution page bitmaps using PyMuPDF and runs Tesseract OCR.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF document not found: {pdf_path}")

    doc = pymupdf.open(pdf_path)
    results = []
    try:
        total_pages = len(doc)
        pages_to_process = page_numbers if page_numbers else list(range(1, total_pages + 1))

        for p_num in pages_to_process:
            if p_num < 1 or p_num > total_pages:
                continue
            page = doc[p_num - 1]

            # Fast path: Check if page already has native digital text stream
            native_text = page.get_text("text").strip()
            # If native text has substantial Kannada characters, use it directly (faster & 100% accurate)
            kannada_chars = sum(1 for c in native_text if "KANNADA" in unicodedata.name(c, ""))
            if kannada_chars >= 40:
                cleaned_text = clean_raw_ocr_text(native_text)
                results.append({
                    "page": p_num,
                    "method": "digital_native",
                    "raw_text": native_text,
                    "text": cleaned_text,
                    "char_count": len(cleaned_text)
                })
                continue

            # Fallback to raster OCR
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            try:
                extracted_text = pytesseract.image_to_string(img, lang=lang)
            except Exception:
                extracted_text = pytesseract.image_to_string(img, lang="kan")

            cleaned_text = clean_raw_ocr_text(extracted_text)
            results.append({
                "page": p_num,
                "method": "tesseract_ocr",
                "raw_text": extracted_text,
                "text": cleaned_text,
                "char_count": len(cleaned_text)
            })
    finally:
        doc.close()

    return results


# ==============================================================================
# 4. TEXT CLEANING & LINGUISTIC SENTENCE SEGMENTATION
# ==============================================================================

def clean_raw_ocr_text(raw_text: str) -> str:
    """
    Cleans raw OCR and scanned book text:
    - Strips recurring watermarks and headers
    - Cleans scanner margin artifacts
    - Corrects detached viramas and matras
    """
    if not raw_text:
        return ""

    lines = raw_text.splitlines()
    cleaned_lines = []

    for line in lines:
        l = line.strip()
        # Remove common header/footer watermarks
        if re.search(r"(AATA|aatana|Digital Book Library|Flipbook|Archive\.org|Google\s*Books|Digitized\s*by|Page\s*\d+|\b\d+\b$)", l, re.IGNORECASE) and len(l) < 45:
            continue
        # Remove standalone punctuation or stray ASCII noise symbols
        if len(l) <= 2 and not any("KANNADA" in unicodedata.name(c, "") for c in l):
            continue
        cleaned_lines.append(l)

    result = "\n".join(cleaned_lines)
    # Fix broken viramas detached by OCR space: e.g. "ಕ್ " -> "ಕ್"
    result = re.sub(r"([ಕ-ಹ])\s+್", r"\1್", result)
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
        words = clean.split()
        if len(words) < 2:
            continue

        # Check Kannada character ratio (from Tulu-NMT criteria)
        kannada_chars = sum(1 for c in clean if "KANNADA" in unicodedata.name(c, ""))
        if kannada_chars >= len(clean) * 0.35:
            valid_sentences.append(clean)

    return valid_sentences


# ==============================================================================
# 5. END-TO-END BOOK PROCESSOR TO TULU CORPUS
# ==============================================================================

def process_book_to_corpus(
    source: Union[str, int],
    page_numbers: Optional[List[int]] = None,
    dpi: int = 200,
    lang: str = "kan",
    output_json: Optional[str] = None
) -> Dict[str, any]:
    """
    Universal End-to-End Book Processing Pipeline:
      1. Resolves and downloads book from ANY source (URL, archive.org, local path, or AATA catalog)
      2. Performs digital extraction / Tesseract OCR
      3. Cleans noise, fixes diacritics, and segments sentences
      4. Transliterates to official Unicode 16.0 Tigalari (`U+11380`-`U+113FF`) and Latin phonetic
      5. Returns structured corpus dictionary and optionally saves JSON.
    """
    local_pdf = download_book(source)
    ocr_results = ocr_pdf_pages(local_pdf, page_numbers=page_numbers, dpi=dpi, lang=lang)

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
        "source": str(source),
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
