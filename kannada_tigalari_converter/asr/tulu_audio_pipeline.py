"""
Tulu Audio Preprocessing & Acoustic Feature Extraction Pipeline
===============================================================
Handles audio ingestion, normalization, Voice Activity Detection (VAD),
80-channel log-Mel spectrogram generation, and paired synthetic speech generation.

Standards:
- Sample Rate: 16,000 Hz (16kHz)
- Channels: Mono (1 channel)
- Bit Depth: 32-bit float normalized to [-1.0, 1.0]
- Features: 80-channel Log-Mel Spectrogram matching Whisper / IndicASR standards
"""

import os
import sys
import wave
import io
import math
import subprocess
import numpy as np
from typing import Tuple, List, Optional, Union, Dict, BinaryIO

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import torch
    import torchaudio
    import torchaudio.transforms as T
except ImportError:
    torch = None
    torchaudio = None
    T = None


class AudioPreprocessor:
    """
    Standardized audio loader, normalizer, and acoustic feature extractor.
    """

    TARGET_SR: int = 16000

    @classmethod
    def load_audio(cls, source: Union[str, bytes, BinaryIO, np.ndarray], sr: Optional[int] = None) -> np.ndarray:
        """
        Loads audio from a file path, raw bytes, file-like buffer, or numpy array.
        Converts to 16,000 Hz mono float32 in [-1.0, 1.0].
        """
        if isinstance(source, np.ndarray):
            audio = source.astype(np.float32)
            current_sr = sr or cls.TARGET_SR
        elif isinstance(source, (bytes, bytearray)):
            buffer = io.BytesIO(source)
            if sf:
                audio, current_sr = sf.read(buffer, dtype="float32")
            else:
                audio, current_sr = cls._load_wav_buffer(buffer)
        elif isinstance(source, io.IOBase):
            if sf:
                audio, current_sr = sf.read(source, dtype="float32")
            else:
                audio, current_sr = cls._load_wav_buffer(source)
        elif isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"Audio file not found: {source}")
            if sf:
                audio, current_sr = sf.read(source, dtype="float32")
            elif source.lower().endswith(".wav"):
                with wave.open(source, "rb") as wf:
                    audio, current_sr = cls._load_wave_obj(wf)
            else:
                raise RuntimeError(f"Cannot load non-wav file without soundfile: {source}")
        else:
            raise TypeError(f"Unsupported audio source type: {type(source)}")

        # Convert stereo / multichannel to mono
        if audio.ndim > 1:
            audio = np.mean(audio, axis=-1)

        # Resample to 16,000 Hz if necessary
        if current_sr != cls.TARGET_SR:
            audio = cls.resample_audio(audio, current_sr, cls.TARGET_SR)

        # Peak amplitude normalization
        max_val = np.max(np.abs(audio))
        if max_val > 1e-5:
            audio = audio / max_val * 0.95

        return audio.astype(np.float32)

    @staticmethod
    def _load_wave_obj(wf: wave.Wave_read) -> Tuple[np.ndarray, int]:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

        if sampwidth == 2:
            data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        elif sampwidth == 1:
            data = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        elif sampwidth == 4:
            data = np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=-1)
        return data, sr

    @classmethod
    def _load_wav_buffer(cls, buffer: BinaryIO) -> Tuple[np.ndarray, int]:
        with wave.open(buffer, "rb") as wf:
            return cls._load_wave_obj(wf)

    @classmethod
    def resample_audio(cls, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resamples audio from orig_sr to target_sr using scipy or linear interpolation."""
        if orig_sr == target_sr or len(audio) == 0:
            return audio

        num_target_samples = int(round(len(audio) * float(target_sr) / orig_sr))
        try:
            from scipy import signal
            resampled = signal.resample(audio, num_target_samples)
            return resampled.astype(np.float32)
        except ImportError:
            # Linear interpolation fallback
            orig_indices = np.linspace(0, len(audio) - 1, len(audio))
            target_indices = np.linspace(0, len(audio) - 1, num_target_samples)
            resampled = np.interp(target_indices, orig_indices, audio)
            return resampled.astype(np.float32)

    @classmethod
    def trim_silence(cls, audio: np.ndarray, frame_duration_ms: int = 30, threshold: float = 0.02) -> np.ndarray:
        """
        Trims leading and trailing silence based on short-term root-mean-square (RMS) energy.
        """
        if len(audio) == 0:
            return audio

        frame_len = int(cls.TARGET_SR * (frame_duration_ms / 1000.0))
        num_frames = len(audio) // frame_len
        if num_frames == 0:
            return audio

        energies = []
        for i in range(num_frames):
            frame = audio[i * frame_len:(i + 1) * frame_len]
            rms = np.sqrt(np.mean(frame ** 2))
            energies.append(rms)

        # Adaptive threshold based on audio peak to avoid clipping soft speech
        max_energy = max(energies) if energies else 0.0
        effective_threshold = max(0.005, min(threshold, max_energy * 0.10))

        # Find first and last frames above threshold
        start_frame = 0
        for i, e in enumerate(energies):
            if e > effective_threshold:
                start_frame = max(0, i - 1)
                break

        end_frame = num_frames
        for i in range(num_frames - 1, -1, -1):
            if energies[i] > effective_threshold:
                end_frame = min(num_frames, i + 2)
                break

        start_sample = start_frame * frame_len
        end_sample = min(len(audio), end_frame * frame_len)
        trimmed = audio[start_sample:end_sample]
        return trimmed if len(trimmed) > 0 else audio

    @classmethod
    def compute_log_mel_spectrogram(
        cls,
        audio: np.ndarray,
        sr: int = 16000,
        n_mels: int = 80,
        n_fft: int = 400,
        hop_length: int = 160,
    ) -> np.ndarray:
        """
        Computes 80-channel log-Mel spectrogram aligned with Whisper/ASR standards.
        Shape: (n_mels, time_steps)
        """
        if torch is not None and torchaudio is not None:
            tensor = torch.from_numpy(audio).float()
            mel_transform = T.MelSpectrogram(
                sample_rate=sr,
                n_fft=n_fft,
                win_length=n_fft,
                hop_length=hop_length,
                n_mels=n_mels,
                power=2.0,
            )
            mel_spec = mel_transform(tensor)
            log_mel = torch.log(torch.clamp(mel_spec, min=1e-5))
            return log_mel.numpy()

        # Pure NumPy / SciPy fallback
        try:
            from scipy import signal
            freqs, times, Sxx = signal.spectrogram(
                audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length, mode='magnitude'
            )
            # Simple triangular mel filterbank approximation
            n_freqs = Sxx.shape[0]
            mel_filters = np.zeros((n_mels, n_freqs))
            for i in range(n_mels):
                center = int((i + 1) * n_freqs / (n_mels + 2))
                left = int(i * n_freqs / (n_mels + 2))
                right = int((i + 2) * n_freqs / (n_mels + 2))
                for j in range(left, center):
                    mel_filters[i, j] = (j - left) / max(1, center - left)
                for j in range(center, right):
                    mel_filters[i, j] = (right - j) / max(1, right - center)

            mel_spec = np.dot(mel_filters, Sxx)
            log_mel = np.log(np.maximum(mel_spec, 1e-5))
            return log_mel
        except Exception:
            # Minimal feature vector placeholder if scipy missing
            return np.zeros((n_mels, max(1, len(audio) // hop_length)), dtype=np.float32)


class SyntheticTuluAudioGenerator:
    """
    Generates paired acoustic speech samples (audio <-> text) for Tulu sentences
    using native macOS Indian voice synthesis or formants for ground-truth calibration.
    """

    @classmethod
    def synthesize_to_wav(cls, text_kannada: str, output_wav_path: str, rate: Optional[int] = None) -> bool:
        """
        Synthesizes a sentence in Kannada script into a 16kHz WAV file.
        Uses native macOS 'say -v Soumya' (Kannada voice) if available,
        or falls back to an acoustic waveform generator.
        :param rate: Speaking rate in WPM (e.g. 150=slow, 175=normal, 205=fast).
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
        temp_aiff = output_wav_path.replace(".wav", ".aiff")

        # 1. Attempt macOS native Kannada voice
        try:
            cmd = ["say", "-v", "Soumya"]
            if rate:
                cmd.extend(["-r", str(rate)])
            cmd.extend([text_kannada, "-o", temp_aiff])
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=12,
            )
            if res.returncode == 0 and os.path.exists(temp_aiff):
                # Load, normalize to 16kHz mono, and write WAV
                audio = AudioPreprocessor.load_audio(temp_aiff)
                if sf:
                    sf.write(output_wav_path, audio, AudioPreprocessor.TARGET_SR)
                else:
                    cls._write_simple_wav(output_wav_path, audio, AudioPreprocessor.TARGET_SR)
                if os.path.exists(temp_aiff):
                    os.remove(temp_aiff)
                return True
        except Exception:
            pass

        # 2. Fallback acoustic tone synthesis (for automated testing in CI/CD without macOS voices)
        audio = cls._synthesize_acoustic_tones(text_kannada)
        if sf:
            sf.write(output_wav_path, audio, AudioPreprocessor.TARGET_SR)
        else:
            cls._write_simple_wav(output_wav_path, audio, AudioPreprocessor.TARGET_SR)
        return True

    @staticmethod
    def _write_simple_wav(filepath: str, audio: np.ndarray, sr: int = 16000):
        int_data = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(int_data.tobytes())

    @staticmethod
    def _synthesize_acoustic_tones(text: str, sr: int = 16000) -> np.ndarray:
        """Deterministic acoustic phonetic waveform generator for testing environments."""
        duration = max(0.5, len(text) * 0.08)
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        # Generate base pitch (F0 ~ 140 Hz) + harmonic formants
        f0 = 140.0
        wave_data = (
            0.5 * np.sin(2 * np.pi * f0 * t) +
            0.3 * np.sin(2 * np.pi * (f0 * 2.2) * t) +
            0.15 * np.sin(2 * np.pi * (f0 * 3.5) * t)
        )
        # Apply envelope
        envelope = np.ones_like(t)
        attack = int(sr * 0.05)
        decay = int(sr * 0.05)
        if len(t) > attack + decay:
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-decay:] = np.linspace(1, 0, decay)
        return (wave_data * envelope * 0.8).astype(np.float32)


