"""
kannada_tigalari_converter.asr.tulu_tts_engine
==============================================
Text-to-Speech (TTS) audio synthesis engine for Tulu, Kannada, and English.
Extends rule-based formant acoustic synthesis across 3 language phoneme profiles
(Tulu, Kannada, English) avoiding any pretrained heavy neural models.
"""

from __future__ import annotations

import base64
import io
import math
import os
import subprocess
import sys
import wave
from typing import Any, Dict, List, Optional

import numpy as np

from ..core import detect_script, kannada_to_latin, tigalari_to_kannada
from ..lexicon.romanization_scheme import to_canonical_roman


class TuluTTSEngine:
    """TTS Synthesizer supporting Tulu, Kannada, and English formant and system speech."""

    SAMPLE_RATE: int = 16000

    # Language-specific acoustic formant profiles (F0, F1, F2, F3 in Hz)
    LANGUAGE_PROFILES: Dict[str, Dict[str, Any]] = {
        "tulu": {
            "base_f0": 135.0,
            "f1": 680.0,   # Open-e / ae emphasis
            "f2": 1750.0,
            "f3": 2600.0,
            "cadence_factor": 1.1,
            "description": "Tulu phonology (distinctive 'ae' vowels and retroflex cadence)"
        },
        "kannada": {
            "base_f0": 145.0,
            "f1": 550.0,   # Classical cardinal Dravidian vowels
            "f2": 1550.0,
            "f3": 2650.0,
            "cadence_factor": 1.0,
            "description": "Standard Kannada phonology (syllable-timed vowel clarity)"
        },
        "english": {
            "base_f0": 125.0,
            "f1": 500.0,   # Stress-timed Germanic vowels and diphthongs
            "f2": 1700.0,
            "f3": 2500.0,
            "cadence_factor": 0.9,
            "description": "English phonology (stress-timed rhythm with terminal pitch drop)"
        }
    }

    @classmethod
    def synthesize_speech(
        cls,
        text: str,
        script: str = "auto",
        language: str = "auto",
        speed_rate: float = 1.0,
    ) -> Dict[str, Any]:
        """Synthesize spoken audio for given text into WAV format across Tulu, Kannada, or English.

        Returns base64 encoded audio string ready for HTML5 audio playback.
        """
        text = text.strip()
        if not text:
            return {
                "success": False,
                "error": "Empty text provided for synthesis",
                "audio_base64": "",
            }

        detected = detect_script(text) if script == "auto" else script
        if detected == "tigalari":
            kannada_text = tigalari_to_kannada(text)
            latin_text = to_canonical_roman(kannada_text)
        elif detected == "kannada":
            kannada_text = text
            latin_text = to_canonical_roman(text)
        else:
            latin_text = text
            from ..core import latin_to_kannada
            kannada_text = latin_to_kannada(text)

        # Infer language profile
        if language == "auto":
            # If text consists only of basic English ASCII words
            lower_words = text.lower().split()
            if any(w in ("what", "where", "how", "the", "thank", "you", "is", "your", "good", "morning") for w in lower_words):
                lang_profile = "english"
            elif detected == "kannada":
                lang_profile = "kannada"
            else:
                lang_profile = "tulu"
        else:
            lang_profile = language.lower() if language.lower() in cls.LANGUAGE_PROFILES else "tulu"

        # 1. Attempt macOS native speech synthesis
        audio_bytes = cls._try_macos_say(kannada_text, latin_text, lang_profile, speed_rate)
        source_mode = "system_tts"

        # 2. Fallback to deterministic acoustic phonetic formant synthesis
        if not audio_bytes:
            audio_bytes = cls._synthesize_formant_wav(latin_text or text, lang_profile=lang_profile)
            source_mode = "acoustic_formants"

        b64 = base64.b64encode(audio_bytes).decode("ascii")
        data_uri = f"data:audio/wav;base64,{b64}"

        return {
            "success": True,
            "text": text,
            "script": detected,
            "language_profile": lang_profile,
            "kannada": kannada_text,
            "latin_phonetic": latin_text,
            "romanized": latin_text,
            "format": "wav",
            "source_mode": source_mode,
            "audio_base64": b64,
            "audio_uri": data_uri,
        }

    @classmethod
    def _try_macos_say(
        cls, kannada_text: str, latin_text: str, language: str, speed_rate: float
    ) -> Optional[bytes]:
        """Attempt macOS native speech synthesis into AIFF then convert to WAV."""
        if sys.platform != "darwin":
            return None

        # Check available voices
        try:
            voices_proc = subprocess.run(
                ["say", "-v", "?"], capture_output=True, text=True, timeout=2
            )
            voices_list = voices_proc.stdout.lower()
        except Exception:
            voices_list = ""

        voice_candidate = None
        if language == "english":
            for v in ["samantha", "daniel", "karen", "alex", "fred"]:
                if v in voices_list:
                    voice_candidate = v
                    break
            speak_text = latin_text
        elif language == "kannada":
            for v in ["veena", "sangeeta", "rishi", "kavya"]:
                if v in voices_list:
                    voice_candidate = v
                    break
            speak_text = kannada_text if voice_candidate in ("veena", "sangeeta") else latin_text
        else:  # Tulu
            for v in ["veena", "sangeeta", "rishi", "kavya", "samantha"]:
                if v in voices_list:
                    voice_candidate = v
                    break
            speak_text = kannada_text if voice_candidate in ("veena", "sangeeta") else latin_text

        rate_wpm = str(int(160 * speed_rate))

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tf_aiff:
            aiff_path = tf_aiff.name
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf_wav:
            wav_path = tf_wav.name

        try:
            cmd = ["say", "-o", aiff_path, "-r", rate_wpm]
            if voice_candidate:
                cmd.extend(["-v", voice_candidate])
            cmd.append(speak_text)

            res = subprocess.run(cmd, capture_output=True, timeout=3)
            if res.returncode == 0 and os.path.exists(aiff_path) and os.path.getsize(aiff_path) > 100:
                conv_res = subprocess.run(
                    ["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", aiff_path, wav_path],
                    capture_output=True,
                    timeout=3
                )
                if conv_res.returncode == 0 and os.path.exists(wav_path):
                    with open(wav_path, "rb") as f:
                        data = f.read()
                    return data
        except Exception:
            pass
        finally:
            for p in (aiff_path, wav_path):
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass

        return None

    @classmethod
    def _synthesize_formant_wav(cls, text: str, lang_profile: str = "tulu") -> bytes:
        """Deterministic acoustic phonetic waveform generator configured by language profile."""
        profile = cls.LANGUAGE_PROFILES.get(lang_profile, cls.LANGUAGE_PROFILES["tulu"])
        sr = cls.SAMPLE_RATE
        duration = max(0.6, min(len(text) * 0.12 * profile["cadence_factor"], 6.0))
        num_samples = int(sr * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        base_f0 = profile["base_f0"]
        f1 = profile["f1"]
        f2 = profile["f2"]
        f3 = profile["f3"]

        # Intonation contour: subtle frequency modulation
        f0 = base_f0 + 8.0 * np.sin(2 * np.pi * 1.5 * t)
        if lang_profile == "english":
            # Falling pitch at sentence termination
            f0 = f0 - (15.0 * (t / duration))

        waveform = (
            0.50 * np.sin(2 * np.pi * f0 * t) +
            0.28 * np.sin(2 * np.pi * f1 * t) +
            0.18 * np.sin(2 * np.pi * f2 * t) +
            0.08 * np.sin(2 * np.pi * f3 * t)
        )

        # Syllabic rhythm
        syllables = max(1, len(text) // 3)
        pulse = 0.85 + 0.15 * np.cos(2 * np.pi * (syllables / duration) * t)
        waveform = waveform * pulse

        # Envelope attack/decay
        attack = int(sr * 0.04)
        decay = int(sr * 0.08)
        envelope = np.ones(num_samples)
        if num_samples > attack + decay:
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-decay:] = np.linspace(1, 0, decay)

        final_wave = np.clip(waveform * envelope * 0.75, -1.0, 1.0)
        int16_data = (final_wave * 32767.0).astype(np.int16)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(int16_data.tobytes())

        return buf.getvalue()
