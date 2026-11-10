# Tulu-Tigalari & Kannada Transliterator (ತುಳು ಅನುವಾದಕ)

A complete Python library, CLI, and Web Transliterator Application for the **Tulu Dravidian Language** (ತುಳು ಬಾಸೆ), supporting official **Unicode 16.0** character definitions (`U+11380` – `U+113FF`), Baraha/ITRANS phonetic keyboard mapping inspired by [AATA Transliterator (aatana.org/transliterate)](https://aatana.org/transliterate/), speech AI, and zero-burden LLM preparation.

---

## 🚀 Key Features & Capabilities

### 1. Multi-Way Script Transliteration & Phonetics
- **Latin / English (Phonetic)** $\longleftrightarrow$ **Kannada (ಕನ್ನಡ)**
- **Kannada (ಕನ್ನಡ)** $\longleftrightarrow$ **Tulu-Tigalari (Unicode 16.0)**
- **Latin / English** $\longleftrightarrow$ **Tulu-Tigalari (Unicode 16.0)**
- **Script Auto-Detection:** Intelligently detects input language/script (`detect_script`).
- **Tulu Language Phonetic Nuances:**
  - Handles the unique Tulu **"ae" sound** (represented in Kannada as `ೆ್`, e.g., `kODae` $\rightarrow$ `ಕೋಡೆ್` $\rightarrow$ `𑎒𑏆𑎞𑏁𑏎`).
  - Native Dravidian consonants: `ಳ` (`L`), `ಱ` (`rr` / `R`), `ೞ` (`zh`).
  - Ottakshara / geminates / conjunct stacking using Unicode 16.0 `U+113D0` (*TULU-TIGALARI CONJOINER*).
  - Standalone pure consonants using `U+113CE` (*TULU-TIGALARI SIGN VIRAMA*).
  - Lossless bidirectional round-trips with 100% test fidelity.

### 2. Interactive Web Studio (Port 9000 & PWA Offline Support)
- **Multi-threaded Web Studio:** Serves by default on `http://localhost:9000/index.html` with dynamic port fallback and multi-threaded request handling.
- **Magic Slate (✍️ Interactive Handwriting Canvas):** Draw Tigalari and Kannada characters with mouse or touch. Real-time stroke recognition reconstructs unicode glyphs directly.
- **Vision Document OCR (📷):** Drag-and-drop or upload images containing Tulu/Kannada text for instant extraction and transliteration.
- **Text-to-Speech (🔊 TTS Audio Engine):** Local speech synthesis with Web Audio acoustic formant modeling and macOS native speech engine fallback.
- **Speech-to-Text Studio (🎙️ Whisper ASR):** Record voice or upload audio files to transcribe spoken Tulu into Kannada, Tigalari, Latin, and English.
- **Font-Independent Vector Card Exporter (✨ SVG & 📷 PNG):** Download publication-ready, scalable SVG cards or 2x retina PNG graphics that display Tigalari script perfectly on any device, even without the font installed.
- **PWA Mobile App:** Complete with Service Worker (`sw.js`) and Web Manifest (`manifest.json`) for installing as a standalone offline app on Android, iOS, and macOS.

### 3. Grammar Translation & Dual-Engine Router
- **Deterministic FSM Grammar Rules:** Sub-millisecond (`< 0.1ms`) SOV $\longleftrightarrow$ SVO bidirectional sentence translation.
- **Neural SLM Hybrid Engine:** Dynamic router toggle between deterministic rules and contextual local Small Language Models (e.g., Qwen2.5 / Llama 3 via Ollama).

### 4. Agglutinative Morphology & Lexicons
- **Lemmatization:** Deconstruct inflected words to recover canonical dictionary base lemmas (e.g. `ಇಲ್ಲಡ್` $\rightarrow$ `ಇಲ್ಲ`, `ಕುಡ್ಲಗ್` $\rightarrow$ `ಕುಡ್ಲ`, `ಬರ್ಪೆ` $\rightarrow$ `ಬಲೆ`).
- **8-Case Noun Declension Engine:** Full Dravidian case inflection (Nominative, Accusative, Dative, Genitive, Locative, Ablative, Instrumental, Sociative).
- **Verb Conjugation:** Tense $\times$ Person $\times$ Number $\times$ Polarity paradigms, negative forms (`-ಿಜಿ`), obligatives (`-ೊಡು`), infinitives (`-ಯೆರೆ`).
- **Basel Mission Historical Lexicon (1886):** Rev. August Männer's landmark dictionary with 204 cultural terms across 17 traditional agrarian and spiritual domains.

### 5. Zero-Burden LLM Preparation Suite
- **Stream Dataset Builder (`tulu_dataset_builder.py`):** Converts the master corpus into standard instruction tuning formats (`ShareGPT` / `Alpaca`) in `< 0.05s` with `O(1)` memory usage (`< 25MB` RAM).
- **Unicode 16.0 Tokenizer Tool (`tulu_tokenizer_tool.py`):** Patches Hugging Face tokenizers with official Tigalari codepoints (`U+11380`–`U+113FF`) and special Tulu ligatures (`ೆ್`, `ಱ`, `ೞ`) to prevent token fragmentation.
- **Micro-Batch LoRA Trainer (`tulu_llm_trainer.py`):** Hardware-safe trainer featuring an instant `--dry-run` simulation mode (<2s runtime, zero GPU load).
- **Ollama Modelfile Exporter (`Modelfile.tulu`):** Zero-training configuration to run ultra-lightweight models (like `qwen2.5:0.5b`, consuming < 400MB RAM) with prompt-engineered Tulu translation and Tigalari generation.

---

## 📁 Directory Structure

```
.
├── kannada_tigalari_converter/             # Core Python Engine & NLP Library
│   ├── core/                               # Script Conversion, Phonetics, Observability
│   │   ├── kannada_tigalari.py             # Kannada <-> Unicode 16.0 Tigalari converter
│   │   ├── transliterator.py               # Unified script detector & transliterator
│   │   └── observability.py                # Structured telemetry and metrics tracker
│   ├── lexicon/                            # Lexicons & Dictionaries
│   │   ├── tulu_dictionary.py              # Modern Tulu dictionary & phonetic lookup
│   │   ├── historical_dictionary.py        # 1886 Basel Mission historical dictionary
│   │   ├── words_dataset_250.py            # 250-word canonical subset
│   │   └── words_dataset_1000.py           # 1,000-word benchmark corpus
│   ├── nlp/                                # Natural Language Processing & LLM Suite
│   │   ├── sentence_translator.py          # SOV <-> SVO grammar translation engine
│   │   ├── neural_translator.py            # Hybrid dual-engine router (Rule vs SLM)
│   │   ├── tulu_morphology.py              # Morphological analyzer, POS tagger, declensions
│   │   ├── tulu_dataset_builder.py         # Memory-efficient stream dataset builder
│   │   ├── tulu_tokenizer_tool.py          # Tigalari Unicode 16.0 tokenizer patcher
│   │   ├── tulu_llm_trainer.py             # Micro-batch LoRA trainer with --dry-run
│   │   └── ollama_model_exporter.py        # Modelfile exporter for local SLMs
│   ├── asr/                                # Speech Processing & TTS
│   │   ├── tulu_audio_pipeline.py          # 16kHz audio loader, VAD trimming, Mel-spectrogram
│   │   ├── tulu_asr_engine.py              # Whisper-tiny ASR on Apple Silicon MPS
│   │   └── tulu_tts_engine.py              # Local acoustic formant speech synthesizer
│   ├── vision/                             # OCR & Handwriting Recognition
│   │   ├── stroke_recognizer.py            # Magic Slate geometric stroke recognizer
│   │   └── vision_ocr.py                   # Document preprocessing & Kannada OCR
│   ├── benchmark.py                        # Automated performance & accuracy benchmark
│   ├── export_svg.py                       # Font-independent SVG vector card generator
│   └── cli.py                              # Unified CLI & Multi-threaded Web Server
├── web/                                    # Interactive Web Studio (PWA)
│   ├── index.html                          # Full-featured Web UI
│   ├── app.js                              # Client controller (Audio, Canvas, Transliterator)
│   ├── manifest.json                       # Progressive Web App manifest
│   ├── sw.js                               # Service Worker for offline asset caching
│   └── fonts/Mallige_Unicode_v2.ttf        # Embedded Unicode 16.0 Tigalari font
├── datasets/                               # Curated Datasets (Master Corpus, Lexicons)
│   ├── tulu_master_consolidated_corpus.csv # 1,793+ deduplicated trilingual entries
│   └── tulu_lexicon_1000.csv               # 1,000 verified Tulu vocabulary entries
├── docs/                                   # In-Depth Guides & Technical Architecture
│   └── TULU_MASTER_CORPUS_CREATION.md      # Detailed creation documentation for master corpus
├── Modelfile.tulu                          # Zero-training Ollama Modelfile configuration
├── run_app.py                              # Launcher script for Web Studio (Port 9000)
└── run_tests.py                            # Discovers and runs all 188+ unit tests
```

---

## ⚡ Quick Start

### 1. Launch the Web Studio (Port 9000)

Run from your terminal:
```bash
python3 run_app.py
```
Or:
```bash
python3 kannada_tigalari_converter/cli.py --web --port 9000
```
This automatically opens `http://localhost:9000/index.html` in your browser.

---

### 2. Python API Usage

```python
from kannada_tigalari_converter import transliterate, detect_script
from kannada_tigalari_converter.export_svg import TuluSvgExporter

# 1. Phonetic Latin -> Tulu-Tigalari (Unicode 16.0)
tig = transliterate("solmelu", from_script="latin", to_script="tigalari")
print(tig)  # 𑎱𑏆𑎭𑏐𑎪𑏁𑎭𑎻

# 2. Phonetic Latin -> Kannada
kan = transliterate("solmelu", from_script="latin", to_script="kannada")
print(kan)  # ಸೊಲ್ಮೆಲು

# 3. Tulu 'ae' sound
print(transliterate("kODae", from_script="latin", to_script="kannada"))   # ಕೋಡೆ್

# 4. Kannada -> Tulu-Tigalari
print(transliterate("ನಮಸ್ಕಾರ", from_script="kannada", to_script="tigalari"))  # 𑎥𑎪𑎱𑏐𑎒𑎸𑎬

# 5. Export font-independent SVG vector card
TuluSvgExporter.save_to_file("ನಮಸ್ಕಾರ", "namaskara.svg", theme="dark")
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

# Run zero-burden performance & accuracy benchmark
python3 kannada_tigalari_converter/cli.py --benchmark

# Morphological analysis of inflected Tulu words
python3 kannada_tigalari_converter/cli.py --analyze "ಇಲ್ಲಡ್"
python3 kannada_tigalari_converter/cli.py --lemmatize "ಬರ್ಪೆ"
python3 kannada_tigalari_converter/cli.py --decline "ಇಲ್ಲ"
python3 kannada_tigalari_converter/cli.py --conjugate "ಬಲೆ"
python3 kannada_tigalari_converter/cli.py --analyze-sentence "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ"

# Search 1886 Basel Mission Historical Tulu Dictionary
python3 kannada_tigalari_converter/cli.py --historical "agel"
```

---

### 4. Running the Benchmark Suite

To measure transliteration speed, sentence translation latency, and memory consumption locally:
```bash
python3 -m kannada_tigalari_converter.benchmark
```
*Results on Apple Silicon (M4):*
- **Transliteration Throughput:** `> 150,000 words/second` (100% roundtrip accuracy)
- **Sentence Translation Latency:** `~ 4.3 ms`
- **Morphology Parsing Speed:** `~ 4,000 parses/second`
- **Peak RAM Footprint:** `< 0.25 MB`
- **Total Duration:** `< 2.0 seconds`

---

### 5. Running with Local SLMs via Ollama

Run ultra-lightweight models (e.g. Qwen2.5-0.5B, consuming < 400MB RAM) without local GPU training:
```bash
# 1. Register the pre-configured Tulu Modelfile
ollama create tulu-slm -f Modelfile.tulu

# 2. Interact with the Tulu model
ollama run tulu-slm "Translate 'ಎಂಚ ಉಲ್ಲರ್' to English and Tigalari script"
```

---

### 6. Web Corpus Quality & Noise Segregation

Raw internet scraped data (Wikipedia, Wiktionary, OCR) contains artifacts such as wikitext leaks, incomplete table splits, and broken fragments. The quality segregation engine scores linguistic authenticity and partitions the data in `< 2.5s` using `O(1)` streaming:

```bash
# Segregate raw web data into high-quality and quarantined low-quality files
python3 kannada_tigalari_converter/cli.py --segregate-quality datasets/tulu_wikipedia_corpus.csv
```

*Results on Wikipedia Corpus (13,929 entries):*
- **⭐ High-Quality Dataset (`datasets/tulu_web_corpus_high_quality.csv`):** **11,522 records (82.7%)** (Grammatical, fluent Tulu with authentic morphology, ready for LLM fine-tuning).
- **⚠️ Low-Quality Quarantined (`datasets/tulu_web_corpus_low_quality.csv`):** **2,407 records (17.3%)** (Broken fragments, unbalanced brackets, wikitext `scope=` leaks, excessive table digits).

---

### 7. Running Tests

```bash
# Run the complete test suite (195 unit tests)
python3 run_tests.py
```

---

### 8. Documentation & Corpus Details

For a complete breakdown of how `tulu_master_consolidated_corpus.csv` was aggregated, deduplicated, and normalized across 5 primary sources:
👉 Read [`docs/TULU_MASTER_CORPUS_CREATION.md`](file:///Users/jayanthanayak/Side_task/Tulu_Model/docs/TULU_MASTER_CORPUS_CREATION.md).

---

## 📜 License & Acknowledgements

- **License:** MIT License. See [LICENSE](LICENSE) for details.
- **Tigalari Unicode Font:** Embedded `Mallige Unicode v2` font supporting official Unicode 16.0 Tigalari codepoints.
- **Reference & Inspiration:** [AATA Transliterator (aatana.org)](https://aatana.org/transliterate/) and Rev. August Männer's 1886 Basel Mission Tulu Dictionary.
