# Tulu-Tigalari & Kannada Transliterator (ತುಳು ಅನುವಾದಕ)

A complete Python library, CLI, and Web Transliterator Application for the **Tulu Dravidian Language** (ತುಳು ಬಾಸೆ), supporting **Unicode 16.0** character definitions (`U+11380` – `U+113FF`) and Baraha/ITRANS phonetic keyboard mapping inspired by [AATA Transliterator (aatana.org/transliterate)](https://aatana.org/transliterate/).

---

## Features

- **Multi-Way Transliteration:**
  - **Latin / English (Phonetic)** $\longleftrightarrow$ **Kannada (ಕನ್ನಡ)**
  - **Kannada (ಕನ್ನಡ)** $\longleftrightarrow$ **Tulu-Tigalari (Unicode 16.0)**
  - **Latin / English** $\longleftrightarrow$ **Tulu-Tigalari (Unicode 16.0)**
  - Auto-detection of input script (`detect_script`).
- **Tulu Language Phonetic Nuances:**
  - Handles the unique Tulu **"ae" sound** (represented in Kannada as `ೆ್`, e.g., `kODae` $\rightarrow$ `ಕೋಡೆ್` $\rightarrow$ `𑎒𑏆𑎞𑏁𑏎`).
  - Native Dravidian consonants: `ಳ` (`L`), `ಱ` (`rr` / `R`), `ೞ` (`zh`).
  - Ottakshara / geminates / conjunct stacking using Unicode 16.0 `U+113D0` (*TULU-TIGALARI CONJOINER*).
  - Standalone pure consonants using `U+113CE` (*TULU-TIGALARI SIGN VIRAMA*).
  - Lossless bidirectional round-trips with short/long E & O separation.
- **Interactive Web Transliterator Application:**
  - Runs in any modern browser with instant zero-latency transliteration as you type.
  - Self-contained embedded **Mallige Unicode v2** font via `@font-face` so Tulu-Tigalari script renders natively without needing system font installation.
  - Quick Tulu phrase presets (`ಸೊಲ್ಮೆಲು`, `ನಮಸ್ಕಾರ`, `ಈರ್ ಎಂಚ ಉಲ್ಲರ್?`, `ಕೋಡೆ್ ಬರ್ಸ ಬತ್ತ್ಂಡ್`).
  - Special character palette for Tulu halant, anusvara, visarga, and unique letters.
  - Live Unicode 16.0 code point inspector for linguistic research.
  - Phonetic typing cheat sheet table.

---

## Directory Structure

```
.
├── Mallige_Unicode_v2.ttf          # Official Unicode 16.0 Tulu-Tigalari font
├── run_app.py                      # One-click launcher for the Web Transliterator
└── kannada_tigalari_converter/
    ├── __init__.py                 # Python package exports
    ├── kannada_tigalari.py         # Kannada <-> Tigalari conversion engine
    ├── tulu_phonetic.py            # Latin <-> Kannada phonetic transliteration engine
    ├── transliterator.py           # Unified transliteration interface
    ├── cli.py                      # CLI with multi-mode, debug, REPL, and --web
    ├── test_converter.py           # Unit tests
    └── web/                        # Web Transliterator (HTML + CSS + JS)
        ├── index.html              # Main web UI
        ├── style.css               # Responsive design & font styles
        ├── app.js                  # Frontend controller
        ├── transliterator.js       # Client-side JavaScript transliteration engine
        └── fonts/
            └── Mallige_Unicode_v2.ttf
```

---

## Quick Start

### 1. Launch the Web Transliterator (Aatana-style UI)

Run from your terminal:
```bash
python3 run_app.py
```
Or:
```bash
python3 kannada_tigalari_converter/cli.py --web
```
This opens `http://localhost:8080/index.html` in your default browser.

---

### 2. Python API Usage

```python
from kannada_tigalari_converter import transliterate, detect_script

# 1. Phonetic Latin -> Tulu-Tigalari
tig = transliterate("solmelu", from_script="latin", to_script="tigalari")
print(tig)  # 𑎱𑏆𑎭𑏐𑎪𑏁𑎭𑎻

# 2. Phonetic Latin -> Kannada
kan = transliterate("solmelu", from_script="latin", to_script="kannada")
print(kan)  # ಸೊಲ್ಮೆಲು

# 3. Tulu 'ae' sound
print(transliterate("kODae", from_script="latin", to_script="kannada"))   # ಕೋಡೆ್

# 4. Kannada -> Tulu-Tigalari
print(transliterate("ನಮಸ್ಕಾರ", from_script="kannada", to_script="tigalari"))  # 𑎥𑎪𑎱𑏐𑎒𑎸𑎬

# 5. Tigalari -> Kannada
print(transliterate("𑎱𑏆𑎭𑏐𑎪𑏁𑎭𑎻", from_script="tigalari", to_script="kannada")) # ಸೊಲ್ಮೆಲು

# 6. Auto-detect source script
print(transliterate("barsa", from_script="auto", to_script="tigalari"))
```

---

### 3. Command Line Interface (CLI)

```bash
# Convert English/Latin to Tigalari (default)
python3 kannada_tigalari_converter/cli.py "solmelu"

# Convert English/Latin to Kannada
python3 kannada_tigalari_converter/cli.py "solmelu" --to kannada

# Convert Kannada to Tigalari with Unicode codepoint breakdown
python3 kannada_tigalari_converter/cli.py "ನಮಸ್ಕಾರ" --debug

# Convert Tigalari back to Kannada
python3 kannada_tigalari_converter/cli.py "𑎥𑎪𑎱𑏐𑎒𑎸𑎬" --reverse

# Search 1,000-word modern dictionary
python3 kannada_tigalari_converter/cli.py --lookup "water"

# Search 1886 Basel Mission Historical Tulu Dictionary (Rev. August Männer)
python3 kannada_tigalari_converter/cli.py --historical "agel"
python3 kannada_tigalari_converter/cli.py --historical --historical-domain "Paddy Cultivation"
python3 kannada_tigalari_converter/cli.py --historical --historical-pos "noun"

# Start Interactive Terminal REPL
python3 kannada_tigalari_converter/cli.py --interactive

# Browse 210 digitized Tulu books from AATA Digital Library
python3 kannada_tigalari_converter/cli.py --list-aatana-books "yakshgana"

# Run Kannada OCR on an AATA book and extract clean sentences in Tigalari & Kannada
python3 kannada_tigalari_converter/cli.py --ocr-aatana-book 1 --ocr-pages 3,4

# Inspect Tulu-NMT FLORES-200 parallel benchmark and evaluation metrics
python3 kannada_tigalari_converter/cli.py --nmt-benchmark

# Scrape Tulu Wikipedia (tcy.wikipedia.org) to harvest authentic sentences
python3 kannada_tigalari_converter/cli.py --scrape-wiki 30

# Scrape Tulu lemmas and definitions from English Wiktionary
python3 kannada_tigalari_converter/cli.py --scrape-wiktionary

# Run comprehensive internet harvest across Wikipedia & Wiktionary and update master CSV
python3 kannada_tigalari_converter/cli.py --scrape-all 50
```

---

### 4. Running Tests

```bash
# Run all test suites together (35 tests total)
python3 run_tests.py

# Or run individual modules:
python3 -m unittest kannada_tigalari_converter/test_converter.py
python3 -m unittest kannada_tigalari_converter/test_250_words.py
python3 -m unittest kannada_tigalari_converter/test_1000_words.py
python3 -m unittest kannada_tigalari_converter/test_aatana_and_nmt.py
```

---

### 5. Historical Lexicon & Dictionaries

- **Modern 1,000-word Corpus** (`words_dataset_1000.py` / `tulu_dictionary.py`):
  Covers 19 categories including daily conversational sentences, kinship, food, geography, anatomy, verb conjugations, and cultural heritage.
- **1886 Basel Mission Historical Lexicon** (`historical_dictionary.py` / `web/historical_dict.js`):
  Derived from **Rev. August Männer's 1886 landmark *Tulu-English Dictionary*** (Basel Mission Press, Mangalore). Contains 204 classical terms categorized across 17 cultural domains (Paddy Cultivation, Agrarian & Domestic Rituals, Daiva Worship, Artisans, Maritime, and Classical Verbs), each with complete Kannada, Tulu-Tigalari, Latin phonetic transliterations, grammatical part of speech, and 1886 definitions.

---

### 6. AATA Digital Book Library & Tulu-NMT Pipeline

- **AATA Digital Book Library Collector & OCR Facility** (`aatana_library_collector.py`):
  - Catalogues all **210 digitized Tulu literature books** from [AATA Digital Library](https://aatana.org/book-library/).
  - Integrated with **Tesseract OCR (Kannada `kan` model)** and **PyMuPDF** to extract text from scanned pages.
  - Automatically filters watermarks and non-Dravidian noise.
  - Converts segmented Tulu sentences into **Unicode 16.0 Tulu-Tigalari** and phonetic Latin.
- **Tulu Neural Machine Translation Pipeline** (`tulu_nmt_pipeline.py`):
  - Incorporates the methodology of **Manu Narayanan & Noëmi Aepli (LREC-COLING 2024)** ([Tulu-NMT](https://github.com/manunarayanan/Tulu-NMT)).
  - Implements transfer learning from high-resource Kannada (`kan_Knda`) to low-resource Tulu (`tcy_Knda`).
  - Supports English-Kannada-Tulu trilingual alignments and auto-generates Tigalari (`tcy_Tglr`).
  - Implements **sacreBLEU** and **chrF** Dravidian evaluation metrics.
  - Exports training/validation/test splits in Hugging Face JSONL format for models like IndicBARTSS, NLLB-200, and IndicTrans2.

---

### 7. Datasets in CSV Format (`datasets/`)

All datasets are exported as UTF-8 encoded CSV files in the [`datasets/`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/) folder:

| CSV File | Records | Description & Schema |
| :--- | :--- | :--- |
| [`tulu_master_consolidated_corpus.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_master_consolidated_corpus.csv) | **1,793+** | **Consolidated Master Corpus**: `id, source_type, source_name, tulu_kannada, tulu_tigalari, tulu_latin, english_meaning` |
| [`tulu_wikipedia_corpus.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_wikipedia_corpus.csv) | **539+** | Scraped from `tcy.wikipedia.org`: `id, source_article, tulu_kannada, tulu_tigalari, tulu_latin, word_count, char_count` |
| [`wiktionary_tulu_lemmas.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/wiktionary_tulu_lemmas.csv) | **50+** | English Wiktionary Tulu Lemmas: `id, tulu_kannada, tulu_tigalari, tulu_latin, source` |
| [`tulu_lexicon_1000.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_lexicon_1000.csv) | 1,000 | 19 categories: `id, category, english_meaning, tulu_kannada, tulu_tigalari, tulu_latin_phonetic` |
| [`tulu_lexicon_250.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_lexicon_250.csv) | 250 | Core test suite: `id, category, english_meaning, tulu_kannada, tulu_tigalari, tulu_latin_phonetic` |
| [`tulu_historical_dictionary_1886.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_historical_dictionary_1886.csv) | 204 | Rev. A. Männer (1886): `id, tulu_kannada, tulu_tigalari, tulu_latin, english_definition, part_of_speech, domain, source` |
| [`aatana_books_catalog.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/aatana_books_catalog.csv) | 210 | AATA Digital Library: `id, title, pdf_path, pdf_url` |
| [`tulu_nmt_parallel_corpus.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/tulu_nmt_parallel_corpus.csv) | 10 | Parallel NMT benchmark: `id, eng_Latn, kan_Knda, tcy_Knda, tcy_Tglr, tcy_Phonetic` |
| [`aatana_ocr_sodara_habba.csv`](file:///Users/jayanthanayak/Side_task/Tulu_Model/datasets/aatana_ocr_sodara_habba.csv) | 68 | OCR extracted sentences: `id, source_book, kannada, tigalari, phonetic, word_count, char_count` |

To regenerate or update all CSVs anytime:
```bash
python3 kannada_tigalari_converter/export_datasets_to_csv.py
# or via CLI:
python3 kannada_tigalari_converter/cli.py --export-csv
```
