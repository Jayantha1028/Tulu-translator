"""
Comprehensive 1,000-Word Unit Test Suite for Tulu-Tigalari & Kannada Transliteration.
Compares 1,000 real-world input words across 19 categories, validating:
  1. Kannada -> Tigalari Unicode 16.0 fidelity (1,000 words)
  2. Tigalari -> Kannada 100% lossless roundtrip (1,000 words)
  3. Latin Phonetic -> Kannada accuracy (1,000 words)
  4. End-to-end Latin -> Tigalari conversion (1,000 words)
  5. Script auto-detection (3,000 script checks)
  6. Category coverage across 19 distinct domains
"""

import sys
import os
import unittest

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
    from kannada_tigalari_converter.words_dataset_1000 import WORDS_DATASET_1000
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
    from words_dataset_1000 import WORDS_DATASET_1000


class Test1000WordsFidelity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.total_words = len(WORDS_DATASET_1000)
        assert cls.total_words == 1000, f"Expected 1000 words, found {cls.total_words}"
        print(f"\n[Test Setup] Loaded {cls.total_words} validation words across 19 categories.")

    def test_01_dataset_integrity(self):
        """Verifies that dataset has 1,000 unique items with all required keys."""
        self.assertEqual(len(WORDS_DATASET_1000), 1000)
        seen_ids = set()
        for item in WORDS_DATASET_1000:
            self.assertIn("id", item)
            self.assertIn("latin_phonetic", item)
            self.assertIn("kannada", item)
            self.assertIn("english_meaning", item)
            self.assertIn("category", item)
            self.assertIn("expected_tigalari", item)
            self.assertNotIn(item["id"], seen_ids)
            seen_ids.add(item["id"])

    def test_02_kannada_to_tigalari_all_1000(self):
        """Tests that Kannada text converts to official Unicode 16.0 Tigalari for all 1,000 words."""
        mismatches = []
        for w in WORDS_DATASET_1000:
            actual = kannada_to_tigalari(w["kannada"])
            if actual != w["expected_tigalari"]:
                mismatches.append((w["id"], w["kannada"], w["expected_tigalari"], actual))
        
        self.assertEqual(
            len(mismatches), 0,
            f"Encountered {len(mismatches)} mismatches in Kannada -> Tigalari: {mismatches[:3]}"
        )

    def test_03_tigalari_to_kannada_roundtrip_all_1000(self):
        """Tests 100% lossless reverse roundtrip from Tigalari back to Kannada for all 1,000 words."""
        mismatches = []
        for w in WORDS_DATASET_1000:
            tig = w["expected_tigalari"]
            restored = tigalari_to_kannada(tig)
            if restored != w["kannada"]:
                mismatches.append((w["id"], w["kannada"], restored))

        self.assertEqual(
            len(mismatches), 0,
            f"Encountered {len(mismatches)} roundtrip failures: {mismatches[:3]}"
        )

    def test_04_latin_phonetic_to_kannada_all_1000(self):
        """Tests that Baraha/ITRANS Latin phonetic input converts to exact Kannada for all 1,000 words."""
        mismatches = []
        for w in WORDS_DATASET_1000:
            actual = latin_to_kannada(w["latin_phonetic"])
            if actual != w["kannada"]:
                mismatches.append((w["id"], w["latin_phonetic"], w["kannada"], actual))

        self.assertEqual(
            len(mismatches), 0,
            f"Encountered {len(mismatches)} phonetic transliteration mismatches: {mismatches[:3]}"
        )

    def test_05_end_to_end_latin_to_tigalari_all_1000(self):
        """Tests complete Latin -> Kannada -> Tigalari end-to-end pipeline for all 1,000 words."""
        mismatches = []
        for w in WORDS_DATASET_1000:
            actual = latin_to_tigalari(w["latin_phonetic"])
            if actual != w["expected_tigalari"]:
                mismatches.append((w["id"], w["latin_phonetic"], w["expected_tigalari"], actual))

        self.assertEqual(
            len(mismatches), 0,
            f"Encountered {len(mismatches)} end-to-end mismatches: {mismatches[:3]}"
        )

    def test_06_script_auto_detection_all_1000(self):
        """Tests that script auto-detection accurately identifies Latin, Kannada, and Tigalari."""
        for w in WORDS_DATASET_1000:
            self.assertEqual(detect_script(w["latin_phonetic"]), "latin")
            self.assertEqual(detect_script(w["kannada"]), "kannada")
            self.assertEqual(detect_script(w["expected_tigalari"]), "tigalari")

    def test_07_category_coverage(self):
        """Ensures all 19 categories have words tested."""
        categories = {}
        for w in WORDS_DATASET_1000:
            cat = w["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        self.assertEqual(len(categories), 19, f"Expected 19 categories, found {len(categories)}")
        total_items = sum(categories.values())
        self.assertEqual(total_items, 1000)


if __name__ == '__main__':
    unittest.main()
