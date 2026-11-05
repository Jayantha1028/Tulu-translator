"""
Unit Tests for Data Cleansing & O(1) Deduplication Engine
=========================================================
Tests:
1. DataCleaner: NFC normalization, control characters, wiki markup, tags, citations.
2. Tulu/Kannada Script Density & Validity Filter.
3. MD5 Canonical Fingerprinting for Robust Deduplication.
4. DeduplicatedDataset: insert, deduplication on every insert, streaming append, stats.
5. ParallelCorpusBuilder: clean and deduplicated parallel pair inserts.
"""

import os
import sys
import tempfile
import unittest

# Ensure current and parent dirs on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.data_cleaner import DataCleaner, DeduplicatedDataset
from kannada_tigalari_converter.tulu_nmt_pipeline import ParallelCorpusBuilder


class TestDataCleaner(unittest.TestCase):
    """Tests for text normalization and sanitization."""

    def test_unicode_nfc_and_control_chars_removal(self):
        """Removes control chars (ZWSP, BOM, null bytes) and normalizes to NFC."""
        dirty = "ತುಳು\u200Bನಾಡ್ದ\ufeff ಕರಾವಳಿ\x00"
        cleaned = DataCleaner.normalize_unicode(dirty)
        self.assertNotIn("\u200B", cleaned)
        self.assertNotIn("\ufeff", cleaned)
        self.assertNotIn("\x00", cleaned)
        self.assertIn("ತುಳು", cleaned)

    def test_strip_wiki_templates_and_refs(self):
        """Strips {{Infobox...}}, <ref>...</ref>, HTML tags, and citations."""
        wiki_text = (
            "{{Infobox language|name=Tulu}}\n"
            "ತುಳು ಬಾಸೆ ದ್ರಾವಿಡ ಬಾಸಾ ಕುಟುಂಬೊಗು ಸೇರ್ದ್ಂಡ್.<ref>Linguistic Survey</ref> "
            "ಉಂದು ಕರಾವಳಿಡ್ ಪಾತೆರುವೆರ್.[1][citation needed]"
        )
        cleaned = DataCleaner.clean_text(wiki_text)
        self.assertNotIn("{{Infobox", cleaned)
        self.assertNotIn("<ref>", cleaned)
        self.assertNotIn("Linguistic Survey", cleaned)
        self.assertNotIn("[1]", cleaned)
        self.assertNotIn("[citation needed]", cleaned)
        self.assertIn("ತುಳು ಬಾಸೆ ದ್ರಾವಿಡ ಬಾಸಾ ಕುಟುಂಬೊಗು ಸೇರ್ದ್ಂಡ್", cleaned)

    def test_unpack_wiki_internal_links(self):
        """Unpacks [[Target|Label]] -> Label, and [[Target]] -> Target."""
        text = "ಉಂದು [[ಕುಡ್ಲ|ಮಂಗಳೂರು]] ನಗರೊಡು ಉಂಡು. [[ಉಡುಪಿ]] ಜಿಲ್ಲೆಡ್."
        cleaned = DataCleaner.clean_text(text)
        self.assertIn("ಮಂಗಳೂರು ನಗರೊಡು ಉಂಡು", cleaned)
        self.assertIn("ಉಡುಪಿ ಜಿಲ್ಲೆಡ್", cleaned)
        self.assertNotIn("[[", cleaned)

    def test_strip_urls_and_multispaces(self):
        """Removes URLs and collapses whitespace."""
        text = "ಮಾಹಿತಿ https://tcy.wikipedia.org/wiki/Tulu    ನೋಡಿ  \t\n  ಇಲ್ಲಿದೆ."
        cleaned = DataCleaner.clean_text(text)
        self.assertNotIn("http", cleaned)
        self.assertEqual(cleaned, "ಮಾಹಿತಿ ನೋಡಿ ಇಲ್ಲಿದೆ.")

    def test_is_valid_tulu_kannada(self):
        """Validates authentic Tulu/Kannada text and rejects boilerplate."""
        # Valid Tulu
        ok, reason = DataCleaner.is_valid_tulu_kannada("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ")
        self.assertTrue(ok, f"Expected valid, got: {reason}")

        # Too short (< 2 words)
        ok, reason = DataCleaner.is_valid_tulu_kannada("ಇಲ್ಲ")
        self.assertFalse(ok)
        self.assertIn("too_few_words", reason)

        # Low Kannada density (pure English)
        ok, reason = DataCleaner.is_valid_tulu_kannada("This is an English sentence without Tulu.")
        self.assertFalse(ok)
        self.assertIn("low_kannada_density", reason)

        # Wikipedia navigation boilerplate
        ok, reason = DataCleaner.is_valid_tulu_kannada("ವರ್ಗ:ತುಳುನಾಡು ಇತಿಹಾಸ thumb|right")
        self.assertFalse(ok)

    def test_canonical_fingerprinting(self):
        """Fingerprint ignores minor whitespace, case, and punctuation differences."""
        t1 = "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ."
        t2 = "ಯಾನ್    ಇಲ್ಲಗ್ ಬರ್ಪೆ!"
        t3 = "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ"
        fp1 = DataCleaner.compute_fingerprint(t1)
        fp2 = DataCleaner.compute_fingerprint(t2)
        fp3 = DataCleaner.compute_fingerprint(t3)
        self.assertEqual(fp1, fp2)
        self.assertEqual(fp1, fp3)


