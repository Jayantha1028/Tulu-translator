#!/usr/bin/env python3
"""
Unit tests for Tulu Dataset Quality Segregator.
"""

import os
import unittest
import tempfile
import csv

from kannada_tigalari_converter.nlp.dataset_quality_segregator import (
    TuluQualityScorer,
    DatasetQualitySegregator,
)


class TestDatasetQualitySegregator(unittest.TestCase):
    def test_high_quality_tulu_sentence(self):
        text = "ಆಂಡ ಮಿಥಿಲಾ ಪ್ರದೇಸೊದ ವಿದೊವಿದೊ ಜಾತಿಲೆ ಜನೊ ಅಂಗಿಕಾ ಬುಕ್ಕೊ ಬಜ್ಜಿಕನ್ ಅಕ್ಲೆನ ಅಪ್ಪೆಬಾಸೆಯಾದ್ ಪಾತೆರುವೆರ್."
        score, status, metrics = TuluQualityScorer.evaluate(text)
        self.assertGreaterEqual(score, 0.60)
        self.assertEqual(status, "high_quality_fluent")
        self.assertGreaterEqual(metrics["tulu_markers_found"], 2)

    def test_broken_fragment_rejected(self):
        text = "2011 ನೇಪಾಳ ಜನಗಣತಿದ ಸಮಯೊಡು ಮೊರಾಂಗ್‌ದ 1"
        score, status, _ = TuluQualityScorer.evaluate(text)
        self.assertLess(score, 0.60)

    def test_unbalanced_brackets_rejected(self):
        text = "೭೦ ಮೀಟರ್ (೨೨ ಅಡಿ ಉದ್ದದ ರಡ್ಡ್ ಕಂಬೊಲು"
        score, status, _ = TuluQualityScorer.evaluate(text)
        self.assertLess(score, 0.60)
        self.assertEqual(status, "unbalanced_brackets")

    def test_wiki_markup_leak_rejected(self):
        text = 'scope="col" | ವಿಭಾಗೊ 42 ಗೆಲುವುಲು ಡೌನ್‌ಹಿಲ್ ಸ್ಕೀ ಪಂಥೋ'
        score, status, _ = TuluQualityScorer.evaluate(text)
        self.assertLess(score, 0.60)
        self.assertEqual(status, "wiki_markup_leak")

    def test_empty_text_handled(self):
        score, status, _ = TuluQualityScorer.evaluate("   ")
        self.assertEqual(score, 0.0)
        self.assertEqual(status, "empty_text")

    def test_streaming_segregation(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".csv") as fin:
            writer = csv.writer(fin)
            writer.writerow(["id", "tulu_kannada"])
            writer.writerow(["1", "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ ಬುಕ್ಕೊ ಎಡ್ಡೆ ತಿನಸು ತಿನ್ಪೆ."])
            writer.writerow(["2", "== ಉಲ್ಲೇಕೊಲು =="])
            writer.writerow(["3", "alt=Photo| ಸುಂದರ ದೃಶ್ಯ"])
            fin_path = fin.name

        high_out = fin_path + ".high.csv"
        low_out = fin_path + ".low.csv"

        try:
            segregator = DatasetQualitySegregator(quality_threshold=0.60)
            stats = segregator.segregate_file(fin_path, high_out, low_out)
            self.assertEqual(stats["total_records"], 3)
            self.assertEqual(stats["high_quality_count"], 1)
            self.assertEqual(stats["low_quality_count"], 2)
            self.assertTrue(os.path.exists(high_out))
            self.assertTrue(os.path.exists(low_out))
        finally:
            for p in (fin_path, high_out, low_out):
                if os.path.exists(p):
                    os.remove(p)


if __name__ == "__main__":
    unittest.main()
