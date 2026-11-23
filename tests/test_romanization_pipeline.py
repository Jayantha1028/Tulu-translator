#!/usr/bin/env python3
"""
Unit Tests for Canonical ASCII Romanization Pipeline
====================================================
Tests the complete migration to ASCII-only representations across:
  1. Canonical Romanization Scheme (phonemes, 'ae' diacritic, retroflexes, roundtrips)
  2. Romanized Datasets (Master corpus, Lexicons, KN-EN parallel corpus)
  3. Rebuilt ASCII-only Tokenizer (Zero Indic/Tigalari codepoints in vocabulary)
  4. End-to-end Romanized Tulu -> Kannada MT
  5. Romanized Kannada -> English MT
  6. Rebuilt Multi-Language TTS Engine (Tulu, Kannada, English profiles)
"""

import os
import sys
import unittest
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.lexicon.romanization_scheme import (
    to_canonical_roman,
    from_canonical_roman,
    CANONICAL_PHONEME_TOKENS,
)
from kannada_tigalari_converter.nlp.tulu_tokenizer_tool import TuluTokenizerTool
from kannada_tigalari_converter.nlp.sentence_translator import FullSentenceTranslator
from kannada_tigalari_converter.nlp.kn_en_translator import KannadaEnglishTranslator
from kannada_tigalari_converter.asr.tulu_tts_engine import TuluTTSEngine


class TestCanonicalRomanizationScheme(unittest.TestCase):
    """Verifies that the canonical ASCII mapping locks correctly."""

    def test_basic_phoneme_roundtrips(self):
        samples = [
            ("ಸೊಲ್ಮೆಲು", "solmelu"),
            ("ನಮಸ್ಕಾರ", "namaskaara"),
            ("ಬರ್ಪೆರ್", "barper"),
            ("ಆರೋಗ್ಯ", "aarOgya"),
            ("ಭಗವಂತ", "bhagavaMta"),
        ]
        for kn, expected_rom in samples:
            rom = to_canonical_roman(kn)
            self.assertEqual(rom, expected_rom)
            back = from_canonical_roman(rom, to_script="kannada")
            self.assertEqual(back, kn)

    def test_tulu_open_ae_diacritic(self):
        # Tulu open-e sound (Kannada: ೆ್, Baraha/ITRANS: ae)
        kn = "ಕೋಡೆ್"
        rom = to_canonical_roman(kn)
        self.assertEqual(rom, "kODae")
        back = from_canonical_roman(rom, to_script="kannada")
        self.assertEqual(back, kn)

    def test_retroflexes_and_special_consonants(self):
        # ಳ (L), ಱ (rr), ೞ (zh), ಣ (N)
        self.assertEqual(to_canonical_roman("ಕಾಲ"), "kaala")
        self.assertEqual(to_canonical_roman("ಕಾಳ"), "kaaLa")
        self.assertEqual(to_canonical_roman("ಹಣ್ಣು"), "haNNu")

    def test_canonical_tokens_pure_ascii(self):
        tokens = CANONICAL_PHONEME_TOKENS
        for tok in tokens:
            self.assertTrue(all(ord(c) < 128 for c in tok), f"Token '{tok}' is not pure ASCII!")


class TestRomanizedDatasets(unittest.TestCase):
    """Verifies that batch romanization generated valid datasets."""

    def test_master_corpus_romanized_exists(self):
        path = os.path.join(BASE_DIR, "datasets", "tulu_master_corpus_romanized.csv")
        self.assertTrue(os.path.isfile(path), "tulu_master_corpus_romanized.csv missing")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [next(reader) for _ in range(5)]
            self.assertEqual(len(rows), 5)
            self.assertIn("tulu_romanized", rows[0])
            self.assertIn("english_translation", rows[0])

    def test_kn_en_parallel_romanized_exists(self):
        path = os.path.join(BASE_DIR, "datasets", "kn_en_parallel_romanized.csv")
        self.assertTrue(os.path.isfile(path), "kn_en_parallel_romanized.csv missing")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)
            self.assertIn("kannada_romanized", first_row)
            self.assertIn("english", first_row)

    def test_historical_gold_25k_dataset_integrity(self):
        path = os.path.join(BASE_DIR, "datasets", "tulu_historical_gold_25k.csv")
        self.assertTrue(os.path.isfile(path), "tulu_historical_gold_25k.csv missing")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertIn("tulu_kannada", reader.fieldnames)
            self.assertIn("tulu_romanized", reader.fieldnames)
            self.assertIn("english", reader.fieldnames)
            self.assertIn("source", reader.fieldnames)
            count = sum(1 for _ in reader)
            self.assertEqual(count, 25000)

    def test_single_source_of_truth_integrity(self):
        path = os.path.join(BASE_DIR, "datasets", "tulu_master_single_source_of_truth.csv")
        self.assertTrue(os.path.isfile(path), "tulu_master_single_source_of_truth.csv missing")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Verify primary / lead column is tulu_tigalari
            self.assertEqual(reader.fieldnames[0], "tulu_tigalari")
            self.assertIn("tulu_kannada", reader.fieldnames)
            self.assertIn("tulu_latin", reader.fieldnames)
            self.assertIn("english_translation", reader.fieldnames)
            self.assertIn("corpus_source", reader.fieldnames)

            # Check 100 sample rows across the dataset
            sample_count = 0
            for row in reader:
                sample_count += 1
                tig = row["tulu_tigalari"].strip()
                en = row["english_translation"].strip()
                self.assertTrue(bool(tig), "tulu_tigalari must not be null or empty")
                self.assertTrue(bool(en), "english_translation must not be null or empty")
                # Verify Tigalari codepoints (Unicode 16.0: 0x11380 - 0x113FF)
                self.assertTrue(any(0x11380 <= ord(c) <= 0x113FF for c in tig))
                if sample_count >= 100:
                    break
            self.assertGreaterEqual(sample_count, 100)


