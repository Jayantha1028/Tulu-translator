"""
Unit Tests for Tulu Full-Sentence Bidirectional Grammar Translator
=================================================================
Tests SOV <-> SVO structural translation, morphological case resolution,
verb conjugations, and multi-script Tigalari output.
"""

import unittest
from kannada_tigalari_converter.nlp.sentence_translator import (
    FullSentenceTranslator,
    TranslationResult,
)


class TestFullSentenceTranslator(unittest.TestCase):
    """Test suite for sentence-level grammar translation."""

    def test_01_tulu_to_english_sov(self):
        """Tests that Tulu SOV sentence 'ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ' translates to English SVO."""
        res = FullSentenceTranslator.translate("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ")
        self.assertEqual(res.source_lang, "tulu")
        self.assertIn("coming", res.translated_text.lower())
        self.assertIn("house", res.translated_text.lower())
        self.assertTrue(len(res.tulu_tigalari) > 0)
        self.assertTrue(len(res.tulu_latin) > 0)

    def test_02_tulu_to_english_question(self):
        """Tests question translation: 'ಈರ್ ಒಲ್ಪ ಪೋಪರ್'."""
        res = FullSentenceTranslator.translate("ಈರ್ ಒಲ್ಪ ಪೋಪರ್")
        self.assertEqual(res.source_lang, "tulu")
        self.assertTrue(res.translated_text.endswith("?"))
        self.assertIn("where", res.translated_text.lower())

    def test_03_conversational_idioms(self):
        """Tests common conversational Tulu greetings and idioms."""
        cases = [
            ("ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು", "Warm heart greetings unto all!"),
            ("ಚಾ ಪರಿಂಡಾ", "Did you have tea?"),
            ("ಕೋಡೆ್ ಮಲ್ಲ ಬರ್ಸ ಬತ್ತ್ಂಡ್", "Yesterday heavy rain arrived"),
            ("ಇನಿ ಬರ್ಸ ಬರ್ಪುಂಡು", "It will rain today"),
        ]
        for tulu_in, expected_sub in cases:
            res = FullSentenceTranslator.translate(tulu_in)
            self.assertEqual(res.source_lang, "tulu")
            self.assertIn(expected_sub.lower(), res.translated_text.lower())

    def test_04_english_to_tulu_sov(self):
        """Tests English SVO -> Tulu SOV sentence generation."""
        cases = [
            ("Where are you going?", "ಈರ್ ಓಡೆಗ್ ಪೋಪರ್"),
            ("I am going to the house", "ಯಾನ್ ಇಲ್ಲಗ್ ಪೋಪೆ"),
            ("What is your name?", "ಈರೆನ ಪುದರ್ ದಾನೆ"),
        ]
        for eng_in, expected_tulu in cases:
            res = FullSentenceTranslator.translate(eng_in)
            self.assertEqual(res.source_lang, "english")
            self.assertEqual(res.tulu_kannada, expected_tulu)
            self.assertTrue(len(res.tulu_tigalari) > 0)
            self.assertTrue(len(res.tulu_latin) > 0)

    def test_05_dative_and_locative_cases(self):
        """Tests that 'to house' produces Dative (-ಗ್) and 'in house' produces Locative (-ಡ್)."""
        res_dat = FullSentenceTranslator.translate("I am going to the house")
        self.assertIn("ಇಲ್ಲಗ್", res_dat.tulu_kannada)

        res_loc = FullSentenceTranslator.translate("ಯಾನ್ ಇಲ್ಲಡ್ ಉಲ್ಲೆ")
        self.assertTrue("home" in res_loc.translated_text.lower() or "house" in res_loc.translated_text.lower())

    def test_06_tigalari_script_fidelity(self):
        """Ensures that every translated sentence includes valid official Unicode 16.0 Tigalari."""
        res = FullSentenceTranslator.translate("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ")
        # Unicode 16.0 Tigalari codepoint range U+11380–U+113FF
        tigalari_chars = [c for c in res.tulu_tigalari if 0x11380 <= ord(c) <= 0x113FF]
        self.assertTrue(len(tigalari_chars) >= 4)

    def test_07_empty_and_whitespace(self):
        """Handles empty string gracefully without error."""
        res = FullSentenceTranslator.translate("   ")
        self.assertEqual(res.translated_text, "")
        self.assertEqual(res.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
