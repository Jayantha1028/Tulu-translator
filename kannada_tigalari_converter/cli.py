#!/usr/bin/env python3
"""
Command Line Interface for Tulu & Kannada Transliterator.
Supports English / Latin, Kannada, and Tulu-Tigalari (Unicode 16.0).

Usage Examples:
    python cli.py "solmelu"                     # Latin -> Tigalari (default)
    python cli.py "solmelu" --to kannada        # Latin -> Kannada
    python cli.py "ನಮಸ್ಕಾರ" --to tigalari        # Kannada -> Tigalari
    python cli.py "𑎥𑎪𑎱𑏐𑎒𑎸𑎬" --to kannada      # Tigalari -> Kannada
    python cli.py --interactive                 # Interactive REPL
    python cli.py --web                         # Launch Web Transliterator
"""

import sys
import os
import argparse
import webbrowser

# Ensure import works anywhere
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
DATASETS_DIR = os.path.join(PARENT_DIR, "datasets")
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from kannada_tigalari_converter.transliterator import (
        transliterate,
        detect_script,
        inspect_codepoints,
    )
    from kannada_tigalari_converter.tulu_dictionary import lookup_tulu
    from kannada_tigalari_converter.historical_dictionary import search_historical_dictionary
    from kannada_tigalari_converter.aatana_library_collector import search_books, get_catalog, process_book_to_corpus
    from kannada_tigalari_converter.tulu_nmt_pipeline import load_nmt_benchmark_corpus, NMTMetrics
    from kannada_tigalari_converter.export_datasets_to_csv import export_all_csvs
    from kannada_tigalari_converter.tulu_web_scraper import TuluWikiHarvester, WiktionaryTuluHarvester, export_harvested_to_csv
    from kannada_tigalari_converter.tulu_morphology import (
        analyze as morph_analyze, analyze_sentence, lemmatize,
        pos_tag, decline_noun, conjugate_verb, Case,
    )
except ImportError:
    from transliterator import (
        transliterate,
        detect_script,
        inspect_codepoints,
    )
    from tulu_dictionary import lookup_tulu
    from historical_dictionary import search_historical_dictionary
    from aatana_library_collector import search_books, get_catalog, process_book_to_corpus
    from tulu_nmt_pipeline import load_nmt_benchmark_corpus, NMTMetrics
    from export_datasets_to_csv import export_all_csvs
    from tulu_web_scraper import TuluWikiHarvester, WiktionaryTuluHarvester, export_harvested_to_csv
    from tulu_morphology import (
        analyze as morph_analyze, analyze_sentence, lemmatize,
        pos_tag, decline_noun, conjugate_verb, Case,
    )


