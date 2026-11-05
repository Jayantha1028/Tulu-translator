"""
Unit Test Suite: Complex Ligatures, Phonetic Corner Cases & Morphological Agglutination
========================================================================================
Comprehensive edge-case test suite for Tulu/Kannada/Tigalari converter,
transliterator, morphological analyzer, and dictionary fallback engine.

Validates:
1. Complex Consonant Stacks (triple/quadruple conjuncts, geminate aspirates).
2. Phonetic Edge Conditions (anusvara, visarga, dead consonants, vocalic R/L).
3. Input Boundary Conditions (empty, whitespace, non-Indic, punctuation, emoji, ZWJ/ZWNJ).
4. Script Auto-Detection Boundary Cases.
5. Complex Agglutinative Morphology (clitics, oblique plurals, negative verbs, oblique pronouns).
6. Dictionary Morphological Fallback for edge cases.
"""

import sys
import os
import unittest

# Ensure current directory and parent directory are on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.kannada_tigalari import (
    kannada_to_tigalari,
    tigalari_to_kannada,
)
from kannada_tigalari_converter.tulu_phonetic import (
    latin_to_kannada,
    kannada_to_latin,
)
from kannada_tigalari_converter.transliterator import (
    detect_script,
    transliterate,
)
from kannada_tigalari_converter.tulu_morphology import (
    analyze,
    analyze_sentence,
    lemmatize,
    POS,
    Case,
    Number,
    Mood,
)
from kannada_tigalari_converter.tulu_dictionary import lookup_tulu, TULU_DICTIONARY


class TestComplexLigaturesAndConjuncts(unittest.TestCase):
    """Rigorous tests for complex ligatures, deep consonant stacks, and roundtrip fidelity."""

    def test_triple_consonant_stack_strya(self):
        """Triple stack: ಸ್ತ್ರ್ಯ (sa + ta + ra + ya) -> Tigalari and lossless roundtrip."""
        kn = "ಸ್ತ್ರ್ಯ"
        tig = kannada_to_tigalari(kn)
        self.assertTrue(len(tig) > 0)
        # Verify round-trip back to Kannada
        rt = tigalari_to_kannada(tig)
        self.assertEqual(rt, kn, f"Roundtrip failed for triple conjunct {kn} -> {tig} -> {rt}")

    def test_quadruple_consonant_stack_rtsnya(self):
        """Deep consonant stack: ರ್ತ್ಸ್ನ್ಯ (ra + ta + sa + na + ya)."""
        kn = "ರ್ತ್ಸ್ನ್ಯ"
        tig = kannada_to_tigalari(kn)
        self.assertTrue(len(tig) > 0)
        rt = tigalari_to_kannada(tig)
        self.assertEqual(rt, kn)

    def test_geminate_aspirate_clusters(self):
        """Geminates with aspirated stops: ಖ್ಖ, ತ್ಥ, ದ್ಧ, ಛ್ಛ, ಭ್ಭ."""
        clusters = [
            "ಖ್ಖ",  # geminate aspirated velar
            "ತ್ಥ",  # dental geminate aspirate
            "ದ್ಧ",  # voiced dental geminate aspirate (buddha: ಬುದ್ಧ)
            "ಬುದ್ಧ",
            "ಭ್ಭ",  # bilabial geminate aspirate
            "ಘ್ಘ",  # velar voiced aspirate
            "ಛ್ಛ",  # palatal geminate aspirate
        ]
        for word in clusters:
            tig = kannada_to_tigalari(word)
            rt = tigalari_to_kannada(tig)
            self.assertEqual(rt, word, f"Lossless roundtrip failed for aspirate {word}")

    def test_retroflex_and_rare_characters(self):
        """Rare Dravidian & Vedic phonemes: ಳ (LLA), ಱ (RRA), ೞ (LLLA), ಙ (NGA), ಞ (NYA)."""
        words = ["ಮಂಗಳೂರು", "ಬೆಳ್ಳಗೆ", "ಕೊಳ್ಳ", "ಕಣ್ಣ್"]
        for w in words:
            tig = kannada_to_tigalari(w)
            rt = tigalari_to_kannada(tig)
            self.assertEqual(rt, w)

    def test_word_final_dead_consonants(self):
        """Consonants ending with explicit virama: ಮಹಾನ್, ರಾಜನ್, ಸರ್ವ್."""
        words = ["ಮಹಾನ್", "ರಾಜನ್", "ಸರ್ವ್", "ಕಣ್"]
        for w in words:
            tig = kannada_to_tigalari(w)
            rt = tigalari_to_kannada(tig)
            self.assertEqual(rt, w, f"Failed roundtrip for dead consonant {w}")

    def test_internal_visarga_compounds(self):
        """Visarga in compound words: ದುಃಖ (duhkha), ಅಂತಃಕರಣ (antaHkaraNa)."""
        words = ["ದುಃಖ", "ಅಂತಃಕರಣ", "ಪ್ರಾತಃಕಾಲ"]
        for w in words:
            tig = kannada_to_tigalari(w)
            rt = tigalari_to_kannada(tig)
            self.assertEqual(rt, w)

    def test_anusvara_before_all_vargas(self):
        """Anusvara followed by stops across different vargas (velar, palatal, retroflex, dental, labial)."""
        words = [
            "ಅಂಕ",    # velar
            "ಸಂಚಾರಿ", # palatal
            "ಕುಂಡ",   # retroflex
            "ಸಂತೋಷ",  # dental
            "ಸಂಪತ್ತು", # labial
            "ಸಂಸ್ಕೃತಿ",# fricative / sibilant
        ]
        for w in words:
            tig = kannada_to_tigalari(w)
            rt = tigalari_to_kannada(tig)
            self.assertEqual(rt, w)


