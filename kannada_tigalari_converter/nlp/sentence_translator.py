"""
Tulu Full-Sentence Bidirectional Grammar Translator (ತುಳು ವಾಕ್ಯ ಅನುವಾದಕ)
======================================================================
Comprehensive rule-based machine translation engine for Tulu <-> English.

Core Features:
1. Tulu -> English Sentence Translation:
   - SOV (Subject-Object-Verb) to SVO (Subject-Verb-Object) structural reordering
   - Noun case decoding: Accusative, Dative, Locative, Genitive, Ablative, Sociative, Instrumental
   - Verb tense & agreement: Present, Past, Future, Imperative, Obligative, Gerund, Negative
   - Pronominal & honorific agreement (1st/2nd/3rd person, singular/plural, polite)
   - Conversational idiomatic expressions and question particle handling

2. English -> Tulu Sentence Translation:
   - SVO to SOV syntax generation
   - Dative / Locative suffix inflection on destination and location nouns
   - Verb conjugation synthesis based on Subject agreement and tense
   - Multi-script rendering into official Unicode 16.0 Tigalari and Latin phonetics
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any

from kannada_tigalari_converter.core.transliterator import (
    kannada_to_tigalari,
    kannada_to_latin,
    latin_to_kannada,
    detect_script,
)
from kannada_tigalari_converter.nlp.tulu_morphology import (
    analyze,
    analyze_sentence,
    POS,
    Case,
    Tense,
    Person,
)
from kannada_tigalari_converter.lexicon.tulu_dictionary import lookup_tulu


@dataclass
class TranslationResult:
    """Detailed result of sentence translation."""
    source_text: str
    source_lang: str               # "tulu", "kannada", or "english"
    translated_text: str           # Target translation
    tulu_kannada: str              # Canonical Tulu in Kannada script (cosmetic)
    tulu_tigalari: str             # Official Unicode 16.0 Tigalari script (cosmetic)
    tulu_latin: str                # Phonetic Latin / Canonical Romanized
    tokens: List[Dict[str, Any]]   # Morphological breakdown of tokens
    confidence: float              # 0.0 to 1.0 confidence score
    grammar_notes: List[str]       # Explanatory linguistic notes
    tulu_romanized: str = ""       # Canonical ASCII Romanized Tulu
    kannada_romanized: str = ""    # Canonical ASCII Romanized Kannada

    def __post_init__(self):
        if not self.tulu_romanized:
            self.tulu_romanized = self.tulu_latin
        if not self.kannada_romanized:
            self.kannada_romanized = self.tulu_latin

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_text": self.source_text,
            "source_lang": self.source_lang,
            "translated_text": self.translated_text,
            "tulu_romanized": self.tulu_romanized,
            "kannada_romanized": self.kannada_romanized,
            "tulu_kannada": self.tulu_kannada,
            "tulu_tigalari": self.tulu_tigalari,
            "tulu_latin": self.tulu_latin,
            "tokens": self.tokens,
            "confidence": round(self.confidence, 3),
            "grammar_notes": self.grammar_notes,
        }


# High-frequency Tulu Pronouns and lexical mappings
PRONOUN_MAP_TULU = {
    "ಯಾನ್": ("I", "1sg"),
    "ಯಾನ": ("I", "1sg"),
    "ಎಂಕ್": ("to me", "1sg_dat"),
    "ಎನ್ನ": ("my", "1sg_gen"),
    "ನಮ": ("we", "1pl_incl"),
    "ಎಂಕ್ಲು": ("we", "1pl_excl"),
    "ನಂಕ್": ("to us", "1pl_dat"),
    "ನಮ್ಮ": ("our", "1pl_gen"),
    "ಈ": ("you", "2sg_inf"),
    "ನಿನ": ("your", "2sg_gen"),
    "ನಿಕ್ಕ್": ("to you", "2sg_dat"),
    "ಈರ್": ("you", "2sg_polite"),
    "ಈರೆನ": ("your", "2sg_polite_gen"),
    "ಈರೆಗ್": ("to you", "2sg_polite_dat"),
    "ನಿಕುಲು": ("you all", "2pl"),
    "ಆಯೆ": ("he", "3sg_masc"),
    "ಆಯನ": ("his", "3sg_masc_gen"),
    "ಆಯಗ್": ("to him", "3sg_masc_dat"),
    "ಆಲ್": ("she", "3sg_fem"),
    "ಆಲೆನ": ("her", "3sg_fem_gen"),
    "ಆಲೆಗ್": ("to her", "3sg_fem_dat"),
    "ಆಕುಲು": ("they", "3pl"),
    "ಮೋಕುಲು": ("they (proximal)", "3pl"),
    "ಉಂದು": ("this", "dem_prox"),
    "ಆವು": ("that / it", "dem_dist"),
    "ಅಂದು": ("yes / it is so", "affirmative"),
}

# Tulu Adverbs, Particles, Questions
ADVERB_QUESTION_MAP = {
    "ಒಲ್ಪ": ("where", "interr_loc"),
    "ಓಡೆಗ್": ("where to", "interr_dir"),
    "ದಾನೆ": ("what", "interr_obj"),
    "ದಾದ": ("what", "interr_obj"),
    "ದಾಯೆ": ("why", "interr_reason"),
    "ಏಪ": ("when", "interr_time"),
    "ಎಂಚ": ("how", "interr_manner"),
    "ಏರ್": ("who", "interr_person"),
    "ಇನಿ": ("today", "temp_adv"),
    "ಕೋಡೆ್": ("yesterday", "temp_adv"),
    "ಎಲ್ಲೆ": ("tomorrow", "temp_adv"),
    "ಮುಲ್ಪ": ("here", "loc_adv"),
    "ಅಲ್ಪ": ("there", "loc_adv"),
    "ಬೋಡು": ("want / need / must have", "modal"),
    "ಬೋಡ್ಚಿ": ("do not want / not needed", "modal_neg"),
    "ಅಂಡು": ("is / became / concluded", "copula_past"),
    "ಇಜ್ಜಿ": ("no / is not / there is no", "neg_copula"),
    "ತೆರಿಯಿಜಿ": ("do not know / not understood", "verb_neg"),
    "ಗೊತ್ತಿಜ್ಜಿ": ("do not know", "verb_neg"),
    "ಮಸ್ತ್": ("very / very much / plenty", "quantifier"),
    "ಭಾರಿ": ("immensely / heavily", "intensifier"),
    "ಎಡ್ಡೆ": ("good / well", "adjective"),
    "ಮಲ್ಲ": ("big / heavy / grand", "adjective"),
    "ಎಲ್ಯ": ("small / little", "adjective"),
    "ಚಂದ": ("beautiful / lovely", "adjective"),
}

# Full Conversational Idioms & Greetings
TULU_ENGLISH_PHRASE_CORPUS = {
    "ಮಾತೆರೆಗ್ಲಾ ಸೊಲ್ಮೆಲು": "Warm heart greetings unto all!",
    "ಸೊಲ್ಮೆಲು ಮಾತೆರ್ಗ್ಲಾ": "Warm heart greetings unto all!",
    "ನಮಸ್ಕಾರ": "Hello / Respectful greetings",
    "ಸೊಲ್ಮೆಲು": "Thank you / Greetings",
    "ಎಂಚ ಉಲ್ಲರ್": "How are you? (Polite)",
    "ಎಂಚ ಉಲ್ಲ": "How are you? (Informal)",
    "ಈರ್ ಎಂಚ ಉಲ್ಲರ್": "How are you? (Polite)",
    "ಈ ಎಂಚ ಉಲ್ಲ": "How are you? (Informal)",
    "ಈರೆನ ಪುದರ್ ದಾನೆ": "What is your name?",
    "ಈರೆನ ಪುದರ್ ದಾದ": "What is your name?",
    "ನಿನ ಪುದರ್ ದಾನೆ": "What is your name?",
    "ಎನ್ನ ಪುದರ್": "My name is",
    "ಈರ್ ಒಲ್ಪ ಉಲ್ಲರ್": "Where are you?",
    "ಈರ್ ಓಡೆಗ್ ಪೋಪರ್": "Where are you going?",
    "ಈ ಓಡೆಗ್ ಪೋಪ": "Where are you going?",
    "ಯಾನ್ ಇಲ್ಲಡ್ ಉಲ್ಲೆ": "I am at home",
    "ಯಾನ್ ಇಲ್ಲಗ್ ಬರ್ಪೆ": "I am coming to the house",
    "ಯಾನ್ ಇಲ್ಲಗ್ ಪೋಪೆ": "I am going home",
    "ನಮ ಕುಡ್ಲಗ್ ಪೋಯಿ": "We went to Mangalore",
    "ಚಾ ಪರಿಂಡಾ": "Did you have tea?",
    "ವಣಸ್ ಆಂಡಾ": "Did you have your meal?",
    "ವಣಸ್ ಆಂಡ್": "Meal is finished",
    "ನಂಕ್ ವಣಸ್ ಆಂಡ್": "Our meal has concluded",
    "ಇನಿ ಬರ್ಸ ಬರ್ಪುಂಡು": "It will rain today",
    "ಕೋಡೆ್ ಮಲ್ಲ ಬರ್ಸ ಬತ್ತ್ಂಡ್": "Yesterday heavy rain arrived",
    "ಎಲ್ಲೆ ಬೇಲೆ ಇಜ್ಜಿ": "Tomorrow there is no work",
    "ಮುಲ್ಪ ಕುಲ್ಲುಲೆ": "Please sit down here",
    "ದಯಮಲ್ತ್ ಕುಲ್ಲುಲೆ": "Please sit down",
    "ಉಂತುಲೆ": "Please wait / Stand up",
    "ತುಳು ಪಾತೆರ್ಲೆ": "Please speak in Tulu",
    "ಎಡ್ಡೆ ದಿನ": "Have a good day",
    "ಎಡ್ಡೆ ಆವಡ್": "May good happen / Best wishes",
}


class FullSentenceTranslator:
    """
    Translates complete multi-word sentences between Tulu and English,
    preserving case markers, grammatical tense, and word order.
    """

    @classmethod
    def translate(cls, text: str, source_lang: Optional[str] = None) -> TranslationResult:
        """
        Translates a full sentence. Automatically detects source language (Tulu or English).
        """
        raw = (text or "").strip()
        if not raw:
            return TranslationResult(
                source_text="",
                source_lang="unknown",
                translated_text="",
                tulu_kannada="",
                tulu_tigalari="",
                tulu_latin="",
                tokens=[],
                confidence=0.0,
                grammar_notes=["Empty text provided."],
            )

        # Detect source script/language
        detected_script = detect_script(raw)
        if not source_lang:
            if detected_script in ("kannada", "tigalari"):
                source_lang = "tulu"
            else:
                # Could be Latin phonetic Tulu or English text
                # Check for English function words
                eng_words = {"what", "where", "why", "who", "when", "how", "i", "you", "he", "she",
                             "we", "they", "is", "am", "are", "went", "come", "coming", "going",
                             "to", "the", "in", "at", "from", "with", "have", "had", "my", "your",
                             "our", "rain", "house", "home", "water", "milk", "tea", "food"}
                tokens_lower = set(re.findall(r"\b[a-zA-Z]+\b", raw.lower()))
                overlap = tokens_lower.intersection(eng_words)
                if len(overlap) >= 1 and any(w in ("what", "where", "i", "you", "is", "the", "to", "in") for w in tokens_lower):
                    source_lang = "english"
                else:
                    # Treat as phonetic Tulu if no clear English markers
                    source_lang = "tulu"

        if source_lang == "english":
            return cls.translate_english_to_tulu(raw)
        else:
            return cls.translate_tulu_to_english(raw, detected_script)

    @classmethod
    def translate_tulu_to_english(cls, text: str, script: str = "auto") -> TranslationResult:
        """Translates a Tulu sentence (Kannada, Tigalari, or Latin script) into English."""
        # Convert to canonical Kannada script if needed
        clean_text = text.strip()
        if script == "auto":
            script = detect_script(clean_text)

        if script == "tigalari":
            from kannada_tigalari_converter.core.transliterator import tigalari_to_kannada
            kn_text = tigalari_to_kannada(clean_text)
        elif script == "latin":
            kn_text = latin_to_kannada(clean_text)
        else:
            kn_text = clean_text

        # 1. Check exact conversational idiom match
        norm_kn = " ".join(kn_text.split()).rstrip("?.!,; ")
        for phrase_kn, eng_trans in TULU_ENGLISH_PHRASE_CORPUS.items():
            if norm_kn == phrase_kn:
                tg = kannada_to_tigalari(norm_kn)
                lat = kannada_to_latin(norm_kn)
                return TranslationResult(
                    source_text=text,
                    source_lang="tulu",
                    translated_text=eng_trans,
                    tulu_kannada=norm_kn,
                    tulu_tigalari=tg,
                    tulu_latin=lat,
                    tokens=[{"word": norm_kn, "meaning": eng_trans}],
                    confidence=0.98,
                    grammar_notes=["Exact conversational idiom match."],
                )

        # 2. Tokenize and analyze grammatically
        words = norm_kn.split()
        analyses = analyze_sentence(norm_kn)
        token_infos = []
        grammar_notes = []

        subject_part = ""
        object_parts = []
        verb_part = ""
        adverb_parts = []
        is_question = "?" in text or any(w in ADVERB_QUESTION_MAP for w in words)

        for w, morph in zip(words, analyses):
            token_entry = {
                "surface": w,
                "lemma": morph.lemma_kannada,
                "pos": morph.pos.value,
                "tag": morph.tag_string(),
                "english": morph.english_meaning or "",
            }

            # Check pronouns
            if w in PRONOUN_MAP_TULU:
                eng_p, tag = PRONOUN_MAP_TULU[w]
                token_entry["english"] = eng_p
                if "dat" in tag or "gen" in tag:
                    object_parts.append(eng_p)
                else:
                    subject_part = eng_p
                token_infos.append(token_entry)
                continue

            # Check adverbs / question particles
            if w in ADVERB_QUESTION_MAP:
                eng_adv, tag = ADVERB_QUESTION_MAP[w]
                token_entry["english"] = eng_adv
                if "interr" in tag:
                    adverb_parts.insert(0, eng_adv.capitalize())
                else:
                    adverb_parts.append(eng_adv)
                token_infos.append(token_entry)
                continue

            # Check noun cases
            if morph.pos == POS.NOUN:
                noun_meaning = cls._lookup_noun_base(morph.lemma_kannada)
                case_meaning = noun_meaning
                if morph.case:
                    grammar_notes.append(f"{w} ({morph.lemma_kannada}) has {morph.case.value} case.")
                    if morph.case == Case.DATIVE:
                        case_meaning = f"to the {noun_meaning}"
                    elif morph.case == Case.LOCATIVE:
                        case_meaning = f"in/at the {noun_meaning}"
                    elif morph.case == Case.GENITIVE:
                        case_meaning = f"of the {noun_meaning}"
                    elif morph.case == Case.ABLATIVE:
                        case_meaning = f"from the {noun_meaning}"
                    elif morph.case == Case.SOCIATIVE:
                        case_meaning = f"with {noun_meaning}"
                    elif morph.case == Case.INSTRUMENTAL:
                        case_meaning = f"by {noun_meaning}"
                    elif morph.case == Case.ACCUSATIVE:
                        case_meaning = noun_meaning
                token_entry["english"] = case_meaning
                object_parts.append(case_meaning)
                token_infos.append(token_entry)
                continue

            # Check verbs
            if morph.pos == POS.VERB or morph.tense or morph.person:
                v_trans = cls._format_verb_phrase(morph, subject_part)
                token_entry["english"] = v_trans
                verb_part = v_trans
                if morph.tense:
                    grammar_notes.append(f"Verb '{w}': Tense={morph.tense.value}, Person={morph.person.value if morph.person else 'any'}.")
                token_infos.append(token_entry)
                continue

            # General dictionary lookup fallback
            d_lookup = lookup_tulu(w)
            if d_lookup:
                d_eng = d_lookup[0]["english"]
                token_entry["english"] = d_eng
                object_parts.append(d_eng)
            else:
                token_entry["english"] = morph.english_meaning or w
                object_parts.append(token_entry["english"])

            token_infos.append(token_entry)

        # 3. Assemble SVO English syntax
        assembled_parts = []
        if adverb_parts and is_question:
            assembled_parts.extend(adverb_parts)
        if subject_part:
            assembled_parts.append(subject_part)
        if verb_part:
            assembled_parts.append(verb_part)
        if object_parts:
            assembled_parts.extend(object_parts)
        if adverb_parts and not is_question:
            assembled_parts.extend(adverb_parts)

        final_sentence = " ".join(assembled_parts).strip()
        if not final_sentence:
            final_sentence = " ".join(t["english"] for t in token_infos)

        # Capitalize and add proper punctuation
        final_sentence = final_sentence[0].upper() + final_sentence[1:] if final_sentence else ""
        if is_question and not final_sentence.endswith("?"):
            final_sentence += "?"
        elif not is_question and not final_sentence.endswith("."):
            final_sentence += "."

        tg = kannada_to_tigalari(norm_kn)
        lat = kannada_to_latin(norm_kn)

        return TranslationResult(
            source_text=text,
            source_lang="tulu",
            translated_text=final_sentence,
            tulu_kannada=norm_kn,
            tulu_tigalari=tg,
            tulu_latin=lat,
            tokens=token_infos,
            confidence=0.92,
            grammar_notes=grammar_notes or ["Rule-based morphological SOV -> SVO translation."],
        )

    @classmethod
    def translate_english_to_tulu(cls, text: str) -> TranslationResult:
        """Translates an English sentence into authentic Tulu with Tigalari script."""
        clean = " ".join(text.strip().split()).rstrip(".!?,")
        lower = clean.lower()

        # 1. Check exact phrase corpus match
        for kn, eng in TULU_ENGLISH_PHRASE_CORPUS.items():
            if lower == eng.lower().rstrip(".!?"):
                tg = kannada_to_tigalari(kn)
                lat = kannada_to_latin(kn)
                return TranslationResult(
                    source_text=text,
                    source_lang="english",
                    translated_text=kn,
                    tulu_kannada=kn,
                    tulu_tigalari=tg,
                    tulu_latin=lat,
                    tokens=[{"english": clean, "tulu": kn}],
                    confidence=0.98,
                    grammar_notes=["Direct idiom and conversational match."],
                )

        # 2. Pattern-based structural translation (SVO -> SOV)
        tulu_subject = ""
        tulu_objects = []
        tulu_verb = ""
        tulu_question = ""
        grammar_notes = []

        tokens = re.findall(r"\b[a-zA-Z']+\b", lower)

        # Detect Subject
        subj_person = "3sg"
        if "i" in tokens:
            tulu_subject = "ಯಾನ್"
            subj_person = "1sg"
        elif "we" in tokens:
            tulu_subject = "ನಮ"
            subj_person = "1pl"
        elif "you" in tokens:
            tulu_subject = "ಈರ್"
            subj_person = "2sg_polite"
        elif "he" in tokens:
            tulu_subject = "ಆಯೆ"
            subj_person = "3sg_masc"
        elif "she" in tokens:
            tulu_subject = "ಆಲ್"
            subj_person = "3sg_fem"
        elif "they" in tokens:
            tulu_subject = "ಆಕುಲು"
            subj_person = "3pl"

        # Detect Questions
        if "where" in tokens:
            tulu_question = "ಒಲ್ಪ"
            if "to" in tokens or "going" in tokens:
                tulu_question = "ಓಡೆಗ್"
        elif "what" in tokens:
            tulu_question = "ದಾನೆ"
        elif "why" in tokens:
            tulu_question = "ದಾಯೆ"
        elif "how" in tokens:
            tulu_question = "ಎಂಚ"
        elif "when" in tokens:
            tulu_question = "ಏಪ"

        # Detect Targets / Objects / Cases
        if "house" in tokens or "home" in tokens:
            if "to" in tokens:
                tulu_objects.append("ಇಲ್ಲಗ್")  # Dative
                grammar_notes.append("Destination 'house' takes Dative case (-ಗ್).")
            elif "in" in tokens or "at" in tokens:
                tulu_objects.append("ಇಲ್ಲಡ್")  # Locative
                grammar_notes.append("Location 'house' takes Locative case (-ಡ್).")
            else:
                tulu_objects.append("ಇಲ್ಲ")
        elif "mangalore" in tokens:
            if "to" in tokens:
                tulu_objects.append("ಕುಡ್ಲಗ್")
            elif "in" in tokens or "at" in tokens:
                tulu_objects.append("ಕುಡ್ಲಡ್")
            else:
                tulu_objects.append("ಕುಡ್ಲ")
        elif "school" in tokens:
            tulu_objects.append("ಶಾಲೆಗ್" if "to" in tokens else "ಶಾಲೆ")
        elif "tea" in tokens:
            tulu_objects.append("ಚಾ")
        elif "water" in tokens:
            tulu_objects.append("ನೀರ್")
        elif "milk" in tokens:
            tulu_objects.append("ಪೇರ್")
        elif "food" in tokens or "meal" in tokens:
            tulu_objects.append("ವಣಸ್")
        elif "rain" in tokens:
            tulu_objects.append("ಬರ್ಸ")
        elif "name" in tokens:
            tulu_objects.append("ಪುದರ್")
            if "your" in tokens:
                tulu_subject = "ಈರೆನ"

        # Detect Tense and Conjugate Verb
        is_past = any(w in tokens for w in ["went", "came", "ate", "drank", "did", "had", "arrived"])
        is_neg = any(w in tokens for w in ["not", "no", "never", "cannot", "don't", "didn't"])
        is_imperative = any(w in tokens for w in ["please", "sit", "wait", "stand", "speak"])

        if "go" in tokens or "going" in tokens or "went" in tokens:
            if is_past:
                tulu_verb = "ಪೋಯೆ" if subj_person == "1sg" else ("ಪೋಯೆರ್" if "2" in subj_person or "3pl" in subj_person else "ಪೋಂಡ್")
            elif is_neg:
                tulu_verb = "ಪೋಪುಜಿ"
            else:
                tulu_verb = "ಪೋಪೆ" if subj_person == "1sg" else ("ಪೋಪರ್" if "2" in subj_person or "3pl" in subj_person else "ಪೋಪುಂಡು")
        elif "come" in tokens or "coming" in tokens or "came" in tokens:
            if is_past:
                tulu_verb = "ಬತ್ತೆ" if subj_person == "1sg" else ("ಬತ್ತೆರ್" if "2" in subj_person or "3pl" in subj_person else "ಬತ್ತ್ಂಡ್")
            elif is_neg:
                tulu_verb = "ಬರ್ಪುಜಿ"
            else:
                tulu_verb = "ಬರ್ಪೆ" if subj_person == "1sg" else ("ಬರ್ಪರ್" if "2" in subj_person or "3pl" in subj_person else "ಬರ್ಪುಂಡು")
        elif "eat" in tokens or "ate" in tokens or "eating" in tokens:
            tulu_verb = "ತಿಂದೆ" if is_past else "ತಿನ್ಪೆ"
        elif "drink" in tokens or "drank" in tokens:
            tulu_verb = "ಪರಿಯೆ" if is_past else "ಪರ್ಪೆ"
        elif "sit" in tokens:
            tulu_verb = "ಕುಲ್ಲುಲೆ"
        elif "wait" in tokens or "stand" in tokens:
            tulu_verb = "ಉಂತುಲೆ"
        elif "speak" in tokens:
            tulu_verb = "ಪಾತೆರ್ಲೆ"

        # Assemble Tulu SOV Sentence
        components = []
        if tulu_subject:
            components.append(tulu_subject)
        if tulu_objects:
            components.extend(tulu_objects)
        if tulu_question:
            components.append(tulu_question)
        if tulu_verb:
            components.append(tulu_verb)

        if not components:
            # Fallback dictionary matching for individual words
            for w in tokens:
                d = lookup_tulu(w)
                if d:
                    components.append(d[0]["kannada"])
                else:
                    components.append(w)

        tulu_kn = " ".join(components)
        tulu_tg = kannada_to_tigalari(tulu_kn)
        tulu_lat = kannada_to_latin(tulu_kn)

        return TranslationResult(
            source_text=text,
            source_lang="english",
            translated_text=tulu_kn,
            tulu_kannada=tulu_kn,
            tulu_tigalari=tulu_tg,
            tulu_latin=tulu_lat,
            tokens=[{"word": w} for w in tokens],
            confidence=0.90,
            grammar_notes=grammar_notes or ["Rule-based English SVO -> Tulu SOV transformation."],
        )

    @classmethod
    def translate_tulu_to_kannada(cls, text: str, romanized_output: bool = True) -> TranslationResult:
        """
        Translates Tulu sentence into Kannada (end-to-end Romanized pipeline).
        Examples:
          - 'yaan illag barpe' -> 'naanu manege baruttEne'
          - 'eer olpa poopar' -> 'neevu ellige hooguttaare'
        """
        raw = (text or "").strip()
        if not raw:
            return TranslationResult(
                source_text="", source_lang="tulu", translated_text="",
                tulu_kannada="", tulu_tigalari="", tulu_latin="",
                tulu_romanized="", kannada_romanized="",
                tokens=[], confidence=0.0, grammar_notes=["Empty input."]
            )

        from kannada_tigalari_converter.lexicon.romanization_scheme import to_canonical_roman, from_canonical_roman
        tulu_rom = to_canonical_roman(raw)
        words = tulu_rom.split()

        PRONOUN_MAP_TULU_KN = {
            "yaan": "naanu", "yana": "naanu", "emk": "nanage", "enna": "nanna",
            "nama": "naavu", "namk": "namage", "namma": "namma",
            "ee": "neenu", "eena": "ninna", "nikk": "ninage", "ninna": "ninna",
            "eer": "neevu", "eereg": "nimage", "eerena": "nimma",
            "aaye": "avanu", "aayag": "avanige", "aayana": "avana",
            "aal": "avaLu", "aaleg": "avaLige", "aalena": "avaLa",
            "akulu": "avaru", "akuleg": "avarige", "akulena": "avara",
            "avu": "adu", "ayikk": "adakke", "ayita": "adara",
            "undu": "idu", "undek": "idakke", "undeta": "idara"
        }

        NOUN_ROOT_MAP = {
            "illa": "mane", "ill": "mane",
            "kuDla": "mangaLooru",
            "mara": "mara", "kaNDo": "hola", "kaNDa": "hola",
            "baasae": "bhaaShe", "baase": "bhaaShe",
            "barsa": "maLe",
            "pudar": "hesaru",
            "neeru": "neeru", "peer": "haalu",
            "chaaha": "chaaha", "vanas": "ooTa",
            "dina": "dina", "bEle": "kelasa", "bele": "kelasa"
        }

        CASE_MAP_TULU_KN = [
            ("oTTugu", "oMdiGe"),
            ("ard", "inda"),
            ("erd", "inda"),
            ("rd", "inda"),
            ("aD", "alli"),
            ("eD", "alli"),
            ("D", "alli"),
            ("T", "dalli"),
            ("ag", "ge"),
            ("eg", "ge"),
            ("g", "ge"),
            ("k", "kke"),
            ("da", "da"),
            ("na", "na"),
            ("n", "annu"),
        ]

        INTERROGATIVE_MAP = {
            "olpa": "ellige", "oodeg": "ellige",
            "daada": "eenu", "daaye": "yaake",
            "eMcha": "hege", "eet": "eShTu", "eer": "yaaru"
        }

        kn_tokens = []
        subj = "naanu"

        for w in words:
            w_clean = re.sub(r"[^\w]", "", w).lower()
            if not w_clean:
                continue

            if w_clean in PRONOUN_MAP_TULU_KN:
                kn_p = PRONOUN_MAP_TULU_KN[w_clean]
                kn_tokens.append(kn_p)
                if kn_p in ("naanu", "naavu", "neenu", "neevu", "avanu", "avaLu", "avaru", "adu"):
                    subj = kn_p
                continue

            if w_clean in INTERROGATIVE_MAP:
                kn_tokens.append(INTERROGATIVE_MAP[w_clean])
                continue

            matched_noun = False
            for suf_tu, suf_kn in CASE_MAP_TULU_KN:
                if w_clean.endswith(suf_tu.lower()) and len(w_clean) > len(suf_tu):
                    stem = w_clean[:-len(suf_tu)]
                    kn_stem = NOUN_ROOT_MAP.get(stem, stem)
                    kn_tokens.append(f"{kn_stem}{suf_kn}")
                    matched_noun = True
                    break
            if matched_noun:
                continue

            if w_clean in NOUN_ROOT_MAP:
                kn_tokens.append(NOUN_ROOT_MAP[w_clean])
                continue

            # Verb stem conjugations
            if w_clean.startswith("barp") or w_clean.startswith("bar"):
                if w_clean.endswith("e"):
                    kn_tokens.append("baruttEne")
                elif w_clean.endswith("ar") or w_clean.endswith("er"):
                    kn_tokens.append("baruttaare")
                elif w_clean.endswith("uNDu") or w_clean.endswith("u"):
                    kn_tokens.append("baruttade")
                elif "tt" in w_clean or "tte" in w_clean:
                    kn_tokens.append("baMde" if subj == "naanu" else "baMdaru")
                else:
                    kn_tokens.append("baruttEne")
                continue

            if w_clean.startswith("poop") or w_clean.startswith("pOp") or w_clean.startswith("poo"):
                if w_clean.endswith("e"):
                    kn_tokens.append("hooguttEne")
                elif w_clean.endswith("ar") or w_clean.endswith("er"):
                    kn_tokens.append("hooguttaare")
                elif "ye" in w_clean or "te" in w_clean:
                    kn_tokens.append("hOode" if subj == "naanu" else "hOodaru")
                else:
                    kn_tokens.append("hooguttEne")
                continue

            if w_clean.startswith("tinp") or w_clean.startswith("tin"):
                kn_tokens.append("tinnuttEne" if w_clean.endswith("e") else "tinnuttaare")
                continue

            if w_clean.startswith("malp") or w_clean.startswith("malt"):
                kn_tokens.append("maaDuttEne" if w_clean.endswith("e") else "maaDuttaare")
                continue

            kn_tokens.append(w_clean)

        kn_romanized = " ".join(kn_tokens)
        if raw.endswith("?"):
            kn_romanized += "?"
        elif not kn_romanized.endswith((".", "!", "?")):
            kn_romanized += "."

        kn_cosmetic = from_canonical_roman(kn_romanized, to_script="kannada")
        tulu_cosmetic_kn = from_canonical_roman(tulu_rom, to_script="kannada")
        tulu_cosmetic_tg = from_canonical_roman(tulu_rom, to_script="tigalari")

        return TranslationResult(
            source_text=raw,
            source_lang="tulu",
            translated_text=kn_romanized if romanized_output else kn_cosmetic,
            tulu_kannada=tulu_cosmetic_kn,
            tulu_tigalari=tulu_cosmetic_tg,
            tulu_latin=tulu_rom,
            tulu_romanized=tulu_rom,
            kannada_romanized=kn_romanized,
            tokens=[{"word": w} for w in words],
            confidence=0.95,
            grammar_notes=["End-to-end Romanized Tulu -> Kannada MT rule transformation."]
        )

    @classmethod
    def _lookup_noun_base(cls, lemma: str) -> str:
        """Looks up the English meaning of a base noun."""
        d = lookup_tulu(lemma)
        if d:
            clean = d[0]["english"].split("/")[0].strip()
            return clean.lower()
        return lemma

    @classmethod
    def _format_verb_phrase(cls, morph: Any, subject: str) -> str:
        """Constructs an English verb phrase matching tense and person."""
        lemma = morph.lemma_kannada
        # Extract English action
        act = morph.english_meaning or ""
        if act and (" " in act or "/" in act):
            act = act.split("/")[0].strip()

        if "come" in act or lemma in ("ಬಲೆ", "ಬರ್", "ಬರ್ಪು"):
            if morph.tense == Tense.PRESENT:
                return "am coming" if subject == "I" else "is coming / comes"
            elif morph.tense == Tense.PAST:
                return "came / arrived"
            elif morph.is_negative:
                return "does not come / will not come"
            return "comes"

        if "go" in act or lemma in ("ಪೋ", "ಪೋಪ"):
            if morph.tense == Tense.PRESENT:
                return "am going" if subject == "I" else "is going / goes"
            elif morph.tense == Tense.PAST:
                return "went"
            elif morph.is_negative:
                return "is not going"
            return "goes"

        if "eat" in act or lemma in ("ತಿನ್", "ತಿನ್ಲೆ"):
            return "ate" if morph.tense == Tense.PAST else "am eating / eat"

        if "drink" in act or lemma in ("ಪರ್", "ಪರ್ಲೆ"):
            return "drank" if morph.tense == Tense.PAST else "am drinking / drink"

        if morph.is_negative:
            return f"did not {act or lemma}"
        if morph.tense == Tense.PAST:
            return f"{act}ed" if act and not act.endswith("ed") else act or lemma
        return act or lemma
