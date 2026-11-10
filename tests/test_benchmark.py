#!/usr/bin/env python3
"""
Unit tests for the zero-burden benchmark suite.
"""

import unittest
from kannada_tigalari_converter.benchmark import TuluBenchmarkSuite


class TestBenchmarkSuite(unittest.TestCase):
    def test_transliteration_benchmark(self):
        res = TuluBenchmarkSuite.benchmark_transliteration()
        self.assertEqual(res["total_words"], 1000)
        self.assertEqual(res["roundtrip_accuracy"], 100.0)
        self.assertGreater(res["throughput_wps"], 1000)

    def test_sentence_translation_benchmark(self):
        res = TuluBenchmarkSuite.benchmark_sentence_translation()
        self.assertGreater(res["total_runs"], 0)
        self.assertLess(res["avg_latency_ms"], 5.0)  # Must be fast (<5ms)

    def test_morphology_benchmark(self):
        res = TuluBenchmarkSuite.benchmark_morphology()
        self.assertGreater(res["total_runs"], 0)
        self.assertLess(res["avg_latency_ms"], 10.0)

    def test_stroke_recognizer_benchmark(self):
        res = TuluBenchmarkSuite.benchmark_stroke_recognizer()
        self.assertGreater(res["iterations"], 0)
        self.assertLess(res["avg_latency_ms"], 2.0)


if __name__ == "__main__":
    unittest.main()
