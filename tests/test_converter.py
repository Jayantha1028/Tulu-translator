"""
Unit tests for Tulu-Tigalari and Kannada Transliterator.
"""

import sys
import os
import unittest

# Ensure current directory and parent directory are on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from kannada_tigalari_converter.kannada_tigalari import (
        kannada_to_tigalari,
        tigalari_to_kannada,
        inspect_codepoints,
    )
    from kannada_tigalari_converter.tulu_phonetic import (
        latin_to_kannada,
        kannada_to_latin,
    )
    from kannada_tigalari_converter.transliterator import (
        transliterate,
        detect_script,
        latin_to_tigalari,
        tigalari_to_latin,
    )
except ImportError:
    from kannada_tigalari import (
        kannada_to_tigalari,
        tigalari_to_kannada,
        inspect_codepoints,
    )
    from tulu_phonetic import (
        latin_to_kannada,
        kannada_to_latin,
    )
    from transliterator import (
        transliterate,
        detect_script,
        latin_to_tigalari,
        tigalari_to_latin,
    )


class TestKannadaTigalariConverter(unittest.TestCase):

    def test_vowels(self):
        kannada_vowels = "ಅ ಆ ಇ ಈ ಉ ಊ ಋ ಎ ಏ ಐ ಒ ಓ ಔ"
        tigalari_vowels = kannada_to_tigalari(kannada_vowels)
        self.assertIn('\U00011380', tigalari_vowels)  # ಅ
        self.assertIn('\U00011381', tigalari_vowels)  # ಆ
        self.assertIn('\U00011382', tigalari_vowels)  # ಇ
        self.assertIn('\U00011383', tigalari_vowels)  # ಈ
        self.assertIn('\U00011384', tigalari_vowels)  # ಉ
        self.assertIn('\U00011385', tigalari_vowels)  # ಊ
        self.assertIn('\U0001138A', tigalari_vowels)  # Short E
        self.assertIn('\U0001138B', tigalari_vowels)  # Long EE
        self.assertIn('\U0001138F', tigalari_vowels)  # Short O
        self.assertIn('\U00011390', tigalari_vowels)  # Long OO

    def test_consonants(self):
        kannada_word = "ಕಮಲ"
        tigalari_word = kannada_to_tigalari(kannada_word)
        # ಕ: U+11392, ಮ: U+113AA, ಲ: U+113AD
        expected = '\U00011392\U000113AA\U000113AD'
        self.assertEqual(tigalari_word, expected)

    def test_conjuncts(self):
        # 'ನಮಸ್ಕಾರ' has ligature 'ಸ್ಕ್' (Sa + Halant + Ka)
        # Should contain CONJOINER U+113D0
        word = "ನಮಸ್ಕಾರ"
        converted = kannada_to_tigalari(word)
        self.assertIn('\U000113D0', converted)

        # 'ಕನ್ನಡ' has geminate 'ನ್ನ್' (Na + Halant + Na)
        word2 = "ಕನ್ನಡ"
        converted2 = kannada_to_tigalari(word2)
        self.assertIn('\U000113D0', converted2)

    def test_standalone_virama(self):
        # Word ending in halant (pure consonant), e.g., 'ಮಹಾನ್'
        word = "ಮಹಾನ್"
        converted = kannada_to_tigalari(word)
        # The final 'ನ್' should end with VIRAMA U+113CE, NOT CONJOINER U+113D0
        self.assertTrue(converted.endswith('\U000113CE'))

    def test_bidirectional_roundtrip(self):
        word = "ತುಳುನಾಡ ಧ್ವನಿ"
        converted = kannada_to_tigalari(word)
        restored = tigalari_to_kannada(converted)
        self.assertEqual(restored, word)

    def test_short_and_long_e_o_roundtrip(self):
        sample = "ಎದೆ ಏಣಿ ಒಲವು ಓಟ ಬೆಲೆ ಬೇಲಿ ಕೊಳ ಕೋಲು"
        converted = kannada_to_tigalari(sample)
        restored = tigalari_to_kannada(converted)
        self.assertEqual(restored, sample)

    def test_latin_to_kannada(self):
        self.assertEqual(latin_to_kannada("solmelu"), "ಸೊಲ್ಮೆಲು")
        self.assertEqual(latin_to_kannada("tuLu"), "ತುಳು")
        self.assertEqual(latin_to_kannada("dhvani"), "ಧ್ವನಿ")
        self.assertEqual(latin_to_kannada("barsa"), "ಬರ್ಸ")
        self.assertEqual(latin_to_kannada("enna"), "ಎನ್ನ")
        self.assertEqual(latin_to_kannada("pudar"), "ಪುದರ್")
        self.assertEqual(latin_to_kannada("kODae"), "ಕೋಡೆ್")

    def test_latin_to_tigalari_end_to_end(self):
        tig = latin_to_tigalari("solmelu")
        kan = tigalari_to_kannada(tig)
        self.assertEqual(kan, "ಸೊಲ್ಮೆಲು")

    def test_detect_script(self):
        self.assertEqual(detect_script("namaskara"), "latin")
        self.assertEqual(detect_script("ನಮಸ್ಕಾರ"), "kannada")
        tig = kannada_to_tigalari("ತುಳು")
        self.assertEqual(detect_script(tig), "tigalari")

    def test_unified_transliterate(self):
        # Auto-detect latin -> tigalari
        tig = transliterate("solmelu", from_script='auto', to_script='tigalari')
        self.assertIn('\U000113B1', tig)  # Sa
        # Auto-detect kannada -> latin
        lat = transliterate("ಸೊಲ್ಮೆಲು", from_script='auto', to_script='latin')
        self.assertIn("solmelu", lat.lower())

    def test_historical_dictionary(self):
        try:
            from kannada_tigalari_converter.historical_dictionary import HISTORICAL_TULU_CORPUS, search_historical_dictionary
        except ImportError:
            from historical_dictionary import HISTORICAL_TULU_CORPUS, search_historical_dictionary
        self.assertEqual(len(HISTORICAL_TULU_CORPUS), 204)
        results = search_historical_dictionary("agel")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["tulu_kannada"], "ಅಗೆಲ್")
        self.assertEqual(results[0]["part_of_speech"], "noun")
        paddy_results = search_historical_dictionary("", domain="Paddy Cultivation")
        self.assertGreater(len(paddy_results), 5)


if __name__ == '__main__':
    unittest.main()
