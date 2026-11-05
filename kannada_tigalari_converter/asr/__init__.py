"""
Tulu Speech-to-Text (ASR) & Audio Processing Submodule
======================================================
Provides acoustic preprocessing (16kHz resampling, energy-based VAD,
80-channel log-Mel spectrograms, synthetic voice generator) and neural
Speech-to-Text decoding with Apple Silicon MPS acceleration.
"""

from .tulu_audio_pipeline import (
    AudioPreprocessor,
    SyntheticTuluAudioGenerator,
)
from .tulu_asr_engine import (
    TuluSpeechRecognizer,
    TuluASRResult,
)

__all__ = [
    "AudioPreprocessor",
    "SyntheticTuluAudioGenerator",
    "TuluSpeechRecognizer",
    "TuluASRResult",
]
