#!/usr/bin/env python3
"""
Unified Test Runner for Tulu-Tigalari & Kannada Transliteration Project.
Runs all 93 unit test suites across core converter, 250 words, 1,000 words,
AATA Library OCR collector, Tulu-NMT pipeline, and Tulu Morphological Analyzer.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")

for p in (BASE_DIR, os.path.join(BASE_DIR, "kannada_tigalari_converter")):
    if p not in sys.path:
        sys.path.insert(0, p)


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