class TestRomanizedTokenizer(unittest.TestCase):
    """Verifies that the tokenizer vocabulary contains strictly zero Indic/Tigalari codepoints."""

    def test_tokenizer_pure_ascii_vocabulary(self):
        tokens = TuluTokenizerTool.get_canonical_roman_tokens()
        self.assertGreater(len(tokens), 30)
        for t in tokens:
            for c in t:
                self.assertLess(ord(c), 128, f"Character '{c}' in token '{t}' is not ASCII!")

    def test_export_token_catalog(self):
        path = os.path.join(BASE_DIR, "datasets", "test_custom_tokens.json")
        try:
            exported = TuluTokenizerTool.export_token_catalog(path)
            self.assertTrue(os.path.isfile(exported))
        finally:
            if os.path.exists(path):
                os.remove(path)


class TestTuluToKannadaRomanizedMT(unittest.TestCase):
    """Verifies end-to-end Romanized Tulu -> Romanized Kannada translation."""

    def test_sentence_tulu_to_kannada_romanized(self):
        res = FullSentenceTranslator.translate_tulu_to_kannada("yaan illag barpe")
        self.assertEqual(res.source_lang, "tulu")
        self.assertEqual(res.tulu_romanized, "yaan illag barpe")
        self.assertIn("naanu", res.kannada_romanized)
        self.assertIn("manege", res.kannada_romanized)
        self.assertIn("baruttEne", res.kannada_romanized)

    def test_question_tulu_to_kannada_romanized(self):
        res = FullSentenceTranslator.translate_tulu_to_kannada("eer olpa poopar?")
        self.assertIn("neevu", res.kannada_romanized)
        self.assertIn("ellige", res.kannada_romanized)


class TestKannadaEnglishTranslator(unittest.TestCase):
    """Verifies Romanized Kannada -> English Machine Translation."""

    def setUp(self):
        self.translator = KannadaEnglishTranslator()

    def test_translate_phrases(self):
        out1 = self.translator.translate("nimma hesareenu?")
        self.assertIn("name", out1.lower())

        out2 = self.translator.translate("tumbaa dhanyavaadagaLu")
        self.assertIn("thank", out2.lower())

    def test_translate_kannada_script_input(self):
        # Native Kannada script is automatically converted to canonical Roman
        out = self.translator.translate("ನಿಮ್ಮ ಹೆಸರೇನು?")
        self.assertIn("name", out.lower())


class TestMultiLanguageTTS(unittest.TestCase):
    """Verifies TTS formant synthesis across Tulu, Kannada, and English phoneme sets."""

    def test_tulu_speech_synthesis(self):
        res = TuluTTSEngine.synthesize_speech("solmelu", language="tulu")
        self.assertTrue(res["success"])
        self.assertEqual(res["language_profile"], "tulu")
        self.assertTrue(len(res["audio_base64"]) > 100)

    def test_kannada_speech_synthesis(self):
        res = TuluTTSEngine.synthesize_speech("namaskaara", language="kannada")
        self.assertTrue(res["success"])
        self.assertEqual(res["language_profile"], "kannada")
        self.assertTrue(len(res["audio_base64"]) > 100)

    def test_english_speech_synthesis(self):
        res = TuluTTSEngine.synthesize_speech("Thank you very much", language="english")
        self.assertTrue(res["success"])
        self.assertEqual(res["language_profile"], "english")
        self.assertTrue(len(res["audio_base64"]) > 100)


if __name__ == "__main__":
    unittest.main()