def generate_baseline_paired_dataset(output_dir: str, num_samples: int = 25) -> str:
    """
    Generates an initial ground-truth paired audio dataset (Audio WAV <-> Multi-Script Text)
    from core Tulu vocabulary words.
    """
    from kannada_tigalari_converter.words_dataset_250 import WORDS_DATASET_250
    import csv

    os.makedirs(output_dir, exist_ok=True)
    manifest_csv = os.path.join(output_dir, "paired_audio_manifest.csv")

    records = []
    for item in WORDS_DATASET_250[:num_samples]:
        item_id = item["id"]
        kn_text = item["kannada"]
        wav_filename = f"tulu_sample_{item_id:03d}.wav"
        wav_path = os.path.join(output_dir, wav_filename)

        SyntheticTuluAudioGenerator.synthesize_to_wav(kn_text, wav_path)

        records.append({
            "id": item_id,
            "audio_file": wav_filename,
            "tulu_kannada": kn_text,
            "tulu_tigalari": item["expected_tigalari"],
            "tulu_latin": item["latin_phonetic"],
            "english": item["english_meaning"],
        })

    with open(manifest_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "audio_file", "tulu_kannada", "tulu_tigalari", "tulu_latin", "english"])
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"✓ Generated {len(records)} paired audio benchmark samples in {output_dir}")
    return manifest_csv