class TestDeduplicatedDataset(unittest.TestCase):
    """Tests deduplication and persistence for dataset inserts."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_insert_with_deduplication(self):
        """Verifies that inserting identical or canonical duplicate items is rejected."""
        dataset = DeduplicatedDataset(filepath=self.temp_path, auto_save=True)

        rec1 = {
            "source_type": "Wikipedia",
            "source_name": "Article1",
            "tulu_kannada": "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ.",
            "english_meaning": "I come home"
        }
        # First insert succeeds
        ok1, reason1 = dataset.insert(rec1)
        self.assertTrue(ok1)
        self.assertEqual(reason1, "inserted")
        self.assertEqual(len(dataset.records), 1)

        # Exact duplicate insert rejected
        ok2, reason2 = dataset.insert(rec1)
        self.assertFalse(ok2)
        self.assertEqual(reason2, "duplicate")
        self.assertEqual(len(dataset.records), 1)

        # Punctuation/whitespace variation rejected as duplicate
        rec3 = dict(rec1)
        rec3["tulu_kannada"] = "ಯಾನ್   ಇಲ್ಲಗ್   ಬರ್ಪೆ! "
        ok3, reason3 = dataset.insert(rec3)
        self.assertFalse(ok3)
        self.assertEqual(reason3, "duplicate")
        self.assertEqual(len(dataset.records), 1)

        # Different sentence succeeds
        rec4 = {
            "source_type": "Wikipedia",
            "source_name": "Article2",
            "tulu_kannada": "ಕುಡ್ಲ ಒಂಜಿ ಪೊರ್ಲುದ ಊರು.",
            "english_meaning": "Mangalore is a beautiful city"
        }
        ok4, reason4 = dataset.insert(rec4)
        self.assertTrue(ok4)
        self.assertEqual(len(dataset.records), 2)

    def test_automatic_tigalari_and_latin_generation(self):
        """Automatically fills in Tigalari and Latin phonetics if missing."""
        dataset = DeduplicatedDataset(filepath=self.temp_path, auto_save=True)
        dataset.insert({
            "source_type": "Test",
            "source_name": "Unit",
            "tulu_kannada": "ನಮಸ್ಕಾರ ತುಳುನಾಡ್",
            "english_meaning": "Greetings Tulunadu"
        })
        rec = dataset.records[0]
        self.assertTrue(len(rec["tulu_tigalari"]) > 0)
        self.assertIn("namaskaara", rec["tulu_latin"].lower())

    def test_reloading_existing_file_maintains_fingerprint_cache(self):
        """A new dataset instance loading an existing CSV will immediately reject duplicates."""
        ds1 = DeduplicatedDataset(filepath=self.temp_path, auto_save=True)
        ds1.insert({"tulu_kannada": "ತುಳು ಭಾಷೆ ಪ್ರಾಚೀನವಾಯಿನವು."})
        self.assertEqual(len(ds1.records), 1)

        # Create new dataset pointing to same file
        ds2 = DeduplicatedDataset(filepath=self.temp_path, auto_save=True)
        self.assertEqual(len(ds2.records), 1)

        # Attempt to insert same sentence into ds2
        ok, reason = ds2.insert({"tulu_kannada": "ತುಳು ಭಾಷೆ ಪ್ರಾಚೀನವಾಯಿನವು."})
        self.assertFalse(ok)
        self.assertEqual(reason, "duplicate")

    def test_batch_insertion(self):
        """Batch insert correctly tracks stats."""
        dataset = DeduplicatedDataset(filepath=self.temp_path, auto_save=False)
        batch = [
            {"tulu_kannada": "ವಾಕ್ಯ ಒಂದು ಇಲ್ಲಿದೆ."},
            {"tulu_kannada": "ವಾಕ್ಯ ಎರಡು ಇಲ್ಲಿದೆ."},
            {"tulu_kannada": "ವಾಕ್ಯ ಒಂದು ಇಲ್ಲಿದೆ."},  # duplicate of 1
            {"tulu_kannada": "X"},                   # invalid (too short)
        ]
        stats = dataset.insert_batch(batch)
        self.assertEqual(stats["inserted"], 2)
        self.assertEqual(stats["duplicate"], 1)
        self.assertEqual(stats["invalid"], 1)


class TestParallelCorpusDeduplication(unittest.TestCase):
    """Tests deduplication in ParallelCorpusBuilder."""

    def test_parallel_add_pair_dedup(self):
        builder = ParallelCorpusBuilder()
        ok1 = builder.add_pair("Hello", "ನಮಸ್ಕಾರ")
        self.assertTrue(ok1)
        self.assertEqual(len(builder.data), 1)

        # Exact duplicate
        ok2 = builder.add_pair("Hello", "ನಮಸ್ಕಾರ")
        self.assertFalse(ok2)
        self.assertEqual(len(builder.data), 1)

        # Different pair
        ok3 = builder.add_pair("Thank you", "ಸೊಲ್ಮೆಲು")
        self.assertTrue(ok3)
        self.assertEqual(len(builder.data), 2)


if __name__ == "__main__":
    unittest.main()