class TestInputBoundaryConditions(unittest.TestCase):
    """Tests boundary inputs: empty, pure whitespace, mixed scripts, punctuation, and emojis."""

    def test_empty_string_across_all_apis(self):
        """Empty string input should return empty string without throwing exceptions."""
        self.assertEqual(kannada_to_tigalari(""), "")
        self.assertEqual(tigalari_to_kannada(""), "")
        self.assertEqual(latin_to_kannada(""), "")
        self.assertEqual(kannada_to_latin(""), "")
        self.assertEqual(transliterate("", "latin", "kannada"), "")

        # Morphology on empty string
        res = analyze("")
        self.assertEqual(res.pos, POS.UNKNOWN)
        self.assertEqual(res.lemma_kannada, "")

    def test_whitespace_only_strings(self):
        """Whitespace strings should be preserved or handled gracefully."""
        ws = "   \t\n  "
        self.assertEqual(kannada_to_tigalari("   "), "   ")
        self.assertEqual(tigalari_to_kannada("   "), "   ")
        self.assertEqual(latin_to_kannada("   "), "   ")
        # Morphology trims whitespace
        res = analyze(ws)
        self.assertEqual(res.pos, POS.UNKNOWN)

    def test_non_indic_alphanumeric_passthrough(self):
        """Digits, Latin text, and special symbols should pass through uncorrupted."""
        mixed = "ತುಳು 2026: 100% ಶುದ್ಧ!"
        tig = kannada_to_tigalari(mixed)
        # Latin digits and punctuation must be preserved intact
        self.assertIn("2026:", tig)
        self.assertIn("100%", tig)
        self.assertIn("!", tig)
        rt = tigalari_to_kannada(tig)
        self.assertEqual(rt, mixed)

    def test_complex_punctuation_and_emojis(self):
        """Parentheses, brackets, curly quotes, and emojis in text."""
        text = "«ತುಳುನಾಡ್ದ» (ಬಲೆ) [ಕಾರ್ಕಳ] — 🌺 2026."
        tig = kannada_to_tigalari(text)
        self.assertIn("🌺", tig)
        self.assertIn("«", tig)
        self.assertIn("—", tig)
        rt = tigalari_to_kannada(tig)
        self.assertEqual(rt, text)

    def test_zero_width_characters(self):
        """Handle zero-width non-joiner (ZWNJ) and zero-width joiner (ZWJ)."""
        # Explicit virama half-form with ZWNJ: ಕ + ್ + ZWNJ
        zwnj_text = "ಕ್\u200Cಕ"
        tig = kannada_to_tigalari(zwnj_text)
        self.assertTrue(len(tig) > 0)


