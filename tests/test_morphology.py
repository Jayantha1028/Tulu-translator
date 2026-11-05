"""
Unit Tests for Tulu Morphological Analyzer & Lemmatizer.
Tests noun declension, verb conjugation, pronoun recognition,
POS tagging, sentence analysis, and the declension/conjugation generators.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (BASE_DIR, os.path.join(BASE_DIR, "kannada_tigalari_converter")):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.tulu_morphology import (
    POS, Case, Tense, Person, Number, Mood,
    Morpheme, MorphAnalysis,
    analyze, analyze_sentence, lemmatize, pos_tag,
    decline_noun, conjugate_verb,
    lookup_lemma, analyze_batch, export_analysis_to_dicts,
    TULU_PRONOUNS, IRREGULAR_VERB_MAP,
)


class TestNounCaseAnalysis(unittest.TestCase):
    """Tests for noun case suffix stripping and lemmatization."""

    def test_nominative_base_form(self):
        """Base noun should be recognized as-is from lexicon."""
        result = analyze("ಇಲ್ಲ")
        self.assertEqual(result.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(result.pos, POS.NOUN)
        self.assertIn("House", result.english_meaning)

    def test_dative_case_illag(self):
        """ಇಲ್ಲಗ್ (illag) = house + dative 'to/for'."""
        result = analyze("ಇಲ್ಲಗ್")
        self.assertEqual(result.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(result.case, Case.DATIVE)
        self.assertEqual(result.pos, POS.NOUN)

    def test_locative_case_illad(self):
        """ಇಲ್ಲಡ್ (illaD) = house + locative 'in/at'."""
        result = analyze("ಇಲ್ಲಡ್")
        self.assertEqual(result.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(result.case, Case.LOCATIVE)

    def test_genitive_case_illada(self):
        """ಇಲ್ಲದ (illada) = house + genitive 'of'."""
        result = analyze("ಇಲ್ಲದ")
        self.assertEqual(result.lemma_kannada, "ಇಲ್ಲ")
        self.assertEqual(result.case, Case.GENITIVE)

    def test_dative_kudlag(self):
        """ಕುಡ್ಲಗ್ (kuDlag) = Mangaluru + dative."""
        result = analyze("ಕುಡ್ಲಗ್")
        self.assertEqual(result.lemma_kannada, "ಕುಡ್ಲ")
        self.assertEqual(result.case, Case.DATIVE)
        self.assertIn("Mangal", result.english_meaning)

    def test_dative_angadig(self):
        """ಅಂಗಡಿಗ್ (aMgaDig) = shop + dative."""
        result = analyze("ಅಂಗಡಿಗ್")
        # Should recover stem ಅಂಗಡಿ
        self.assertEqual(result.case, Case.DATIVE)
        self.assertEqual(result.pos, POS.NOUN)

    def test_locative_sudet(self):
        """ಸುದೆಟ್ (sudeT) = river + locative (at the river)."""
        result = analyze("ಸುದೆಟ್")
        self.assertEqual(result.case, Case.LOCATIVE)
        self.assertEqual(result.pos, POS.NOUN)

    def test_genitive_kadalda(self):
        """ಕಡಲ್ದ (kaDalda) = ocean + genitive."""
        # kaDal + da -> kaDalda: the 'd' merges with virama
        result = analyze("ಕಡಲ್ದ")
        # The stem ಕಡಲ್ should be found
        self.assertEqual(result.pos, POS.NOUN)

    def test_morpheme_chain_for_dative(self):
        """Morpheme chain should have STEM + DAT for dative noun."""
        result = analyze("ಇಲ್ಲಗ್")
        self.assertEqual(len(result.morphemes), 2)
        self.assertEqual(result.morphemes[0].tag, "STEM")
        self.assertEqual(result.morphemes[1].tag, "DAT")

    def test_tag_string_noun_dative(self):
        """Tag string for dative noun should be 'NOUN.DAT'."""
        result = analyze("ಇಲ್ಲಗ್")
        self.assertEqual(result.tag_string(), "NOUN.DAT")


class TestVerbConjugationAnalysis(unittest.TestCase):
    """Tests for verb suffix stripping and tense/person/number recovery."""

    def test_present_1sg_barpe(self):
        """ಬರ್ಪೆ (barpe) = come + present 1sg."""
        result = analyze("ಬರ್ಪೆ")
        self.assertEqual(result.lemma_kannada, "ಬಲೆ")
        self.assertEqual(result.tense, Tense.PRESENT)
        self.assertEqual(result.person, Person.FIRST)
        self.assertEqual(result.number, Number.SINGULAR)
        self.assertEqual(result.pos, POS.VERB)

    def test_present_3pl_barpar(self):
        """ಬರ್ಪರ್ (barpar) = come + present 3pl."""
        result = analyze("ಬರ್ಪರ್")
        self.assertEqual(result.lemma_kannada, "ಬಲೆ")
        self.assertEqual(result.tense, Tense.PRESENT)
        self.assertEqual(result.person, Person.THIRD)
        self.assertEqual(result.number, Number.PLURAL)

    def test_past_3sg_battmd(self):
        """ಬತ್ತ್ಂಡ್ (battMD) = come + past 3sg (neuter)."""
        result = analyze("ಬತ್ತ್ಂಡ್")
        self.assertEqual(result.lemma_kannada, "ಬಲೆ")
        self.assertEqual(result.tense, Tense.PAST)
        self.assertEqual(result.person, Person.THIRD)

    def test_past_1sg_poye(self):
        """ಪೋಯೆ (pOye) = go + past 1sg."""
        result = analyze("ಪೋಯೆ")
        self.assertEqual(result.lemma_kannada, "ಪೋಲೆ")
        self.assertEqual(result.tense, Tense.PAST)
        self.assertEqual(result.person, Person.FIRST)

    def test_past_3pl_tinder(self):
        """ತಿಂದೆರ್ (tiMder) = eat + past 3pl."""
        result = analyze("ತಿಂದೆರ್")
        self.assertEqual(result.lemma_kannada, "ತಿನ್ಲೆ")
        self.assertEqual(result.tense, Tense.PAST)
        self.assertEqual(result.person, Person.THIRD)
        self.assertEqual(result.number, Number.PLURAL)

    def test_gerund_bannaga(self):
        """ಬನ್ನಗ (bannaga) = come + gerund 'while coming'."""
        result = analyze("ಬನ್ನಗ")
        self.assertEqual(result.lemma_kannada, "ಬಲೆ")
        self.assertEqual(result.mood, Mood.GERUND)
        self.assertIn("coming", result.english_meaning.lower())

    def test_infinitive_bariyere(self):
        """ಬರಿಯೆರೆ (bariyere) = come + infinitive 'to come'."""
        result = analyze("ಬರಿಯೆರೆ")
        self.assertEqual(result.lemma_kannada, "ಬಲೆ")
        self.assertEqual(result.mood, Mood.INFINITIVE)

    def test_negative_teriyiji(self):
        """ತೆರಿಯಿಜಿ (teriyiji) = know + negative."""
        result = analyze("ತೆರಿಯಿಜಿ")
        self.assertEqual(result.lemma_kannada, "ತೆರಿಯುಲೆ")
        self.assertTrue(result.is_negative)
        self.assertEqual(result.mood, Mood.NEGATIVE)

    def test_present_1sg_tinpe(self):
        """ತಿನ್ಪೆ (tinpe) = eat + present 1sg."""
        result = analyze("ತಿನ್ಪೆ")
        self.assertEqual(result.lemma_kannada, "ತಿನ್ಲೆ")
        self.assertEqual(result.tense, Tense.PRESENT)
        self.assertEqual(result.person, Person.FIRST)

    def test_past_1sg_malte(self):
        """ಮಲ್ತೆ (malte) = do + past 1sg."""
        result = analyze("ಮಲ್ತೆ")
        self.assertEqual(result.lemma_kannada, "ಮಲ್ಪುಲೆ")
        self.assertEqual(result.tense, Tense.PAST)

    def test_past_3pl_malter(self):
        """ಮಲ್ತೆರ್ (malter) = do + past 3pl."""
        result = analyze("ಮಲ್ತೆರ್")
        self.assertEqual(result.lemma_kannada, "ಮಲ್ಪುಲೆ")
        self.assertEqual(result.person, Person.THIRD)
        self.assertEqual(result.number, Number.PLURAL)


class TestPronounRecognition(unittest.TestCase):
    """Tests for pronoun identification."""

    def test_pronoun_yaan(self):
        """ಯಾನ್ (yaan) = 'I' pronoun."""
        result = analyze("ಯಾನ್")
        self.assertEqual(result.pos, POS.PRONOUN)
        self.assertEqual(result.english_meaning, "I")

    def test_pronoun_nama(self):
        """ನಮ (nama) = 'we' pronoun."""
        result = analyze("ನಮ")
        self.assertEqual(result.pos, POS.PRONOUN)
        self.assertEqual(result.english_meaning, "we")

    def test_pronoun_eer(self):
        """ಈರ್ (eer) = 'you (polite)' pronoun."""
        result = analyze("ಈರ್")
        self.assertEqual(result.pos, POS.PRONOUN)

    def test_pronoun_aaye(self):
        """ಆಯೆ (aaye) = 'he' pronoun."""
        result = analyze("ಆಯೆ")
        self.assertEqual(result.pos, POS.PRONOUN)
        self.assertEqual(result.english_meaning, "he")


class TestLemmatization(unittest.TestCase):
    """Tests for the quick lemmatize() function."""

    def test_lemmatize_noun_dative(self):
        self.assertEqual(lemmatize("ಇಲ್ಲಗ್"), "ಇಲ್ಲ")

    def test_lemmatize_noun_locative(self):
        self.assertEqual(lemmatize("ಇಲ್ಲಡ್"), "ಇಲ್ಲ")

    def test_lemmatize_verb_present(self):
        self.assertEqual(lemmatize("ಬರ್ಪೆ"), "ಬಲೆ")

    def test_lemmatize_verb_past(self):
        self.assertEqual(lemmatize("ಪೋಯೆ"), "ಪೋಲೆ")

    def test_lemmatize_base_form(self):
        self.assertEqual(lemmatize("ಮರ"), "ಮರ")

    def test_lemmatize_latin_input(self):
        result = lemmatize("barpe", script="latin")
        self.assertEqual(result, "ಬಲೆ")


class TestPOSTagging(unittest.TestCase):
    """Tests for the quick pos_tag() function."""

    def test_pos_noun(self):
        self.assertEqual(pos_tag("ಮರ"), "noun")

    def test_pos_verb_conjugated(self):
        self.assertEqual(pos_tag("ಬರ್ಪೆ"), "verb")

    def test_pos_pronoun(self):
        self.assertEqual(pos_tag("ಯಾನ್"), "pronoun")


class TestNounDeclension(unittest.TestCase):
    """Tests for the decline_noun() paradigm generator."""

    def test_decline_illa(self):
        """Decline ಇಲ್ಲ (house) through all 8 cases."""
        table = decline_noun("ಇಲ್ಲ")
        self.assertEqual(table.lemma_kannada, "ಇಲ್ಲ")

        # Nominative should be unchanged
        nom = table.forms[Case.NOMINATIVE]
        self.assertEqual(len(nom), 1)
        self.assertEqual(nom[0]["kannada"], "ಇಲ್ಲ")

        # Dative should have -ಗ್ and -ಗು forms
        dat = table.forms[Case.DATIVE]
        dat_kn = [f["kannada"] for f in dat]
        self.assertIn("ಇಲ್ಲಗ್", dat_kn)
        self.assertIn("ಇಲ್ಲಗು", dat_kn)

        # Locative
        loc = table.forms[Case.LOCATIVE]
        loc_kn = [f["kannada"] for f in loc]
        self.assertIn("ಇಲ್ಲಡ್", loc_kn)

        # Genitive
        gen = table.forms[Case.GENITIVE]
        gen_kn = [f["kannada"] for f in gen]
        self.assertIn("ಇಲ್ಲದ", gen_kn)

    def test_decline_has_all_8_cases(self):
        """All 8 cases should be present in the declension table."""
        table = decline_noun("ಮರ")
        self.assertEqual(len(table.forms), 8)
        for case in Case:
            self.assertIn(case, table.forms)

    def test_decline_tigalari_output(self):
        """Each form should include a Tigalari rendering."""
        table = decline_noun("ಇಲ್ಲ")
        for case_forms in table.forms.values():
            for form in case_forms:
                self.assertIn("tigalari", form)
                self.assertTrue(len(form["tigalari"]) > 0)

    def test_decline_from_latin(self):
        """Should accept Latin input."""
        table = decline_noun("illa", script="latin")
        self.assertEqual(table.lemma_latin, "illa")


class TestVerbConjugation(unittest.TestCase):
    """Tests for the conjugate_verb() paradigm generator."""

    def test_conjugate_tinle(self):
        """Conjugate ತಿನ್ಲೆ (eat) — check present 1sg."""
        table = conjugate_verb("ತಿನ್ಲೆ")
        self.assertEqual(table.lemma_kannada, "ತಿನ್ಲೆ")
        self.assertIn("prs.1sg", table.forms)

    def test_conjugate_has_all_slots(self):
        """All standard conjugation slots should be present."""
        table = conjugate_verb("ತಿನ್ಲೆ")
        expected_slots = [
            "prs.1sg", "prs.3pl", "prs.3sg",
            "pst.1sg", "pst.3pl", "pst.3sg",
            "imp.pol", "obl", "inf", "ger", "neg",
        ]
        for slot in expected_slots:
            self.assertIn(slot, table.forms, f"Missing slot: {slot}")

    def test_conjugate_tigalari(self):
        """Each form should include Tigalari."""
        table = conjugate_verb("ತಿನ್ಲೆ")
        for slot, form in table.forms.items():
            self.assertIn("tigalari", form, f"No tigalari in slot: {slot}")


class TestSentenceAnalysis(unittest.TestCase):
    """Tests for analyze_sentence() and batch processing."""

    def test_analyze_sentence_basic(self):
        """ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ = 'I come to the house'."""
        results = analyze_sentence("ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ")
        self.assertEqual(len(results), 3)
        # First word: pronoun
        self.assertEqual(results[0].pos, POS.PRONOUN)
        # Second word: noun + dative
        self.assertEqual(results[1].pos, POS.NOUN)
        self.assertEqual(results[1].case, Case.DATIVE)
        # Third word: verb present 1sg
        self.assertEqual(results[2].pos, POS.VERB)
        self.assertEqual(results[2].tense, Tense.PRESENT)

    def test_analyze_empty_sentence(self):
        results = analyze_sentence("")
        self.assertEqual(results, [])

    def test_analyze_batch(self):
        words = ["ಇಲ್ಲ", "ಬರ್ಪೆ", "ಯಾನ್"]
        results = analyze_batch(words)
        self.assertEqual(len(results), 3)

    def test_export_to_dicts(self):
        results = analyze_batch(["ಇಲ್ಲಗ್"])
        dicts = export_analysis_to_dicts(results)
        self.assertEqual(len(dicts), 1)
        self.assertEqual(dicts[0]["pos"], "noun")
        self.assertEqual(dicts[0]["case"], "dative")
        self.assertIsInstance(dicts[0]["morphemes"], list)


class TestMorphAnalysisDataclass(unittest.TestCase):
    """Tests for the MorphAnalysis dataclass methods."""

    def test_tag_string_verb_present(self):
        result = analyze("ಬರ್ಪೆ")
        tag = result.tag_string()
        self.assertIn("VERB", tag)
        self.assertIn("PRE", tag)

    def test_tag_string_negative(self):
        result = analyze("ತೆರಿಯಿಜಿ")
        tag = result.tag_string()
        self.assertIn("NEG", tag)

    def test_to_dict(self):
        result = analyze("ಇಲ್ಲಗ್")
        d = result.to_dict()
        self.assertEqual(d["surface_word"], "ಇಲ್ಲಗ್")
        self.assertEqual(d["lemma_kannada"], "ಇಲ್ಲ")
        self.assertEqual(d["pos"], "noun")
        self.assertEqual(d["case"], "dative")
        self.assertTrue(len(d["lemma_tigalari"]) > 0)

    def test_confidence_exact_match(self):
        """Exact lexicon match should have confidence 1.0."""
        result = analyze("ಇಲ್ಲ")
        self.assertEqual(result.confidence, 1.0)

    def test_confidence_suffix_stripped(self):
        """Suffix-stripped analysis should have high but < 1.0 confidence."""
        result = analyze("ಬರ್ಪೆ")
        self.assertGreaterEqual(result.confidence, 0.85)

    def test_unknown_word(self):
        """Unknown word should get POS.UNKNOWN with low confidence."""
        result = analyze("ಫ಼ೂಝ಼ಬ಼ಾರ಼")
        self.assertEqual(result.pos, POS.UNKNOWN)
        self.assertLess(result.confidence, 0.5)


class TestLatinAndTigalariInput(unittest.TestCase):
    """Tests for analyzing words given in Latin or Tigalari script."""

    def test_latin_verb(self):
        result = analyze("barpe", script="latin")
        self.assertEqual(result.pos, POS.VERB)
        self.assertEqual(result.lemma_latin, "bale")

    def test_latin_noun_dative(self):
        result = analyze("illag", script="latin")
        self.assertEqual(result.pos, POS.NOUN)
        self.assertEqual(result.case, Case.DATIVE)

    def test_auto_detect_latin(self):
        result = analyze("barpe")
        self.assertEqual(result.pos, POS.VERB)


class TestIrregularVerbCoverage(unittest.TestCase):
    """Tests for irregular / suppletive verb stem recognition."""

    def test_come_all_forms(self):
        """All forms of 'come' should lemmatize to ಬಲೆ."""
        forms = ["ಬರ್ಪೆ", "ಬರ್ಪರ್", "ಬತ್ತ್ಂಡ್", "ಬನ್ನಗ", "ಬರಿಯೆರೆ"]
        for form in forms:
            result = analyze(form)
            self.assertEqual(result.lemma_kannada, "ಬಲೆ",
                             f"{form} should lemmatize to ಬಲೆ")

    def test_go_all_forms(self):
        """All forms of 'go' should lemmatize to ಪೋಲೆ."""
        forms = ["ಪೋಪೆ", "ಪೋಪರ್", "ಪೋಯೆ"]
        for form in forms:
            result = analyze(form)
            self.assertEqual(result.lemma_kannada, "ಪೋಲೆ",
                             f"{form} should lemmatize to ಪೋಲೆ")

    def test_eat_present_and_past(self):
        """ತಿನ್ / ತಿಂದ stems → ತಿನ್ಲೆ."""
        self.assertEqual(analyze("ತಿನ್ಪೆ").lemma_kannada, "ತಿನ್ಲೆ")
        self.assertEqual(analyze("ತಿಂದೆರ್").lemma_kannada, "ತಿನ್ಲೆ")

    def test_see_stems(self):
        """ತೂ / ತೂಯ / ತೂಪ stems → ತೂಲೆ."""
        self.assertEqual(analyze("ತೂಪೆ").lemma_kannada, "ತೂಲೆ")
        self.assertEqual(analyze("ತೂಯೆ").lemma_kannada, "ತೂಲೆ")


if __name__ == "__main__":
    unittest.main()
