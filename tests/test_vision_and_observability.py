"""
Unit Tests for Vision OCR, Handwriting Stroke Recognizer,
Telemetry Observability, and TuluMorphAnalyzer wrapper.
"""

import unittest
from PIL import Image, ImageDraw

from kannada_tigalari_converter.core.observability import (
    StructuredLogger,
    TelemetryTracker,
)
from kannada_tigalari_converter.nlp.tulu_morphology import TuluMorphAnalyzer
from kannada_tigalari_converter.vision.tulu_ocr_service import (
    preprocess_document_image,
    extract_entities_from_text,
    ocr_and_translate_document,
)
from kannada_tigalari_converter.vision.stroke_recognizer import (
    CharacterStrokeRecognizer,
)


class TestObservability(unittest.TestCase):
    def test_structured_logger(self):
        logger = StructuredLogger(max_entries=5)
        for i in range(10):
            logger.log(
                service="test-service" if i % 2 == 0 else "other-service",
                level="INFO",
                event="test_event",
                message=f"Log message {i}",
                duration_ms=float(i * 10),
            )

        entries = logger.tail(limit=10)
        self.assertLessEqual(len(entries), 5)
        self.assertEqual(entries[-1]["message"], "Log message 9")

        filtered = logger.tail(limit=10, service="other-service")
        self.assertTrue(all(e["service"] == "other-service" for e in filtered))

    def test_telemetry_tracker(self):
        tracker = TelemetryTracker(window_seconds=60)
        summary_empty = tracker.summary()
        self.assertEqual(summary_empty["request_count"], 0)
        self.assertEqual(summary_empty["p95_latency_ms"], 0.0)

        # Record latencies: 10ms, 20ms, 30ms, 40ms, 100ms (500 error)
        tracker.record(10.0, status_code=200)
        tracker.record(20.0, status_code=200)
        tracker.record(30.0, status_code=200)
        tracker.record(40.0, status_code=200)
        tracker.record(100.0, status_code=500)

        summary = tracker.summary()
        self.assertEqual(summary["request_count"], 5)
        self.assertEqual(summary["error_rate_pct"], 20.0)
        self.assertGreater(summary["p95_latency_ms"], 0.0)
        self.assertEqual(summary["min_latency_ms"], 10.0)
        self.assertEqual(summary["max_latency_ms"], 100.0)


class TestMorphologyAnalyzerWrapper(unittest.TestCase):
    def setUp(self):
        self.analyzer = TuluMorphAnalyzer()

    def test_lemmatize(self):
        lemma = self.analyzer.lemmatize("ಇಲ್ಲಗ್")
        self.assertEqual(lemma, "ಇಲ್ಲ")

    def test_predict_pos(self):
        pos = self.analyzer.predict_pos("ಇಲ್ಲ")
        self.assertEqual(pos, "noun")

    def test_parse_morphemes(self):
        parsed = self.analyzer.parse("ಇಲ್ಲಗ್")
        self.assertIsInstance(parsed, list)
        self.assertGreaterEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["surface"], "ಇಲ್ಲ")
        self.assertEqual(parsed[1]["tag"], "DAT")
        self.assertTrue("meaning" in parsed[1] or "gloss" in parsed[1])


class TestVisionOCRAndEntities(unittest.TestCase):
    def test_preprocess_document_image(self):
        img = Image.new("RGB", (100, 100), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "ತುಳು", fill=(0, 0, 0))

        processed = preprocess_document_image(img)
        self.assertIsInstance(processed, Image.Image)
        self.assertEqual(processed.size, (100, 100))

    def test_extract_entities_from_text(self):
        sample_text = (
            "In Kudla (ಕುಡ್ಲ) near ಕದ್ರಿ temple, invoice #901 was issued on 2026-11-05 "
            "for ₹1,500 by support@tulutrust.org or call +91-98765-43210. "
            "Dated in Saka 1948."
        )
        entities = extract_entities_from_text(sample_text)
        self.assertIn("support@tulutrust.org", entities["emails"])
        self.assertIn("2026-11-05", entities["dates"])
        self.assertTrue(any("1,500" in a for a in entities["monetary_amounts"]))
        self.assertIn("ಕುಡ್ಲ", entities["tulu_cultural_entities"])
        self.assertIn("ಕದ್ರಿ", entities["tulu_cultural_entities"])
        self.assertTrue(len(entities["historical_eras"]) >= 1)

    def test_ocr_and_translate_document(self):
        # Create a test synthetic image with text
        img = Image.new("RGB", (200, 60), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((10, 20), "hello world", fill=(0, 0, 0))

        res = ocr_and_translate_document(img, lang="eng")
        self.assertIn("dimensions", res)
        self.assertIn("raw_text", res)
        self.assertIn("entities", res)
        self.assertIn("translations", res)


class TestStrokeRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = CharacterStrokeRecognizer()

    def test_recognize_empty(self):
        res = self.recognizer.recognize([])
        self.assertFalse(res["matched"])

    def test_recognize_horizontal_line(self):
        # Straight horizontal stroke
        line_stroke = [[{"x": float(x), "y": 10.0} for x in range(0, 100, 5)]]
        res = self.recognizer.recognize(line_stroke)
        self.assertTrue(res["matched"])
        self.assertEqual(res["symbol"], "LINE")

    def test_recognize_vertical_stroke(self):
        # Straight vertical stroke (aspect < 0.4)
        vert_stroke = [[{"x": 10.0, "y": float(y)} for y in range(0, 100, 5)]]
        res = self.recognizer.recognize(vert_stroke)
        self.assertTrue(res["matched"])
        self.assertEqual(res["symbol"], "1")


if __name__ == "__main__":
    unittest.main()