def run_interactive(from_script="auto", to_script="tigalari", debug=False):
    print("=" * 60)
    print("  Tulu-Tigalari Interactive Transliterator")
    print("  Scripts supported: Latin (English), Kannada, Tigalari")
    print("=" * 60)
    print(f"Current mode: From [{from_script.upper()}] -> To [{to_script.upper()}]")
    print("Commands:")
    print("  :mode <from> <to>  - Change mode (e.g. ':mode latin kannada')")
    print("  :debug             - Toggle code point breakdown")
    print("  :help              - Show help")
    print("  exit / quit        - Exit REPL\n")

    while True:
        try:
            line = input(f"{from_script} > ").strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit"):
                break
            if line.startswith(":mode"):
                parts = line.split()
                if len(parts) >= 3:
                    from_script, to_script = parts[1].lower(), parts[2].lower()
                    print(f"Mode set to: {from_script.upper()} -> {to_script.upper()}\n")
                else:
                    print("Usage: :mode <latin|kannada|tigalari|auto> <latin|kannada|tigalari>\n")
                continue
            if line.startswith(":debug"):
                debug = not debug
                print(f"Debug code point inspection: {'ENABLED' if debug else 'DISABLED'}\n")
                continue
            if line.startswith(":help"):
                print("Commands: :mode <from> <to>, :debug, exit\n")
                continue

            detected = detect_script(line) if from_script == "auto" else from_script
            out = transliterate(line, from_script=detected, to_script=to_script)
            print(f"Output ({to_script}): {out}")
            if debug:
                cps = " ".join(f"{c}({cp})" for c, cp in inspect_codepoints(out))
                print(f"Codepoints   : {cps}")
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def launch_web(port=8080):
    """Launches the local web transliterator & ASR speech studio in browser."""
    import http.server
    import socketserver
    import threading
    import json
    import io
    import time

    web_dir = os.path.join(PARENT_DIR, "web")
    if not os.path.isdir(web_dir):
        web_dir = os.path.join(CURRENT_DIR, "web")

    if not os.path.isdir(web_dir):
        print(f"Error: Web directory not found at {web_dir}")
        return

    # Lazy-load recognizer instance
    _speech_recognizer = None

    def get_recognizer():
        nonlocal _speech_recognizer
        if _speech_recognizer is None:
            from kannada_tigalari_converter.tulu_asr_engine import TuluSpeechRecognizer
            _speech_recognizer = TuluSpeechRecognizer()
        return _speech_recognizer

    class TuluWebRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=web_dir, **kwargs)

        def do_POST(self):
            t0 = time.time()
            status_code = 200
            event_name = "api_request"

            if self.path == "/api/asr/transcribe":
                event_name = "asr_transcribe"
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)

                    content_type = self.headers.get("Content-Type", "")
                    audio_bytes = None

                    if "application/json" in content_type:
                        import base64
                        payload = json.loads(body.decode("utf-8"))
                        b64_data = payload.get("audio_base64", "")
                        if "," in b64_data:
                            b64_data = b64_data.split(",")[1]
                        audio_bytes = base64.b64decode(b64_data)
                    elif "multipart/form-data" in content_type:
                        # Simple boundary-based extractor
                        boundary = content_type.split("boundary=")[-1].strip().encode()
                        parts = body.split(b"--" + boundary)
                        for part in parts:
                            if b'filename="' in part or b'name="audio"' in part:
                                header_end = part.find(b"\r\n\r\n")
                                if header_end != -1:
                                    audio_bytes = part[header_end + 4:].rstrip(b"\r\n")
                                    break
                    else:
                        # Raw audio payload
                        audio_bytes = body

                    if not audio_bytes:
                        status_code = 400
                        self._send_json({"error": "No audio data received"}, status=status_code)
                        return

                    recognizer = get_recognizer()
                    res = recognizer.transcribe(audio_bytes)
                    self._send_json({
                        "success": True,
                        **res.to_dict()
                    })
                except Exception as e:
                    status_code = 500
                    self._send_json({"success": False, "error": str(e)}, status=status_code)
                finally:
                    dur_ms = (time.time() - t0) * 1000
                    from kannada_tigalari_converter.core.observability import GLOBAL_LOGGER, GLOBAL_TELEMETRY
                    GLOBAL_TELEMETRY.record(dur_ms, status_code=status_code)
                    GLOBAL_LOGGER.log("tulu-asr", "INFO", event_name, f"Processed in {dur_ms:.1f}ms", duration_ms=dur_ms)
                return

            elif self.path == "/api/translate/sentence":
                event_name = "translate_sentence"
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    payload = json.loads(body.decode("utf-8")) if body else {}
                    text = payload.get("text", "")
                    src = payload.get("source_lang", None)

                    from kannada_tigalari_converter.nlp.sentence_translator import FullSentenceTranslator
                    res = FullSentenceTranslator.translate(text, source_lang=src)
                    self._send_json({
                        "success": True,
                        **res.to_dict()
                    })
                except Exception as e:
                    status_code = 500
                    self._send_json({"success": False, "error": str(e)}, status=status_code)
                finally:
                    dur_ms = (time.time() - t0) * 1000
                    from kannada_tigalari_converter.core.observability import GLOBAL_LOGGER, GLOBAL_TELEMETRY
                    GLOBAL_TELEMETRY.record(dur_ms, status_code=status_code)
                    GLOBAL_LOGGER.log("tulu-nmt", "INFO", event_name, f"Processed in {dur_ms:.1f}ms", duration_ms=dur_ms)
                return

            elif self.path == "/api/ocr/extract-and-translate":
                event_name = "ocr_extract_and_translate"
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    content_type = self.headers.get("Content-Type", "")

                    image_data = None
                    lang = "kan+eng"

                    if "application/json" in content_type:
                        import base64
                        payload = json.loads(body.decode("utf-8"))
                        image_data = payload.get("image", payload.get("image_base64", ""))
                        lang = payload.get("lang", "kan+eng")
                    elif "multipart/form-data" in content_type:
                        boundary = content_type.split("boundary=")[-1].strip().encode()
                        parts = body.split(b"--" + boundary)
                        for part in parts:
                            if b'filename="' in part or b'name="image"' in part or b'name="file"' in part:
                                header_end = part.find(b"\r\n\r\n")
                                if header_end != -1:
                                    image_data = part[header_end + 4:].rstrip(b"\r\n")
                                    break
                    else:
                        image_data = body

                    if not image_data:
                        status_code = 400
                        self._send_json({"error": "No image data received"}, status=status_code)
                        return

                    from kannada_tigalari_converter.vision.tulu_ocr_service import ocr_and_translate_document
                    result = ocr_and_translate_document(image_data, lang=lang)
                    self._send_json({
                        "success": True,
                        **result
                    })
                except Exception as e:
                    status_code = 500
                    self._send_json({"success": False, "error": str(e)}, status=status_code)
                finally:
                    dur_ms = (time.time() - t0) * 1000
                    from kannada_tigalari_converter.core.observability import GLOBAL_LOGGER, GLOBAL_TELEMETRY
                    GLOBAL_TELEMETRY.record(dur_ms, status_code=status_code)
                    GLOBAL_LOGGER.log("tulu-ocr", "INFO", event_name, f"Processed in {dur_ms:.1f}ms", duration_ms=dur_ms)
                return

            elif self.path in ("/recognize/strokes", "/api/recognize/strokes"):
                event_name = "stroke_recognition"
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    payload = json.loads(body.decode("utf-8")) if body else {}
                    strokes = payload.get("strokes", [])

                    from kannada_tigalari_converter.vision.stroke_recognizer import CharacterStrokeRecognizer
                    recognizer = CharacterStrokeRecognizer()
                    result = recognizer.recognize(strokes)
                    self._send_json({
                        "success": True,
                        **result
                    })
                except Exception as e:
                    status_code = 500
                    self._send_json({"success": False, "error": str(e)}, status=status_code)
                finally:
                    dur_ms = (time.time() - t0) * 1000
                    from kannada_tigalari_converter.core.observability import GLOBAL_LOGGER, GLOBAL_TELEMETRY
                    GLOBAL_TELEMETRY.record(dur_ms, status_code=status_code)
                    GLOBAL_LOGGER.log("tulu-strokes", "INFO", event_name, f"Processed in {dur_ms:.1f}ms", duration_ms=dur_ms)
                return

            self._send_json({"error": "Not found"}, status=404)

        def do_GET(self):
            t0 = time.time()
            status_code = 200

            if self.path in ("/health", "/api/health"):
                from kannada_tigalari_converter.core.observability import GLOBAL_TELEMETRY
                self._send_json({
                    "status": "healthy",
                    "service": "tulu-unified-suite",
                    "telemetry": GLOBAL_TELEMETRY.summary()
                })
                return

            if self.path in ("/metrics", "/api/metrics"):
                from kannada_tigalari_converter.core.observability import GLOBAL_LOGGER, GLOBAL_TELEMETRY
                self._send_json({
                    "telemetry": GLOBAL_TELEMETRY.summary(),
                    "recent_logs": GLOBAL_LOGGER.tail(25)
                })
                return
            if self.path.startswith("/api/translate/sentence"):
                try:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed.query)
                    text = params.get("text", [""])[0]
                    src = params.get("source_lang", [None])[0]

                    from kannada_tigalari_converter.nlp.sentence_translator import FullSentenceTranslator
                    res = FullSentenceTranslator.translate(text, source_lang=src)
                    self._send_json({
                        "success": True,
                        **res.to_dict()
                    })
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, status=500)
                return

            if self.path.startswith("/api/asr/test-sample"):
                try:
                    import urllib.parse
                    parsed = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed.query)
                    word = params.get("word", ["ನಮಸ್ಕಾರ"])[0]

                    from kannada_tigalari_converter.tulu_audio_pipeline import SyntheticTuluAudioGenerator
                    sample_path = "/tmp/tulu_web_sample.wav"
                    SyntheticTuluAudioGenerator.synthesize_to_wav(word, sample_path)

                    recognizer = get_recognizer()
                    res = recognizer.transcribe(sample_path)
                    self._send_json({
                        "success": True,
                        "sample_word": word,
                        **res.to_dict()
                    })
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, status=500)
                return

            super().do_GET()

        def _send_json(self, data: dict, status: int = 200):
            response = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

    handler = TuluWebRequestHandler

    # Find free port if 8080 is taken
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", port))
        s.close()
    except OSError:
        port = 8081

    httpd = socketserver.TCPServer(("", port), handler)
    url = f"http://localhost:{port}/index.html"
    print(f"Serving Tulu Transliterator & Speech Studio at {url}")
    print("Press Ctrl+C to stop the web server.\n")

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    webbrowser.open(url)

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping web server.")
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="Tulu-Tigalari & Kannada Transliteration CLI (Unicode 16.0 Standard)."
    )
    parser.add_argument("text", nargs="?", help="Text to transliterate")
    parser.add_argument(
        "-f", "--from", dest="from_script", default="auto",
        choices=["auto", "latin", "kannada", "tigalari"],
        help="Source script (default: auto detect)"
    )
    parser.add_argument(
        "-t", "--to", dest="to_script", default="tigalari",
        choices=["latin", "kannada", "tigalari"],
        help="Target script (default: tigalari)"
    )
    parser.add_argument(
        "-r", "--reverse", action="store_true",
        help="Reverse conversion shortcut (Tigalari -> Kannada, or Kannada -> Latin)"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="Display Unicode code points for each character"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true",
        help="Start interactive conversion prompt"
    )
    parser.add_argument(
        "-w", "--web", action="store_true",
        help="Launch the interactive Web Transliterator in your browser"
    )
    parser.add_argument(
        "-l", "--lookup", dest="lookup_word",
        help="Lookup native Tulu word meaning from English or Kannada"
    )
    parser.add_argument(
        "--historical", dest="historical_query", nargs="?", const="",
        help="Search 1886 Basel Mission historical Tulu dictionary (Rev. August Männer)"
    )
    parser.add_argument(
        "--historical-domain", dest="historical_domain", default=None,
        help="Filter historical dictionary by cultural/semantic domain"
    )
    parser.add_argument(
        "--historical-pos", dest="historical_pos", default=None,
        help="Filter historical dictionary by part of speech (noun, verb, adjective, adverb)"
    )
    parser.add_argument(
        "--list-aatana-books", dest="aatana_search", nargs="?", const="",
        help="List or search 210 digitized Tulu books from AATA Digital Library (aatana.org/book-library/)"
    )
    parser.add_argument(
        "--ocr-aatana-book", dest="ocr_book_id",
        help="Run Kannada OCR on an AATA book by ID or title (e.g. --ocr-aatana-book 1)"
    )
    parser.add_argument(
        "--ocr-pages", dest="ocr_pages", default="3,4",
        help="Comma-separated page numbers for OCR processing (default: 3,4)"
    )
    parser.add_argument(
        "--nmt-benchmark", action="store_true",
        help="Display Tulu-NMT FLORES-200 parallel benchmark and evaluation metrics"
    )
    parser.add_argument(
        "--export-csv", action="store_true",
        help="Export all datasets (1000 words, 250 words, historical, AATA catalog, NMT) to CSV files in datasets/"
    )
    parser.add_argument(
        "--scrape-wiki", dest="scrape_wiki_limit", nargs="?", const=30, type=int,
        help="Scrape Tulu Wikipedia (tcy.wikipedia.org) to harvest authentic sentences (default limit: 30 articles)"
    )
    parser.add_argument(
        "--scrape-wiktionary", action="store_true",
        help="Scrape Tulu lemmas and definitions from English Wiktionary"
    )
    parser.add_argument(
        "--scrape-all", dest="scrape_all_limit", nargs="?", const=50, type=int,
        help="Harvest internet corpus across Wikipedia & Wiktionary and update master CSV (default: 50 articles)"
    )
    parser.add_argument(
        "--scrape-continuous", action="store_true",
        help="Run autonomous background scraper with O(1) deduplication until target is reached (default target: 50,000)"
    )
    parser.add_argument(
        "--target", type=int, default=50000,
        help="Target records for continuous scraper (default: 50,000)"
    )
    parser.add_argument(
        "--status-corpus", action="store_true",
        help="Display health and deduplication stats of the master corpus"
    )
    parser.add_argument(
        "--transcribe", dest="transcribe_audio", type=str, default=None,
        help="Transcribe spoken Tulu audio file (WAV/MP3/M4A) to Kannada, Tigalari, Latin, and English"
    )
    parser.add_argument(
        "--train-asr", action="store_true",
        help="Fine-tune Whisper with LoRA on paired Tulu acoustic speech samples on Apple Silicon MPS"
    )
    parser.add_argument(
        "--train-samples", type=int, default=50,
        help="Number of paired speech samples to synthesize/train (default: 50)"
    )
    parser.add_argument(
        "--epochs", type=int, default=3,
        help="Number of training epochs (default: 3)"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8080,
        help="Port for web server (default: 8080)"
    )

    # ── Morphological Analyzer Commands ──
    parser.add_argument(
        "--analyze", dest="analyze_word", type=str, default=None,
        help="Morphologically analyze a Tulu word (e.g. --analyze ಇಲ್ಲಗ್)"
    )
    parser.add_argument(
        "--analyze-sentence", dest="analyze_sent", type=str, default=None,
        help="Morphologically analyze every word in a Tulu sentence"
    )
    parser.add_argument(
        "--lemmatize", dest="lemmatize_word", type=str, default=None,
        help="Lemmatize a Tulu word — strip inflection to recover base form"
    )
    parser.add_argument(
        "--decline", dest="decline_word", type=str, default=None,
        help="Generate full 8-case declension table for a Tulu noun"
    )
    parser.add_argument(
        "--conjugate", dest="conjugate_word", type=str, default=None,
        help="Generate conjugation paradigm for a Tulu verb"
    )

    args = parser.parse_args()

    if args.lookup_word:
        results = lookup_tulu(args.lookup_word)
        if not results:
            print(f"No dictionary entries found for '{args.lookup_word}'.")
        else:
            print(f"--- Tulu Dictionary Results for '{args.lookup_word}' ---")
            for r in results:
                print(f"English       : {r['english']}")
                print(f"Kannada       : {r['kannada_meaning']}")
                print(f"Tulu (Kannada): {r['tulu_kannada']}")
                print(f"Tulu (Tigalari): {r['tulu_tigalari']}")
                print(f"Phonetic      : {r['tulu_latin']}")
                print("-" * 40)
        return

    if args.historical_query is not None:
        results = search_historical_dictionary(
            args.historical_query,
            domain=args.historical_domain,
            pos=args.historical_pos
        )
        if not results:
            print(f"No historical dictionary entries found for query '{args.historical_query}'.")
        else:
            print(f"--- Basel Mission Historical Tulu Dictionary (1886) [{len(results)} matches] ---")
            for r in results[:25]:
                print(f"[{r['id']}] {r['tulu_kannada']}  |  Tigalari: {r['tulu_tigalari']}  |  Latin: {r['tulu_latin']}")
                print(f"    POS: {r['part_of_speech'].upper()} | Domain: {r['domain']}")
                print(f"    Meaning: {r['english']}")
                print(f"    Source: {r['source']}")
                print("-" * 60)
            if len(results) > 25:
                print(f"... and {len(results) - 25} more entries. Filter with --historical-domain or --historical-pos.")
        return

    if args.aatana_search is not None:
        books = search_books(args.aatana_search)
        print(f"--- AATA Digital Book Library (aatana.org/book-library/) [{len(books)} books] ---")
        for b in books[:30]:
            print(f"[{b['id']:3d}] {b['title']}")
            print(f"      PDF: {b['pdf_url']}")
        if len(books) > 30:
            print(f"... and {len(books) - 30} more books. Filter with --list-aatana-books <keyword>")
        print("\nTo extract text with OCR, run:")
        print("  python3 cli.py --ocr-aatana-book <id> --ocr-pages 1,2,3")
        return

    if args.ocr_book_id:
        pages = [int(p.strip()) for p in args.ocr_pages.split(",") if p.strip().isdigit()]
        print(f"Fetching and running OCR on AATA book '{args.ocr_book_id}' (pages {pages})...")
        res = process_book_to_corpus(args.ocr_book_id, page_numbers=pages)
        print(f"\nCompleted! Processed {res['pages_processed']} pages. Extracted {res['total_sentences']} clean sentences:")
        print("=" * 65)
        for s in res["sentences"][:10]:
            print(f"[{s['id']:2d}] Kannada : {s['kannada']}")
            print(f"     Tigalari: {s['tigalari']}")
            print(f"     Phonetic: {s['phonetic']}")
            print("-" * 65)
        if len(res["sentences"]) > 10:
            print(f"... and {len(res['sentences']) - 10} more sentences.")
        return

    if args.nmt_benchmark:
        corpus = load_nmt_benchmark_corpus()
        print(f"--- Tulu-NMT FLORES-200 Benchmark (Narayanan & Aepli, 2024) [{len(corpus.data)} pairs] ---")
        for r in corpus.data:
            print(f"[{r['id']:2d}] English : {r['eng_Latn']}")
            print(f"     Kannada : {r['kan_Knda']}")
            print(f"     Tulu    : {r['tcy_Knda']}")
            print(f"     Tigalari: {r['tcy_Tglr']}")
            print(f"     Phonetic: {r['tcy_Phonetic']}")
            print("-" * 65)
        return

    if args.export_csv:
        print("Exporting datasets to CSV...")
        results = export_all_csvs()
        print("Export complete! Saved datasets in datasets/:")
        for fname, count in results.items():
            print(f"  ✓ {fname:<36} : {count:>5} records")
        return

    if args.scrape_wiki_limit is not None:
        print(f"Scraping up to {args.scrape_wiki_limit} articles from Tulu Wikipedia...")
        sentences = TuluWikiHarvester.harvest(max_articles=args.scrape_wiki_limit)
        print(f"Harvested {len(sentences)} authentic sentences! Sample:")
        for s in sentences[:5]:
            print(f"[{s['id']}] {s['source']}")
            print(f"  KN: {s['tulu_kannada']}")
            print(f"  TG: {s['tulu_tigalari']}")
            print(f"  PH: {s['tulu_latin']}")
            print("-" * 60)
        return

    if args.scrape_wiktionary:
        print("Scraping Tulu lemmas from English Wiktionary...")
        lemmas = WiktionaryTuluHarvester.harvest(limit=50)
        print(f"Harvested {len(lemmas)} lemmas:")
        for l in lemmas[:10]:
            print(f"[{l['id']:2d}] KN: {l['tulu_kannada']} | TG: {l['tulu_tigalari']} | PH: {l['tulu_latin']}")
        return

    if args.scrape_all_limit is not None:
        print(f"Starting comprehensive internet scrape (Wikipedia limit: {args.scrape_all_limit})...")
        res = export_harvested_to_csv(wiki_limit=args.scrape_all_limit)
        print("\nAll datasets updated:")
        for k, v in res.items():
            print(f"  ✓ {k:<38}: {v:>6} records")
        return

    if args.status_corpus:
        from kannada_tigalari_converter.data_cleaner import DeduplicatedDataset
        master_csv = os.path.join(DATASETS_DIR, "tulu_master_consolidated_corpus.csv")
        ds = DeduplicatedDataset(filepath=master_csv)
        st = ds.stats()
        print("=" * 65)
        print("  Tulu Master Corpus Health & Deduplication Telemetry")
        print("=" * 65)
        print(f"  Total Clean Records     : {st['total_records']:,}")
        print(f"  Unique Fingerprints     : {st['unique_fingerprints']:,}")
        print(f"  Duplicates Discarded    : {st['duplicates_dropped']:,}")
        print(f"  Invalid / Low Density   : {st['invalid_dropped']:,}")
        print(f"  Master File Path        : {master_csv}")
        return

    if args.scrape_continuous:
        from kannada_tigalari_converter.continuous_scraper import ContinuousCorpusHarvester
        harvester = ContinuousCorpusHarvester(target_records=args.target)
        try:
            harvester.run()
        except KeyboardInterrupt:
            print("\n[Harvester] Paused by user. Checkpoint saved. Run again anytime to resume!")
        return

    if args.transcribe_audio:
        from kannada_tigalari_converter.tulu_asr_engine import TuluSpeechRecognizer
        recognizer = TuluSpeechRecognizer()
        res = recognizer.transcribe(args.transcribe_audio)
        print("=" * 65)
        print("  🎙️  Tulu Speech-to-Text Recognition Output")
        print("=" * 65)
        print(f"  Kannada Transcript  : {res.kannada}")
        print(f"  Tigalari Unicode 16 : {res.tigalari}")
        print(f"  Phonetic Latin      : {res.latin}")
        print(f"  English Meaning     : {res.english or '(No definition found)'}")
        print(f"  Confidence Score    : {res.confidence * 100:.1f}%")
        print(f"  Inference Latency   : {res.latency_ms:.1f} ms")
        print(f"  Hardware Engine     : {res.device}")
        return

    if args.train_asr:
        from kannada_tigalari_converter.asr.tulu_asr_trainer import train_tulu_asr
        train_tulu_asr(num_samples=args.train_samples, epochs=args.epochs)
        return

    # ── Morphological Analyzer Handlers ──
    if args.analyze_word:
        result = morph_analyze(args.analyze_word)
        print("=" * 65)
        print("  Tulu Morphological Analysis")
        print("=" * 65)
        print(f"  Input    : {result.surface_word} ({result.surface_latin})")
        print(f"  Lemma    : {result.lemma_kannada} ({result.lemma_latin})")
        print(f"  Tigalari : {result.lemma_tigalari}")
        print(f"  POS      : {result.pos.value}")
        print(f"  Tag      : {result.tag_string()}")
        if result.case:
            print(f"  Case     : {result.case.value}")
        if result.tense:
            print(f"  Tense    : {result.tense.value}")
        if result.person:
            print(f"  Person   : {result.person.value}")
        if result.number:
            print(f"  Number   : {result.number.value}")
        if result.mood and result.mood.value != "indicative":
            print(f"  Mood     : {result.mood.value}")
        if result.is_negative:
            print(f"  Negative : Yes")
        if result.english_meaning:
            print(f"  Meaning  : {result.english_meaning}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Morphemes: {' + '.join(m.tag + '(' + m.latin + ')' for m in result.morphemes)}")
        print("=" * 65)
        return

    if args.analyze_sent:
        results = analyze_sentence(args.analyze_sent)
        print("=" * 65)
        print("  Tulu Sentence Morphological Analysis")
        print("=" * 65)
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] {r.surface_word} ({r.surface_latin})")
            print(f"      Lemma: {r.lemma_kannada} | POS: {r.pos.value} | Tag: {r.tag_string()}")
            if r.english_meaning:
                print(f"      Meaning: {r.english_meaning}")
        print("\n" + "=" * 65)
        return

    if args.lemmatize_word:
        lemma = lemmatize(args.lemmatize_word)
        print(f"  {args.lemmatize_word} → {lemma}")
        return

    if args.decline_word:
        table = decline_noun(args.decline_word)
        print("=" * 70)
        print(f"  Noun Declension: {table.lemma_kannada} ({table.lemma_latin})")
        print("=" * 70)
        for case in Case:
            forms = table.forms[case]
            for f in forms:
                print(f"  {case.value:14s} : {f['kannada']:15s} ({f['latin']:15s}) {f['tigalari']}")
        print("=" * 70)
        return

    if args.conjugate_word:
        table = conjugate_verb(args.conjugate_word)
        print("=" * 70)
        print(f"  Verb Conjugation: {table.lemma_kannada} ({table.lemma_latin})")
        print("=" * 70)
        for slot in sorted(table.forms):
            f = table.forms[slot]
            print(f"  {slot:12s} : {f['kannada']:15s} ({f['latin']:15s}) {f['tigalari']}")
        if table.irregular_forms:
            print("\n  Known Irregular Forms:")
            for slot, f in sorted(table.irregular_forms.items()):
                print(f"  {slot:12s} : {f['kannada']:15s} ({f['latin']:15s}) {f['tigalari']}")
        print("=" * 70)
        return

    if args.web:
        launch_web(port=args.port)
        return

    if args.interactive:
        run_interactive(from_script=args.from_script, to_script=args.to_script, debug=args.debug)
        return

    if not args.text:
        parser.print_help()
        sys.exit(1)

    from_script = args.from_script
    to_script = args.to_script

    if args.reverse:
        detected = detect_script(args.text)
        if detected == "tigalari":
            from_script, to_script = "tigalari", "kannada"
        elif detected == "kannada":
            from_script, to_script = "kannada", "latin"
        else:
            from_script, to_script = "latin", "tigalari"

    out = transliterate(args.text, from_script=from_script, to_script=to_script)
    print(out)

    if args.debug:
        print("\nUnicode Code Points:")
        for ch, cp in inspect_codepoints(out):
            print(f"  {ch} -> {cp}")


if __name__ == '__main__':
    main()
