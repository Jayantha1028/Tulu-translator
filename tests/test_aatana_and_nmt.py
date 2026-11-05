"""
Unit tests for AATA Book Library OCR Collector and Tulu-NMT Pipeline.
"""

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.aatana_library_collector import (
    get_catalog,
    search_books,
    clean_raw_ocr_text,
    segment_tulu_sentences,
)
from kannada_tigalari_converter.tulu_nmt_pipeline import (
    TuluNMTConfig,
    TuluMonolingualProcessor,
    ParallelCorpusBuilder,
    NMTMetrics,
    load_nmt_benchmark_corpus,
)


class TestAataAndNMT(unittest.TestCase):

    def test_catalog_loaded(self):
        catalog = get_catalog()
        self.assertGreaterEqual(len(catalog), 200)
        first_book = catalog[0]
        self.assertIn("title", first_book)
        self.assertIn("pdf_url", first_book)

    def test_search_books(self):
        matches = search_books("yakshgana")
        self.assertGreaterEqual(len(matches), 1)
        self.assertIn("yakshgana", matches[0]["title"].lower())

    def test_ocr_cleaner(self):
        raw = "AATA Digital Book Library\nPage 12\n\nತುಳುನಾಡಿನಲ್ಲಿ ಪರ್ಬ ಅಥವಾ ಹಬ್ಬ\n\n\n\n\nಅದು ದೀಪಾವಳಿ."
        cleaned = clean_raw_ocr_text(raw)
        self.assertNotIn("AATA Digital Book Library", cleaned)
        self.assertIn("ತುಳುನಾಡಿನಲ್ಲಿ ಪರ್ಬ", cleaned)

    def test_segment_sentences(self):
        text = "ತುಳುನಾಡಿನಲ್ಲಿ ಪರ್ಬ ಅಥವಾ ಹಬ್ಬ ಎಂದರೆ ಅದು ದೀಪಾವಳಿ. ಇದು ಜನಪ್ರಿಯ ಅರಸ ಬಲೀಂದ್ರನನ್ನು ಬರಮಾಡಿಕೊಳ್ಳುವ ಹಬ್ಬ!"
        sentences = segment_tulu_sentences(text)
        self.assertGreaterEqual(len(sentences), 2)
        self.assertTrue(any("ದೀಪಾವಳಿ" in s for s in sentences))

    def test_tulu_monolingual_filter(self):
        # Valid Tulu/Kannada sentence
        valid = "ತುಳು ಕರ್ನಾಟಕ ಬುಕ್ಕ ಕೇರಳೊಡು ಪಾತೆರುನ ಒಂಜಿ ದ್ರಾವಿಡ ಬಾಸೆ."
        self.assertIsNotNone(TuluMonolingualProcessor.clean_sentence(valid))

        # Mostly English noise (should be rejected)
        invalid = "This is a random English sentence with no Kannada 12345."
        self.assertIsNone(TuluMonolingualProcessor.clean_sentence(invalid))

    def test_nmt_metrics(self):
        hyp = "ಈರೆನ ಪುದರ್ ದಾದ?"
        ref = "ಈರೆನ ಪುದರ್ ದಾದ?"
        bleu = NMTMetrics.sentence_bleu(hyp, ref)
        chrf = NMTMetrics.sentence_chrf(hyp, ref)
        self.assertGreater(bleu, 0)
        self.assertEqual(chrf, 100.0)

    def test_parallel_corpus_builder(self):
        builder = ParallelCorpusBuilder()
        builder.add_pair(
            english="What is your name?",
            tulu_kannada="ಈರೆನ ಪುದರ್ ದಾದ?",
            kannada="ನಿಮ್ಮ ಹೆಸರೇನು?"
        )
        self.assertEqual(len(builder.data), 1)
        entry = builder.data[0]
        self.assertEqual(entry["eng_Latn"], "What is your name?")
        self.assertEqual(entry["tcy_Knda"], "ಈರೆನ ಪುದರ್ ದಾದ?")
        # Ensure Tigalari was generated
        self.assertTrue(len(entry["tcy_Tglr"]) > 0)
        self.assertIn("\U00011383", entry["tcy_Tglr"])  # Long II for 'ಈ'

    def test_flores_benchmark_corpus(self):
        corpus = load_nmt_benchmark_corpus()
        self.assertEqual(len(corpus.data), 10)
        # Check that all pairs have Tigalari and phonetic transcriptions
        for pair in corpus.data:
            self.assertTrue(pair["tcy_Tglr"])
            self.assertTrue(pair["tcy_Phonetic"])

    def test_csv_export_integrity(self):
        import csv
        datasets_dir = os.path.join(PARENT_DIR, "datasets")
        csv_1000 = os.path.join(datasets_dir, "tulu_lexicon_1000.csv")
        self.assertTrue(os.path.isfile(csv_1000))
        with open(csv_1000, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header[0], "id")
            rows = list(reader)
            self.assertEqual(len(rows), 1000)

        csv_hist = os.path.join(datasets_dir, "tulu_historical_dictionary_1886.csv")
        self.assertTrue(os.path.isfile(csv_hist))
        with open(csv_hist, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            self.assertEqual(len(rows), 204)

    def test_tulu_wiki_cleaner(self):
        from kannada_tigalari_converter.tulu_web_scraper import TuluWikiHarvester
        sample_wiki = "'''ಅಂಗಡಿ ಗೊಬ್ಬು''':ಈ ಗೊಬ್ಬುಡು ಜೋಕುಲು ಅಂಗಡಿಡ್ ಮಲ್ಪುನ ಬ್ಯಾರೊದ ಅನುಕರಣೆನ್ ಮಲ್ಪುನಯರ್ದಾವರ ಈ ಗೊಬ್ಬುಗ್ ಅಂಗಡಿ ಗೊಬ್ಬುಂದು ಪುದರ್ ಬತ್ತ್ಂಡ್. == ಗೊಬ್ಬರೆ ಬೋಡಾಯಿನ ವಸ್ತುಲು =="
        sentences = TuluWikiHarvester.clean_wiki_text(sample_wiki)
        self.assertGreaterEqual(len(sentences), 1)
        self.assertIn("ಅಂಗಡಿ ಗೊಬ್ಬು", sentences[0])
        self.assertNotIn("==", sentences[0])
        self.assertNotIn("'''", sentences[0])


if __name__ == "__main__":
    unittest.main()
