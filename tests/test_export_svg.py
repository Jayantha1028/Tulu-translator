#!/usr/bin/env python3
"""
Unit tests for Tulu-Tigalari SVG Exporter.
"""

import unittest
from kannada_tigalari_converter.export_svg import TuluSvgExporter


class TestSvgExporter(unittest.TestCase):
    def test_generate_svg_kannada_input(self):
        svg = TuluSvgExporter.generate_svg("ನಮಸ್ಕಾರ")
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn("UNICODE 16.0 COMPLIANT", svg)
        self.assertIn("ಕನ್ನಡ: ನಮಸ್ಕಾರ", svg)

    def test_generate_svg_tigalari_input(self):
        # Tigalari for solmelu / namaskara
        tigalari_text = "𑎥𑎪𑎱𑏐𑎒𑎸𑎬"
        svg = TuluSvgExporter.generate_svg(tigalari_text, theme="light")
        self.assertIn("<svg", svg)
        self.assertIn(tigalari_text, svg)
        self.assertIn("MalligeUnicode", svg)

    def test_generate_svg_latin_input(self):
        svg = TuluSvgExporter.generate_svg("solmelu")
        self.assertIn("<svg", svg)
        self.assertIn("solmelu", svg)


if __name__ == "__main__":
    unittest.main()
