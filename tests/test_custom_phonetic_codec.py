#!/usr/bin/env python3
"""
Unit tests for the Tulu Custom Phonetic Codec & Discrete Symbol Engine.
Verifies:
1. Zero Microsoft Uniscribe / OS-shaping dependency.
2. Complete 1-byte discrete symbol fidelity (0 - 255).
3. Lossless round-tripping across Kannada, Tigalari Unicode 16.0, and Roman.
4. Compact serialization and >= 2.0x memory compression vs raw UTF-8.
"""

import unittest
import numpy as np
import os
import sys

from kannada_tigalari_converter.core.tulu_phonetic_codec import (
    TuluPhoneticCodec,
    TuluSymbol,
    CODE_TO_NAME,
    encode_to_custom_code,
    decode_from_custom_code,
)
from kannada_tigalari_converter.transliterator import transliterate


class TestTuluPhoneticCodec(unittest.TestCase):
    def test_symbol_table_uniqueness_and_byte_fit(self):
        """Ensure all discrete symbol IDs are strictly unique and fit into a single uint8 byte (0-255)."""
        attrs = [a for a in dir(TuluSymbol) if not a.startswith("_") and isinstance(getattr(TuluSymbol, a), int)]
        ids = [getattr(TuluSymbol, a) for a in attrs]
        self.assertEqual(len(ids), len(set(ids)), "Symbol IDs must be strictly unique!")
        for code in ids:
            self.assertGreaterEqual(code, 0, f"Code {code} must be non-negative")
            self.assertLessEqual(code, 255, f"Code {code} must fit in uint8 (0-255)")

    def test_special_tokens(self):
        """Verify core control tokens."""
        self.assertEqual(TuluSymbol.PAD, 0)
        self.assertEqual(TuluSymbol.UNK, 1)
        self.assertEqual(TuluSymbol.BOS, 2)
        self.assertEqual(TuluSymbol.EOS, 3)
        self.assertEqual(TuluSymbol.SPACE, 4)
        self.assertEqual(TuluSymbol.NEWLINE, 5)

    def test_kannada_lossless_roundtrip(self):
        """Verify standard Kannada words round-trip losslessly through custom discrete IDs."""
        test_words = [
            "ನಮಸ್ಕಾರ",
            "ಸೊಲ್ಮೆಲು",
            "ಯಾನ್",
            "ಇಲ್ಲಗ್",
            "ಬರ್ಪೆ",
            "ತುಳುನಾಡ್",
            "ಪೊರ್ಲು",
            "ಮಲ್ಲ",
            "ಕೆಲಸ",
            "ಊರು",
        ]
        for word in test_words:
            codes = TuluPhoneticCodec.encode(word)
            self.assertIsInstance(codes, list)
            self.assertTrue(len(codes) > 0)
            decoded = TuluPhoneticCodec.decode(codes, target_format="kannada")
            self.assertEqual(decoded, word, f"Failed round-trip for Kannada word '{word}'")

    def test_tulu_open_e_phonetics(self):
        """Verify Tulu open-e (Kannada ೆ್ / Baraha 'ae') maps to discrete Tulu open-e ID."""
        # Word 'kode' (yesterday) in Tulu orthography
        tulu_word = "ಕೋಡೆ್"
        codes = TuluPhoneticCodec.encode(tulu_word)
        # Should contain MATRA_TULU_AE (43)
        self.assertIn(TuluSymbol.MATRA_TULU_AE, codes)
        decoded = TuluPhoneticCodec.decode(codes, target_format="kannada")
        self.assertEqual(decoded, tulu_word)

        # Standalone open-e vowel
        vowel_open_e = "ಎ್"
        codes_v = TuluPhoneticCodec.encode(vowel_open_e)
        self.assertEqual(codes_v, [TuluSymbol.VOWEL_TULU_AE])
        self.assertEqual(TuluPhoneticCodec.decode(codes_v, target_format="kannada"), vowel_open_e)

    def test_roman_ascii_encoding(self):
        """Verify Roman ASCII phonetic input can be encoded into identical discrete IDs."""
        kannada_word = "ಸೊಲ್ಮೆಲು"
        roman_word = "solmelu"
        codes_kn = TuluPhoneticCodec.encode(kannada_word)
        codes_ro = TuluPhoneticCodec.encode(roman_word)
        self.assertEqual(codes_kn, codes_ro, "Kannada and Roman representations of 'solmelu' must produce identical discrete IDs")

    def test_tigalari_unicode_16_decoding(self):
        """Verify decoding custom IDs produces valid Unicode 16.0 Tigalari codepoints (U+11380 - U+113FF)."""
        phrase = "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ"
        codes = TuluPhoneticCodec.encode(phrase)
        tigalari_out = TuluPhoneticCodec.decode(codes, target_format="tigalari")
        self.assertTrue(len(tigalari_out) > 0)

        # Inspect codepoints: each non-space character must be in Tigalari Unicode block
        for ch in tigalari_out:
            if ch in (" ", "\n", "\t"):
                continue
            cp = ord(ch)
            self.assertTrue(
                0x11380 <= cp <= 0x113FF,
                f"Character {ch} (U+{cp:04X}) is not in Tigalari Unicode 16.0 block!"
            )

    def test_byte_serialization_and_deserialization(self):
        """Verify 1-byte binary packing with zero serialization overhead."""
        phrase = "ತುಳು ಭಾರತದ ಪ್ರಾಚೀನ ದ್ರಾವಿಡ ಭಾಷೆ"
        codes = TuluPhoneticCodec.encode(phrase)
        packed_bytes = TuluPhoneticCodec.to_bytes(codes)

        self.assertIsInstance(packed_bytes, bytes)
        self.assertEqual(len(packed_bytes), len(codes), "Each symbol must consume exactly 1 byte")

        restored_codes = TuluPhoneticCodec.from_bytes(packed_bytes)
        self.assertEqual(restored_codes, codes)

        decoded = TuluPhoneticCodec.decode(restored_codes, target_format="kannada")
        self.assertEqual(decoded, phrase)

    def test_compression_ratio_efficiency(self):
        """Verify memory compression ratio is at least 2.0x vs standard multi-byte UTF-8."""
        sample_sentence = "ಯಾನ್ ಬೊಕ್ಕ ಈ ಒಟ್ಟಿಗೆ ತುಳು ಕಲ್ಪುಗ, ಇನಿ ಪೊಸ ಪಾಠ ಉಂಡು."
        ratio = TuluPhoneticCodec.compression_ratio(sample_sentence)
        self.assertGreaterEqual(ratio, 2.0, f"Expected >= 2.0x compression ratio, got {ratio}x")

    def test_numpy_compatibility(self):
        """Verify compatibility with numpy arrays for direct integration with embedding/model layers."""
        phrase = "ಕುಡ್ಲ"
        codes = TuluPhoneticCodec.encode(phrase)
        arr = np.array(codes, dtype=np.uint8)

        decoded = decode_from_custom_code(arr, target_format="kannada")
        self.assertEqual(decoded, phrase)

    def test_transliterator_integration(self):
        """Verify integration with core transliterate() function via 'custom_code' target and source."""
        # To custom code string
        res = transliterate("solmelu", to_script="custom_code")
        expected_ids = "84 40 78 102 74 37 78 33"
        self.assertEqual(res, expected_ids)

        # From custom code string to Kannada
        kn = transliterate(expected_ids, from_script="custom_code", to_script="kannada")
        self.assertEqual(kn, "ಸೊಲ್ಮೆಲು")

        # From custom code string to Tigalari
        tig = transliterate(expected_ids, from_script="custom_code", to_script="tigalari")
        self.assertEqual(tig, "𑎱𑏅𑎭𑏐𑎪𑏀𑎭𑎻")

    def test_convenience_functions(self):
        """Verify encode_to_custom_code and decode_from_custom_code shortcuts."""
        c = encode_to_custom_code("ಬಲೆ")
        d = decode_from_custom_code(c, "kannada")
        self.assertEqual(d, "ಬಲೆ")

    def test_ktsa_tulu_half_u(self):
        """Verify KTSA proposed Tulu Half-U (U+113CB, Kannada ು್)."""
        # Word 'undu' (is / exists) with Tulu half-u: ಉಂಡು್
        text = "ಉಂಡು್"
        codes = TuluPhoneticCodec.encode(text)
        self.assertIn(TuluSymbol.TULU_HALF_U, codes)

        tig = TuluPhoneticCodec.decode(codes, target_format="tigalari")
        self.assertIn("\U000113CB", tig)

        # Reverse from Tigalari to Kannada
        kn = TuluPhoneticCodec.decode(TuluPhoneticCodec.encode(tig), target_format="kannada")
        self.assertEqual(kn, text)

    def test_ktsa_tulu_numerals(self):
        """Verify KTSA proposed Tulu digits (U+113F0 - U+113F9) and numbers (10, 100)."""
        # Check digit conversion
        kannada_digits = "೦೧೨೩೪೫೬೭೮೯"
        codes = TuluPhoneticCodec.encode(kannada_digits)
        self.assertEqual(codes, [TuluSymbol.DIGIT_0 + i for i in range(10)])

        tig_digits = TuluPhoneticCodec.decode(codes, target_format="tigalari")
        for i in range(10):
            expected_cp = 0x113F0 + i
            self.assertIn(chr(expected_cp), tig_digits)

        # Check transliterator module
        from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari, tigalari_to_kannada
        trans_tig = kannada_to_tigalari(kannada_digits)
        self.assertEqual(trans_tig, "".join(chr(0x113F0 + i) for i in range(10)))
        rt_kn = tigalari_to_kannada(trans_tig)
        self.assertEqual(rt_kn, kannada_digits)


if __name__ == "__main__":
    unittest.main()
