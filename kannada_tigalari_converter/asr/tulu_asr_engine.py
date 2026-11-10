"""
Tulu Speech-to-Text (ASR) Engine & Multi-Script Generation
==========================================================
End-to-end Speech Recognition for Tulu Language (*ISO 639-3: tcy*).
Transcribes spoken audio into:
1. Kannada Script (contemporary standard orthography)
2. Tulu-Tigalari Script (Unicode 16.0 native historical script)
3. Latin Phonetic Transliteration (Baraha / ITRANS standard)
4. English Translation (bilingual contextual translation)

Hardware Acceleration:
- Apple Silicon M-Series (M1/M2/M3/M4) via Metal Performance Shaders (`mps`)
- Nvidia GPUs via CUDA (`cuda`)
- Universal CPU Fallback (`cpu`)
"""

import os
import sys
import time
import json
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any, BinaryIO, Tuple
import numpy as np

# Ensure project imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.tulu_audio_pipeline import AudioPreprocessor
from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari
from kannada_tigalari_converter.tulu_phonetic import kannada_to_latin
from kannada_tigalari_converter.tulu_dictionary import lookup_tulu
from kannada_tigalari_converter.tulu_morphology import analyze as morph_analyze

try:
    import torch
except ImportError:
    torch = None

try:
    from transformers import WhisperProcessor, WhisperForConditionalGeneration
except ImportError:
    WhisperProcessor = None
    WhisperForConditionalGeneration = None


@dataclass
class TuluASRResult:
    """Complete multi-script speech recognition result."""
    kannada: str                   # Recognized Kannada script
    tigalari: str                  # Official Unicode 16.0 Tigalari script
    latin: str                     # Phonetic Latin transliteration
    english: str                   # Contextual English translation / meaning
    confidence: float              # Mean selected-token probability, not calibrated accuracy
    latency_ms: float              # Processing time in milliseconds
    device: str                    # Hardware device used (mps, cuda, cpu)
    audio_duration_sec: float      # Duration of input audio in seconds

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kannada": self.kannada,
            "tigalari": self.tigalari,
            "latin": self.latin,
            "english": self.english,
            "confidence": round(self.confidence, 4),
            "latency_ms": round(self.latency_ms, 2),
            "device": self.device,
            "audio_duration_sec": round(self.audio_duration_sec, 2),
        }


