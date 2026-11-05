"""
Tulu Speech-to-Text (ASR) & Audio Processing Submodule
======================================================
Provides acoustic preprocessing (16kHz resampling, energy-based VAD,
80-channel log-Mel spectrograms, synthetic voice generator), neural
Speech-to-Text decoding with Apple Silicon MPS acceleration, and LoRA fine-tuning.
"""

from .tulu_audio_pipeline import (
    AudioPreprocessor,
    SyntheticTuluAudioGenerator,
)
from .tulu_asr_engine import (
    TuluSpeechRecognizer,
    TuluASRResult,
)
from .tulu_asr_trainer import (
    TuluASRTrainer,
    TuluSpeechDataset,
    train_tulu_asr,
)

__all__ = [
    "AudioPreprocessor",
    "SyntheticTuluAudioGenerator",
    "TuluSpeechRecognizer",
    "TuluASRResult",
    "TuluASRTrainer",
    "TuluSpeechDataset",
    "train_tulu_asr",
]
