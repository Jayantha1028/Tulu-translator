"""
Unit Tests for Tulu Audio Processing Pipeline and Speech-to-Text (ASR) Engine.
==============================================================================
Tests audio ingestion, resampling, VAD silence trimming, log-Mel spectrograms,
synthetic voice generation, and multi-script transcription on Apple Silicon / CPU.
"""

import os
import sys
import tempfile
import unittest
import numpy as np

# Set project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.tulu_audio_pipeline import (
    AudioPreprocessor,
    SyntheticTuluAudioGenerator
)
from kannada_tigalari_converter.tulu_asr_engine import (
    TuluSpeechRecognizer,
    TuluASRResult
)


class TestAudioPreprocessor(unittest.TestCase):
    """Test suite for AudioPreprocessor loading and transformations."""

    def test_load_from_numpy_mono(self):
        # 1-second 440Hz sine wave at 16kHz
        sr = 16000
        t = np.linspace(0, 1.0, sr, endpoint=False)
        sine = 0.5 * np.sin(2 * np.pi * 440 * t)

        processed = AudioPreprocessor.load_audio(sine, sr=sr)
        self.assertEqual(len(processed), sr)
        self.assertAlmostEqual(np.max(np.abs(processed)), 0.95, places=2)
        self.assertEqual(processed.dtype, np.float32)

    def test_stereo_to_mono_conversion(self):
        sr = 16000
        stereo = np.zeros((sr, 2), dtype=np.float32)
        stereo[:, 0] = 0.4
        stereo[:, 1] = 0.6

        mono = AudioPreprocessor.load_audio(stereo, sr=sr)
        self.assertEqual(mono.ndim, 1)
        self.assertEqual(len(mono), sr)

    def test_resampling_linear(self):
        # 8kHz audio resampled to 16kHz
        orig_sr = 8000
        t = np.linspace(0, 0.5, orig_sr // 2, endpoint=False)
        audio = 0.6 * np.sin(2 * np.pi * 300 * t)

        resampled = AudioPreprocessor.resample_audio(audio, orig_sr=8000, target_sr=16000)
        self.assertEqual(len(resampled), 8000)  # 0.5s at 16kHz = 8000 samples

    def test_trim_silence(self):
        sr = 16000
        # 0.2s silence + 0.5s tone + 0.2s silence
        silence_prefix = np.zeros(int(0.2 * sr), dtype=np.float32)
        tone_t = np.linspace(0, 0.5, int(0.5 * sr), endpoint=False)
        tone = 0.8 * np.sin(2 * np.pi * 440 * tone_t).astype(np.float32)
        silence_suffix = np.zeros(int(0.2 * sr), dtype=np.float32)

        padded_audio = np.concatenate([silence_prefix, tone, silence_suffix])
        trimmed = AudioPreprocessor.trim_silence(padded_audio, threshold=0.02)

        # Trimmed length should be less than original padded length
        self.assertLess(len(trimmed), len(padded_audio))
        self.assertGreater(len(trimmed), int(0.4 * sr))

    def test_log_mel_spectrogram_shape(self):
        sr = 16000
        audio = np.random.randn(sr).astype(np.float32) * 0.1
        mel = AudioPreprocessor.compute_log_mel_spectrogram(audio, sr=sr, n_mels=80)

        self.assertEqual(mel.shape[0], 80)
        self.assertGreater(mel.shape[1], 10)


class TestSyntheticAudioGenerator(unittest.TestCase):
    """Test suite for paired synthetic speech generation."""

    def test_synthesize_wav_creation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_wav = os.path.join(tmpdir, "test_sample.wav")
            ok = SyntheticTuluAudioGenerator.synthesize_to_wav("ನಮಸ್ಕಾರ", out_wav)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(out_wav))
            self.assertGreater(os.path.getsize(out_wav), 1000)

            # Load synthesized audio through preprocessor
            audio = AudioPreprocessor.load_audio(out_wav)
            self.assertGreater(len(audio), 4000)
            self.assertEqual(audio.dtype, np.float32)


class TestTuluSpeechRecognizer(unittest.TestCase):
    """Test suite for Tulu Speech-to-Text ASR Engine."""

    @classmethod
    def setUpClass(cls):
        cls.recognizer = TuluSpeechRecognizer()

    def test_device_selection(self):
        # On modern Apple Silicon, should detect 'mps' or 'cpu'
        self.assertIn(self.recognizer.device, ["mps", "cuda", "cpu"])

    def test_transcribe_synthetic_sample(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "namaskara.wav")
            SyntheticTuluAudioGenerator.synthesize_to_wav("ನಮಸ್ಕಾರ", wav_path)

            result = self.recognizer.transcribe(wav_path)
            self.assertIsInstance(result, TuluASRResult)

            # Verify multi-script fields
            self.assertTrue(len(result.kannada) > 0)
            self.assertTrue(len(result.tigalari) > 0)
            self.assertTrue(len(result.latin) > 0)
            self.assertGreater(result.confidence, 0.0)
            self.assertGreater(result.latency_ms, 0.0)

            # Verify dictionary mapping
            result_dict = result.to_dict()
            self.assertIn("kannada", result_dict)
            self.assertIn("tigalari", result_dict)
            self.assertIn("latin", result_dict)
            self.assertIn("english", result_dict)
            self.assertIn("device", result_dict)

    def test_transcribe_audio_array(self):
        # Test directly with in-memory numpy array
        sr = 16000
        t = np.linspace(0, 0.5, int(0.5 * sr), endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 300 * t).astype(np.float32)

        result = self.recognizer.transcribe(audio)
        self.assertIsInstance(result, TuluASRResult)
        self.assertGreaterEqual(result.audio_duration_sec, 0.4)


if __name__ == "__main__":
    unittest.main()
