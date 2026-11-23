"""
Unit Tests for Custom Scripting & Private Use Area (PUA) Engine
===============================================================
Verifies:
1. Isomorphic 1-to-1 roundtrip between Unicode 16.0 and Custom PUA.
2. Default behavior preserves official Unicode 16.0 as the main standard.
3. Switchable conversion to custom script mode via API and transliterator.
4. Auto-detection and seamless reverse transliteration from custom scripting.
"""

import unittest
from kannada_tigalari_converter.core import (
    kannada_to_tigalari,
    tigalari_to_kannada,
    transliterate,
    detect_script,
    SCRIPT_MODE_UNICODE,
    SCRIPT_MODE_CUSTOM,
    unicode_to_custom,
    custom_to_unicode,
    is_unicode_tigalari,
    is_custom_tigalari,
    detect_tigalari_mode,
)


class TestCustomScriptSwitch(unittest.TestCase):
    """Verifies that Unicode 16.0 remains main/default while custom script mode is switchable."""

    def test_default_is_unicode_16(self):
        """Ensures that default transliteration always produces official Unicode 16.0 standard."""
        text = "ನಮಸ್ಕಾರ"
        out_default = kannada_to_tigalari(text)
        out_explicit_unicode = kannada_to_tigalari(text, script_mode="unicode")
        
        self.assertEqual(out_default, out_explicit_unicode)
        self.assertTrue(is_unicode_tigalari(out_default))
        self.assertFalse(is_custom_tigalari(out_default))
        self.assertEqual(detect_script(out_default), "tigalari")
        self.assertEqual(detect_tigalari_mode(out_default), "unicode")

    def test_custom_script_mode_switch(self):
        """Tests that switching script_mode to 'custom' produces valid PUA codepoints."""
        text = "ನಮಸ್ಕಾರ"
        out_custom = kannada_to_tigalari(text, script_mode="custom")

        self.assertTrue(is_custom_tigalari(out_custom))
        self.assertFalse(is_unicode_tigalari(out_custom))
        self.assertEqual(detect_script(out_custom), "tigalari_custom")
        self.assertEqual(detect_tigalari_mode(out_custom), "custom")

        # Check all PUA codepoints (U+E880 - U+E8DF)
        codepoints = [ord(c) for c in out_custom]
        for cp in codepoints:
            self.assertTrue(0xE880 <= cp <= 0xE8DF, f"Expected PUA codepoint, got U+{cp:04X}")

    def test_lossless_roundtrip_unicode_to_custom(self):
        """Tests 100% bidirectional lossless roundtrip between Unicode 16.0 and Custom PUA."""
        test_phrases = [
            "ಸೊಲ್ಮೆಲು",
            "ನಮಸ್ಕಾರ",
            "ಕೋಡೆ್ ಮಲ್ಲ ಬರ್ಸ ಬತ್ತ್ಂಡ್",
            "ಈರ್ ಎಂಚ ಉಲ್ಲರ್?",
            "ದಯಮಲ್ತ್ ಕುಲ್ಲುಲೆ",
            "ಭಾರತ",
            "ವಿಜ್ಞಾನ",
            "ರಾಷ್ಟ್ರ",
        ]
        for p in test_phrases:
            u_tig = kannada_to_tigalari(p, script_mode="unicode")
            custom_tig = unicode_to_custom(u_tig)
            u_back = custom_to_unicode(custom_tig)
            
            self.assertEqual(u_back, u_tig, f"Mismatch for phrase: {p}")
            self.assertEqual(tigalari_to_kannada(custom_tig), p)
            self.assertEqual(tigalari_to_kannada(u_tig), p)

    def test_transliterate_api_script_mode(self):
        """Verifies transliterate() dispatcher with script_mode switch."""
        text = "solmelu"
        
        # Default: Unicode 16.0
        out_u = transliterate(text, from_script="latin", to_script="tigalari")
        self.assertTrue(is_unicode_tigalari(out_u))
        
        # Explicit Custom Script
        out_c = transliterate(text, from_script="latin", to_script="tigalari", script_mode="custom")
        self.assertTrue(is_custom_tigalari(out_c))

        # Target script 'tigalari_custom' shortcut
        out_c2 = transliterate(text, from_script="latin", to_script="tigalari_custom")
        self.assertEqual(out_c, out_c2)

        # Reverse from Custom Script to Kannada and Latin
        kan_back = transliterate(out_c, from_script="tigalari_custom", to_script="kannada")
        lat_back = transliterate(out_c, from_script="tigalari_custom", to_script="latin")
        self.assertEqual(kan_back, "ಸೊಲ್ಮೆಲು")
        self.assertEqual(lat_back, "solmelu")


if __name__ == "__main__":
    unittest.main()