class TuluSpeechRecognizer:
    """
    Main Speech-to-Text inference engine for Tulu.
    Integrates acoustic feature extraction, neural/acoustic decoding,
    and instantaneous multi-script translation.
    """

    def __init__(self, model_name_or_path: str = "openai/whisper-tiny", device: Optional[str] = None):
        self.model_name = model_name_or_path
        self.device = self._select_device(device)
        self.model = None
        self.processor = None

        self._init_engine()

    def _select_device(self, preferred: Optional[str]) -> str:
        """Auto-detects fastest hardware acceleration (Apple Silicon MPS > CUDA > CPU)."""
        if preferred:
            return preferred
        if torch is not None:
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                return "mps"
            if torch.cuda.is_available():
                return "cuda"
        return "cpu"

    def _init_engine(self):
        """Initializes acoustic and neural model components."""
        # Cap PyTorch intra-op threads to prevent CPU overheating
        if torch is not None:
            try:
                torch.set_num_threads(2)
            except Exception:
                pass

        # Load Hugging Face Whisper model if available
        if WhisperForConditionalGeneration is not None and torch is not None:
            try:
                # Load processor & model in float32 / float16
                torch_device = torch.device(self.device)
                dtype = torch.float32 if self.device == "cpu" else torch.float16
                self.processor = WhisperProcessor.from_pretrained(self.model_name)
                self.model = WhisperForConditionalGeneration.from_pretrained(
                    self.model_name,
                    torch_dtype=dtype,
                    low_cpu_mem_usage=True,
                ).to(torch_device)

                # Only use an adapter with a usable recorded validation score.
                lora_dir = os.path.join(ROOT_DIR, "models", "tulu_whisper_lora")
                if os.path.isdir(lora_dir) and os.path.isfile(os.path.join(lora_dir, "adapter_config.json")):
                    summary_path = os.path.join(lora_dir, "training_summary.json")
                    adapter_wer = self._read_adapter_wer(summary_path)

                    if self._adapter_wer_is_usable(adapter_wer):
                        try:
                            from peft import PeftModel
                            self.model = PeftModel.from_pretrained(self.model, lora_dir)
                            print(f"[Tulu ASR] Activated validated Tulu LoRA adapter (WER {adapter_wer:.3f})")
                        except Exception as err:
                            print(f"[Tulu ASR] Info: Base Whisper loaded (LoRA note: {err})")
                    else:
                        print(f"[Tulu ASR] Ignoring adapter with unusable or missing validation WER ({adapter_wer!r}); using base Whisper.")

                generation_config = getattr(self.model, "generation_config", None)
                if generation_config is not None and hasattr(generation_config, "forced_decoder_ids"):
                    generation_config.forced_decoder_ids = None

                self.model.eval()
                print(f"[Tulu ASR] Loaded neural Whisper engine '{self.model_name}' on device '{self.device}'")
            except Exception as e:
                print(f"[Tulu ASR] Info: Neural model load deferred ({e}). Operating in acoustic-matcher mode.")

    def transcribe(
        self,
        audio_source: Union[str, bytes, np.ndarray, BinaryIO],
        sr: Optional[int] = None,
    ) -> TuluASRResult:
        """
        Transcribes speech audio into Kannada, Tigalari, Latin, and English.
        """
        start_time = time.time()

        # 1. Audio Preprocessing
        audio = AudioPreprocessor.load_audio(audio_source, sr=sr)
        duration_sec = len(audio) / AudioPreprocessor.TARGET_SR
        audio_trimmed = AudioPreprocessor.trim_silence(audio)

        # 2. Decoding
        kannada_text = ""
        confidence = 0.0

        # Option A: Neural Whisper Decoding if loaded
        if self.model is not None and self.processor is not None and torch is not None:
            try:
                torch_device = torch.device(self.device)
                dtype = torch.float32 if self.device == "cpu" else torch.float16

                inputs = self.processor(
                    audio_trimmed,
                    sampling_rate=AudioPreprocessor.TARGET_SR,
                    return_tensors="pt"
                )
                input_features = inputs.input_features.to(torch_device, dtype=dtype)

                with torch.no_grad():
                    generated = self.model.generate(
                        input_features=input_features,
                        language="kannada",
                        task="transcribe",
                        max_new_tokens=64,
                        return_dict_in_generate=True,
                        output_scores=True,
                    )
                    kannada_text = self.processor.batch_decode(
                        generated.sequences,
                        skip_special_tokens=True
                    )[0].strip()
                    confidence = self._generation_confidence(generated)

                    # Clean up GPU buffers immediately to keep system cool
                    if self.device == "mps" and hasattr(torch, "mps"):
                        torch.mps.empty_cache()
            except Exception as e:
                print(f"[Tulu ASR] Neural decode notice: {e}, falling back to acoustic matcher.")

        # Do not turn synthetic tones into guessed words when neural ASR is absent
        # or fails. The old tone matcher had no text-dependent acoustic signal.
        if not kannada_text:
            confidence = 0.0

        # 3. Canonical Script Normalization (ensures Kannada script for all downstream conversions)
        from kannada_tigalari_converter.transliterator import detect_script
        from kannada_tigalari_converter.tulu_phonetic import latin_to_kannada
        from kannada_tigalari_converter.kannada_tigalari import tigalari_to_kannada

        raw_script = detect_script(kannada_text)
        if raw_script == "latin":
            canonical_kn = latin_to_kannada(kannada_text)
            if canonical_kn:
                kannada_text = canonical_kn
        elif raw_script == "tigalari":
            kannada_text = tigalari_to_kannada(kannada_text)
        canonical_recognition = kannada_text

        # 4. Smart Lexical Snapping (Phoneme Intent Detection & Word Alignment)
        english_trans = ""
        dict_matches = lookup_tulu(kannada_text)

        test_latin = kannada_to_latin(kannada_text).lower().strip()

        # Step 0: Phonemic Intent Detection for Common Spoken Tulu Greetings & Sentences
        import re
        s_clean = test_latin.replace(" ", "")
        
        # Detect "ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು" (Mataregla solmelu)
        has_mater = bool(re.search(r"(mat|met|maath|maat|maather)", s_clean))
        has_solmelu = bool(re.search(r"(sol|sul|mel|mul|nul|nule|ulu)", s_clean))
        if has_mater and has_solmelu:
            kannada_text = "ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು"
            english_trans = "Warm heart greetings unto all! (Tulu)"
        elif bool(re.search(r"(namas|namash|namak|namsk)", s_clean)):
            kannada_text = "ನಮಸ್ಕಾರ"
            english_trans = "Hello / Respectful greeting"
        elif bool(re.search(r"(solm|sulm|solmelu)", s_clean)) and len(s_clean) <= 10:
            kannada_text = "ಸೊಲ್ಮೆಲು"
            english_trans = "Thank you / Greetings (Tulu)"
        elif bool(re.search(r"(enc|eMch|ench)", s_clean)) and bool(re.search(r"(ull|ullar|ular)", s_clean)):
            kannada_text = "ಎಂಚ ಉಲ್ಲರ್"
            english_trans = "How are you? (Polite)"

        # Common multi-word conversational Tulu phrases table
        CONVERSATIONAL_PHRASES = {
            "mataregla solmelu": ("ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು", "Warm heart greetings unto all! (Tulu)"),
            "materegla solmelu": ("ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು", "Warm heart greetings unto all! (Tulu)"),
            "maatergla solmelu": ("ಮಾತೆರ್ಗ್ಲಾ ಸೊಲ್ಮೆಲು", "Warm heart greetings unto all! (Tulu)"),
            "solmelu maaterglaa": ("ಸೊಲ್ಮೆಲು ಮಾತೆರ್ಗ್ಲಾ", "Warm heart greetings unto all! (Tulu)"),
            "solmelu materegla": ("ಸೊಲ್ಮೆಲು ಮಾತೆರೆಗ್ಲಾ", "Warm heart greetings unto all! (Tulu)"),
            "encha ullar": ("ಎಂಚ ಉಲ್ಲರ್", "How are you? (Polite)"),
            "eer olpa ullar": ("ಈರ್ ಒಲ್ಪ ಉಲ್ಲರ್", "Where are you situated? (Tulu)"),
            "eerena pudar daane": ("ಈರೆನ ಪುದರ್ ದಾನೆ", "What is your respected name? (Tulu)"),
            "enna pudar": ("ಎನ್ನ ಪುದರ್", "My name is... (Tulu)"),
            "namaskara": ("ನಮಸ್ಕಾರ", "Hello / Respectful greeting"),
            "solmelu": ("ಸೊಲ್ಮೆಲು", "Thank you / Greetings (Tulu)"),
            "untule": ("ಉಂತುಲೆ", "Stand up / Halt (Tulu)"),
            "kullule": ("ಕುಲ್ಲುಲೆ", "Please sit down (Polite)"),
            "barpe": ("ಬರ್ಪೆ", "I am coming (Tulu)"),
            "battmd": ("ಬತ್ತ್ಂಡ್", "It arrived / It came"),
            "tulu paatera": ("ತುಳು ಪಾತೆರ", "Speak in Tulu"),
            "edde dina": ("ಎಡ್ಡೆ ದಿನ", "Good day / Have a good day"),
        }

        if not english_trans and not dict_matches and kannada_text:
            import difflib

            # Step A: Check common conversational multi-word phrases first with length sanity check
            best_p = None
            best_p_score = 0.0
            for p_cand in CONVERSATIONAL_PHRASES.keys():
                len_r = min(len(test_latin), len(p_cand)) / max(len(test_latin), len(p_cand))
                if len_r < 0.60:
                    continue
                sc = difflib.SequenceMatcher(None, test_latin, p_cand).ratio()
                if sc > best_p_score:
                    best_p_score = sc
                    best_p = p_cand

            if best_p and best_p_score >= 0.85:
                kannada_text, english_trans = CONVERSATIONAL_PHRASES[best_p]
            else:
                # Step B: Check against full dataset phrases
                from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000
                latin_map = {item["latin_phonetic"].lower(): item for item in WORDS_DATASET_1000}
                
                best_lat = None
                best_lat_score = 0.0
                for l_cand in latin_map.keys():
                    len_r = min(len(test_latin), len(l_cand)) / max(len(test_latin), len(l_cand))
                    if len_r < 0.60:
                        continue
                    sc = difflib.SequenceMatcher(None, test_latin, l_cand).ratio()
                    if sc > best_lat_score:
                        best_lat_score = sc
                        best_lat = l_cand

                if best_lat and best_lat_score >= 0.85:
                    matched_item = latin_map[best_lat]
                    kannada_text = matched_item["kannada"]
                    english_trans = matched_item.get("english_meaning", "")
                else:
                    # Step C: Word-by-word snapping if input has multiple words
                    words = kannada_text.split()
                    if len(words) > 1:
                        snapped_words = []
                        meanings = []
                        for w in words:
                            sw, sm = self._snap_single_word(w)
                            snapped_words.append(sw)
                            if sm:
                                meanings.append(sm)
                        kannada_text = " ".join(snapped_words)
                        english_trans = "; ".join(meanings)
                    else:
                        kannada_text, english_trans = self._snap_single_word(kannada_text)

            # Re-check dictionary with snapped word
            if not english_trans:
                dict_matches = lookup_tulu(kannada_text)

        # 5. Multi-Script Generation
        tigalari_text = kannada_to_tigalari(kannada_text)
        latin_text = kannada_to_latin(kannada_text)

        # 6. English Meaning / Translation resolution
        if not english_trans:
            if dict_matches:
                english_trans = dict_matches[0]["english"]
            else:
                if latin_text:
                    dict_matches = lookup_tulu(latin_text)
                    if dict_matches:
                        english_trans = dict_matches[0]["english"]
                if not english_trans:
                    # Leverage Full-Sentence Grammar Translator
                    try:
                        from kannada_tigalari_converter.nlp.sentence_translator import FullSentenceTranslator
                        s_res = FullSentenceTranslator.translate(kannada_text, source_lang="tulu")
                        if s_res and s_res.translated_text:
                            english_trans = s_res.translated_text
                    except Exception:
                        pass
                if not english_trans:
                    # Fallback to morphology analysis
                    morph = morph_analyze(kannada_text)
                    if morph.english_meaning:
                        english_trans = morph.english_meaning

        if kannada_text != canonical_recognition:
            confidence = min(confidence, 0.5)

        latency = (time.time() - start_time) * 1000.0

        return TuluASRResult(
            kannada=kannada_text,
            tigalari=tigalari_text,
            latin=latin_text,
            english=english_trans,
            confidence=confidence,
            latency_ms=latency,
            device=self.device,
            audio_duration_sec=duration_sec,
        )

    @staticmethod
    def _read_adapter_wer(summary_path: str) -> Optional[float]:
        try:
            with open(summary_path, "r", encoding="utf-8") as summary_file:
                return float(json.load(summary_file)["history"]["eval_metrics"]["wer"])
        except (OSError, ValueError, KeyError, TypeError):
            return None

    @staticmethod
    def _adapter_wer_is_usable(wer: Optional[float]) -> bool:
        return wer is not None and math.isfinite(wer) and 0.0 <= wer < 1.0

    @staticmethod
    def _generation_confidence(generated: Any) -> float:
        """Return mean selected-token probability; this is not a calibrated WER estimate."""
        scores = getattr(generated, "scores", None)
        sequences = getattr(generated, "sequences", None)
        if torch is None or not scores or sequences is None:
            return 0.0
        try:
            token_ids = sequences[:, -len(scores):]
            log_probabilities = []
            for step, logits in enumerate(scores):
                step_log_probs = torch.log_softmax(logits.float(), dim=-1)
                chosen = step_log_probs.gather(1, token_ids[:, step:step + 1])
                log_probabilities.append(chosen.squeeze(1))
            confidence = torch.stack(log_probabilities, dim=1).mean().exp().item()
            return float(min(1.0, max(0.0, confidence)))
        except (AttributeError, IndexError, RuntimeError, TypeError, ValueError):
            return 0.0

    def _snap_single_word(self, w: str) -> Tuple[str, str]:
        """Snaps an individual word phonetically against the known Tulu lexicon."""
        if not w:
            return w, ""
        import difflib
        from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000
        from kannada_tigalari_converter.lexicon.tulu_dictionary import lookup_tulu

        d = lookup_tulu(w)
        exact = next(
            (entry for entry in d if entry.get("tulu_kannada") == w or entry.get("inflected_form") == w),
            None,
        )
        if exact:
            return w, exact["english"]

        w_latin = kannada_to_latin(w).lower().strip()
        latin_map = {item["latin_phonetic"].lower(): item for item in WORDS_DATASET_1000}
        m_lat = difflib.get_close_matches(w_latin, latin_map.keys(), n=1, cutoff=0.85)
        if m_lat:
            item = latin_map[m_lat[0]]
            return item["kannada"], item.get("english_meaning", "")

        kn_map = {item["kannada"]: item for item in WORDS_DATASET_1000}
        m_kn = difflib.get_close_matches(w, kn_map.keys(), n=1, cutoff=0.85)
        if m_kn:
            item = kn_map[m_kn[0]]
            return item["kannada"], item.get("english_meaning", "")

        return w, ""
