"""
Unit Tests for Text-to-Speech (TTS), Neural SLM / Hybrid Translator,
LoRA Dataset Exporter, and PWA Offline Assets.
"""

import json
import os
import unittest

from kannada_tigalari_converter.asr.tulu_tts_engine import TuluTTSEngine
from kannada_tigalari_converter.nlp.neural_translator import (
    NeuralTuluTranslator,
    NeuralTranslationResult,
)


class TestTuluTTSEngine(unittest.TestCase):
    def test_synthesize_speech_kannada(self):
        res = TuluTTSEngine.synthesize_speech("ನಮಸ್ಕಾರ", script="kannada")
        self.assertTrue(res["success"])
        self.assertIn("audio_base64", res)
        self.assertTrue(len(res["audio_base64"]) > 50)
        self.assertTrue(res["audio_uri"].startswith("data:audio/wav;base64,"))
        self.assertEqual(res["format"], "wav")

    def test_synthesize_speech_tigalari(self):
        # Tigalari input gets converted to Kannada/Latin and synthesized
        res = TuluTTSEngine.synthesize_speech("𑎂𑎭𑏐𑎭", script="tigalari")
        self.assertTrue(res["success"])
        self.assertTrue(len(res["audio_base64"]) > 50)

    def test_synthesize_empty_string(self):
        res = TuluTTSEngine.synthesize_speech("   ")
        self.assertFalse(res["success"])


class TestNeuralTuluTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = NeuralTuluTranslator(preferred_engine="rule_based")

    def test_rule_based_translation(self):
        res = self.translator.translate("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ", force_engine="rule_based")
        self.assertIsInstance(res, NeuralTranslationResult)
        self.assertEqual(res.engine_used, "rule_based")
        self.assertIn("house", res.translated_text.lower())
        self.assertTrue(len(res.tulu_tigalari) > 0)

    def test_hybrid_fallback(self):
        # Hybrid engine when local SLM is offline gracefully falls back
        hybrid_trans = NeuralTuluTranslator(preferred_engine="hybrid")
        res = hybrid_trans.translate("I am going home", source_lang="english")
        self.assertTrue(len(res.translated_text) > 0)
        self.assertIn(res.engine_used, ("rule_based", "hybrid_fallback", "neural_slm"))

    def test_export_lora_sft_dataset(self):
        test_out = "/tmp/test_tulu_lora_sft.jsonl"
        count = NeuralTuluTranslator.export_lora_sft_dataset(test_out)
        self.assertGreater(count, 100)
        self.assertTrue(os.path.exists(test_out))

        # Validate line formatting
        with open(test_out, "r", encoding="utf-8") as f:
            first_line = json.loads(f.readline())
            self.assertIn("instruction", first_line)
            self.assertIn("input", first_line)
            self.assertIn("output", first_line)

        if os.path.exists(test_out):
            os.remove(test_out)


class TestPWAAssets(unittest.TestCase):
    def test_manifest_and_sw_exist(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        manifest_path = os.path.join(base_dir, "web", "manifest.json")
        sw_path = os.path.join(base_dir, "web", "sw.js")
        icon192 = os.path.join(base_dir, "web", "icons", "icon-192.png")
        icon512 = os.path.join(base_dir, "web", "icons", "icon-512.png")

        self.assertTrue(os.path.exists(manifest_path), "manifest.json missing")
        self.assertTrue(os.path.exists(sw_path), "sw.js missing")
        self.assertTrue(os.path.exists(icon192), "icon-192.png missing")
        self.assertTrue(os.path.exists(icon512), "icon-512.png missing")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            self.assertEqual(manifest["display"], "standalone")
            self.assertEqual(len(manifest["icons"]), 2)


if __name__ == "__main__":
    unittest.main()