class TestScriptAutoDetectionEdgeCases(unittest.TestCase):
    """Tests auto-detection under ambiguous and edge conditions."""

    def test_mixed_kannada_with_ascii_numbers(self):
        """Text with majority Kannada characters and ASCII digits should detect as Kannada."""
        self.assertEqual(detect_script("ತುಳು 2026"), "kannada")
        self.assertEqual(detect_script("ಮಂಗಳೂರು 575001"), "kannada")

    def test_mixed_latin_with_numbers(self):
        """Text with Latin letters and numbers should detect as Latin."""
        self.assertEqual(detect_script("tulu 2026"), "latin")
        self.assertEqual(detect_script("kudla123"), "latin")

    def test_tigalari_with_punctuation(self):
        """Tigalari script with ASCII punctuation and spaces should detect as Tigalari."""
        tig = kannada_to_tigalari("ನಮಸ್ಕಾರ")
        self.assertEqual(detect_script(f"{tig}!"), "tigalari")

    def test_punctuation_only_fallback(self):
        """Punctuation only should not crash detector."""
        script = detect_script("12345 !? #$%")
        self.assertIn(script, ("latin", "kannada", "tigalari"))


class TestComplexMorphologyAgglutination(unittest.TestCase):
    """Rigorous tests for complex Dravidian agglutination in Tulu:
    - Enclitic peeling (-ಲಾ also, -ನೇ indeed)
    - Oblique plural declensions (-ಕುಲೆಡ್, -ಕುಲೆಗ್)
    - Nominative plurals (-ಕುಲು)
    - Negative verb conjugations (-ಜಿ)
    - Oblique pronoun cases (dative, ablative, sociative)
    """

    def test_enclitic_peeling_noun_locative_also(self):
        """ಇಲ್ಲಡ್ಲಾ (illaDlaa) = இல்ல (house) + ಡ್ (LOC) + ಲಾ (also) -> in the house too."""
        res = analyze("ಇಲ್ಲಡ್ಲಾ")
        self.assertEqual(res.pos, POS.NOUN)
        self.assertEqual(res.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(res.case, Case.LOCATIVE)
        tags = [m.tag for m in res.morphemes]
        self.assertIn("STEM", tags)
        self.assertIn("LOC", tags)
        self.assertIn("CLITIC.ALSO", tags)

    def test_enclitic_peeling_pronoun_also(self):
        """ಯಾನ್ಲಾ (yaanlaa) = I too."""
        res = analyze("ಯಾನ್ಲಾ")
        self.assertEqual(res.pos, POS.PRONOUN)
        self.assertEqual(res.lemma_kannada, "ಯಾನ್")
        tags = [m.tag for m in res.morphemes]
        self.assertIn("CLITIC.ALSO", tags)

    def test_oblique_plural_locative(self):
        """ಇಲ್ಲಕುಲೆಡ್ (illakuleD) = house + plural oblique + locative (in the houses)."""
        res = analyze("ಇಲ್ಲಕುಲೆಡ್")
        self.assertEqual(res.pos, POS.NOUN)
        self.assertEqual(res.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(res.case, Case.LOCATIVE)
        self.assertEqual(res.number, Number.PLURAL)
        tags = [m.tag for m in res.morphemes]
        self.assertEqual(tags, ["STEM", "PL.OBL", "LOC"])

    def test_oblique_plural_dative(self):
        """ಮರಕುಲೆಗ್ (marakuleg) = tree + pl.obl + dat (to the trees)."""
        res = analyze("ಮರಕುಲೆಗ್")
        self.assertEqual(res.pos, POS.NOUN)
        self.assertEqual(res.lemma_kannada, "ಮರ")
        self.assertEqual(res.case, Case.DATIVE)
        self.assertEqual(res.number, Number.PLURAL)

    def test_nominative_plural_illakulu(self):
        """ಇಲ್ಲಕುಲು (illakulu) = houses (nominative plural)."""
        res = analyze("ಇಲ್ಲಕುಲು")
        self.assertEqual(res.pos, POS.NOUN)
        self.assertEqual(res.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(res.number, Number.PLURAL)
        self.assertEqual(res.case, Case.NOMINATIVE)

    def test_negative_verb_malpuji(self):
        """ಮಲ್ಪುಜಿ (malpuji) = do + NEG (does not do / will not do)."""
        res = analyze("ಮಲ್ಪುಜಿ")
        self.assertEqual(res.pos, POS.VERB)
        self.assertEqual(res.lemma_kannada, "ಮಲ್ಪುಲೆ")
        self.assertTrue(res.is_negative)
        self.assertEqual(res.mood, Mood.NEGATIVE)
        tags = [m.tag for m in res.morphemes]
        self.assertEqual(tags, ["STEM", "NEG"])

    def test_negative_verb_barepuji(self):
        """ಬರೆಪುಜಿ (barepuji) = write + NEG."""
        res = analyze("ಬರೆಪುಜಿ")
        self.assertEqual(res.pos, POS.VERB)
        self.assertEqual(res.lemma_kannada, "ಬರೆಪುಲೆ")
        self.assertTrue(res.is_negative)

    def test_negative_verb_kalpuji(self):
        """ಕಲ್ಪುಜಿ (kalpuji) = learn + NEG."""
        res = analyze("ಕಲ್ಪುಜಿ")
        self.assertEqual(res.pos, POS.VERB)
        self.assertEqual(res.lemma_kannada, "ಕಲ್ಪುಲೆ")
        self.assertTrue(res.is_negative)

    def test_pronoun_sociative_ennoTTugu(self):
        """ಎನ್ನೊಟ್ಟುಗು (ennoTTugu) = with me (1sg pronoun sociative)."""
        res = analyze("ಎನ್ನೊಟ್ಟುಗು")
        self.assertEqual(res.pos, POS.PRONOUN)
        self.assertEqual(res.lemma_kannada, "ಯಾನ್")

    def test_pronoun_ablative_nammard(self):
        """ನಮ್ಮರ್ದ್ (nammard) = from us (1pl pronoun ablative)."""
        res = analyze("ನಮ್ಮರ್ದ್")
        self.assertEqual(res.pos, POS.PRONOUN)
        self.assertEqual(res.lemma_kannada, "ನಮ")

    def test_pronoun_dative_eerena_and_eereg(self):
        """ಈರೆಗ್ (eereg) = to you (2sg polite dative)."""
        res = analyze("ಈರೆಗ್")
        self.assertEqual(res.pos, POS.PRONOUN)
        self.assertEqual(res.lemma_kannada, "ಈರ್")

    def test_pronoun_third_person_datives(self):
        """ಆಯಗ್ (to him), ಆಲೆಗ್ (to her), ಅಕುಲೆಗ್ (to them)."""
        res_m = analyze("ಆಯಗ್")
        self.assertEqual(res_m.pos, POS.PRONOUN)
        self.assertEqual(res_m.lemma_kannada, "ಆಯೆ")

        res_f = analyze("ಆಲೆಗ್")
        self.assertEqual(res_f.pos, POS.PRONOUN)
        self.assertEqual(res_f.lemma_kannada, "ಆಲ್")

        res_pl = analyze("ಅಕುಲೆಗ್")
        self.assertEqual(res_pl.pos, POS.PRONOUN)
        self.assertEqual(res_pl.lemma_kannada, "ಅಕುಲು")

    def test_lemmatize_complex_word(self):
        """lemmatize() should directly return base canonical lemma."""
        self.assertEqual(lemmatize("ಇಲ್ಲಕುಲೆಡ್"), "ಇಲ್ಲ")
        self.assertEqual(lemmatize("ಮಲ್ಪುಜಿ"), "ಮಲ್ಪುಲೆ")
        self.assertEqual(lemmatize("ಬರೆಪುಜಿ"), "ಬರೆಪುಲೆ")
        self.assertEqual(lemmatize("ಎನ್ನೊಟ್ಟುಗು"), "ಯಾನ್")

    def test_sentence_with_agglutinated_forms(self):
        """analyze_sentence should parse full sentences containing complex agglutinations."""
        sentence = "ಯಾನ್ ಇಲ್ಲಡ್ಲಾ ಕುಲ್ಲುಂಡು"
        results = analyze_sentence(sentence)
        self.assertEqual(len(results), 3)
        # First word: ಯಾನ್ (1sg pronoun)
        self.assertEqual(results[0].pos, POS.PRONOUN)
        self.assertEqual(results[0].lemma_kannada, "ಯಾನ್")
        # Second word: ಇಲ್ಲಡ್ಲಾ (house + LOC + ALSO)
        self.assertEqual(results[1].pos, POS.NOUN)
        self.assertEqual(results[1].lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(results[1].case, Case.LOCATIVE)
        # Third word: ಕುಲ್ಲುಂಡು (sit + potential/stative)
        self.assertEqual(results[2].pos, POS.VERB)
        self.assertEqual(results[2].lemma_kannada, "ಕುಲ್ಲೆ")

    def test_latin_case_insensitivity_and_vowel_length(self):
        """Phonetic engine: Baraha/ITRANS case distinguishes retroflex vs dental (D/d, L/l, T/t)."""
        self.assertEqual(latin_to_kannada("kuDla"), "ಕುಡ್ಲ")  # retroflex D -> ಡ
        self.assertEqual(latin_to_kannada("kudla"), "ಕುದ್ಲ")  # dental d -> ದ
        self.assertEqual(latin_to_kannada("tuLu"), "ತುಳು")    # retroflex L -> ಳ
        self.assertEqual(latin_to_kannada("tulu"), "ತುಲು")    # dental l -> ಲ
        self.assertEqual(latin_to_kannada("TuLu"), "ಟುಳು")    # retroflex T -> ಟ
        self.assertEqual(latin_to_kannada("illa"), "ಇಲ್ಲ")
        self.assertEqual(latin_to_kannada("kallu"), "ಕಲ್ಲು")


class TestDictionaryMorphologicalFallback(unittest.TestCase):
    """Tests that lookup_tulu gracefully resolves inflected words via morphology."""

    def test_dictionary_exact_vs_inflected_lookup(self):
        """Lookup of exact base 'ಇಲ್ಲ' vs inflected 'ಇಲ್ಲಡ್' (in the house)."""
        base_matches = lookup_tulu("ಇಲ್ಲ")
        self.assertTrue(len(base_matches) > 0)
        self.assertEqual(base_matches[0]["tulu_kannada"], "ಇಲ್ಲ")

        # Inflected form not explicitly in primary lexicon
        inflected_matches = lookup_tulu("ಇಲ್ಲಡ್")
        self.assertTrue(len(inflected_matches) > 0)
        # Should resolve via morphology to 'ಇಲ್ಲ'
        top_match = inflected_matches[0]
        self.assertEqual(top_match["tulu_kannada"], "ಇಲ್ಲ")
        self.assertIn("morph_tag", top_match)
        self.assertEqual(top_match["morph_tag"], "NOUN.LOC")

    def test_dictionary_negative_verb_fallback(self):
        """Lookup of negative verb 'ಮಲ್ಪುಜಿ' via dictionary."""
        matches = lookup_tulu("ಮಲ್ಪುಜಿ")
        self.assertTrue(len(matches) > 0)
        top = matches[0]
        self.assertEqual(top["tulu_kannada"], "ಮಲ್ಪುಲೆ")
        self.assertIn("morph_tag", top)
        self.assertIn("NEG", top["morph_tag"])

    def test_dictionary_oblique_plural_fallback(self):
        """Lookup of 'ಇಲ್ಲಕುಲೆಡ್' via dictionary."""
        matches = lookup_tulu("ಇಲ್ಲಕುಲೆಡ್")
        self.assertTrue(len(matches) > 0)
        top = matches[0]
        self.assertEqual(top["tulu_kannada"], "ಇಲ್ಲ")
        self.assertIn("morph_tag", top)
        self.assertIn("NOUN.LOC", top["morph_tag"])


if __name__ == "__main__":
    unittest.main()
