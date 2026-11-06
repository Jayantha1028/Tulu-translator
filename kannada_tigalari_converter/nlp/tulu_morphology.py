"""
Tulu Morphological Analyzer & Lemmatizer (ತುಳು ರೂಪಿಮಾ ವಿಶ್ಲೇಷಣೆ)
═══════════════════════════════════════════════════════════════════
Finite-state rule-based morphological engine for the Tulu (ತುಳು)
Dravidian language. Supports:

  1. LEMMATIZATION     – strip inflectional suffixes to recover the
                         dictionary base form (lemma) of any Tulu word.
  2. MORPHEME PARSING  – decompose an inflected word into a structured
                         chain of (lemma, morpheme_tag, suffix) tuples.
  3. NOUN DECLENSION   – generate all 8 case forms of any Tulu noun.
  4. VERB CONJUGATION  – generate tense × person × number × polarity
                         paradigm tables for any Tulu verb stem.
  5. POS TAGGING       – predict Part-of-Speech for standalone words.

Linguistic reference:
  • Rev. August Männer (1886), Basel Mission Tulu-English Dictionary.
  • Upadhyaya (1988), Tulu Lexicon, Rashtrakavi Govinda Pai Institute.
  • Bhat (1998), "Tulu", in Steever (ed.) The Dravidian Languages.
  • Narayanan & Aepli (2024), LREC-COLING 2024 – Tulu NMT.

Unicode: All Kannada-script processing uses U+0C80–U+0CFF.
         Tigalari output via kannada_to_tigalari() mapping.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple

try:
    from kannada_tigalari_converter.core import (
        kannada_to_tigalari,
        tigalari_to_kannada,
        kannada_to_latin,
        latin_to_kannada,
        detect_script,
    )
    from kannada_tigalari_converter.lexicon import (
        WORDS_DATASET_1000,
        HISTORICAL_TULU_CORPUS,
    )
except (ImportError, ModuleNotFoundError):
    from core import (
        kannada_to_tigalari,
        tigalari_to_kannada,
        kannada_to_latin,
        latin_to_kannada,
        detect_script,
    )
    from lexicon import (
        WORDS_DATASET_1000,
        HISTORICAL_TULU_CORPUS,
    )


# ═══════════════════════════════════════════════════════════════
#  1.  ENUMERATIONS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════

class POS(str, Enum):
    """Part-of-Speech tags for Tulu words."""
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    POSTPOSITION = "postposition"
    PARTICLE = "particle"
    NUMERAL = "numeral"
    UNKNOWN = "unknown"


class Case(str, Enum):
    """Tulu noun cases (8-case Dravidian system)."""
    NOMINATIVE = "nominative"          # ∅
    ACCUSATIVE = "accusative"          # -ನ್ / -ನು (-n / -nu)
    DATIVE = "dative"                  # -ಗ್ / -ಗು / -ಕ್ (-g / -gu / -k)
    GENITIVE = "genitive"              # -ದ / -ನ (-da / -na)
    LOCATIVE = "locative"              # -ಡ್ / -ಡು / -ಟ್ (-D / -Du / -T)
    ABLATIVE = "ablative"              # -ರ್ದ್ / -ಡ್ದ್ (-rd / -dd)
    INSTRUMENTAL = "instrumental"      # -ಡ / -ಡೆ (-Da / -De)
    SOCIATIVE = "sociative"            # -ೊಟ್ಟುಗು (-oTTugu)


class Tense(str, Enum):
    """Tulu verb tenses."""
    PRESENT = "present"
    PAST = "past"
    FUTURE = "future"


class Person(str, Enum):
    """Grammatical person."""
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"


class Number(str, Enum):
    """Grammatical number."""
    SINGULAR = "singular"
    PLURAL = "plural"


class Mood(str, Enum):
    """Verb mood."""
    INDICATIVE = "indicative"
    IMPERATIVE = "imperative"
    OBLIGATIVE = "obligative"       # -ಒಡು (-oDu) "must"
    CONDITIONAL = "conditional"     # -ಂಡ (-MDa) / -ಡಿ (-Di)
    NEGATIVE = "negative"           # -ಜಿ (-ji) / -ಇಜಿ (-iji)
    POTENTIAL = "potential"          # -ಉಂಡು (-uMDu)
    INFINITIVE = "infinitive"       # -ಯೆರೆ (-yere) / -ಅರೆ (-are)
    GERUND = "gerund"               # -ನಗ (-naga) / -ದ್ (-d)


@dataclass(frozen=True)
class Morpheme:
    """A single morpheme identified during analysis."""
    surface: str          # Surface form in Kannada script
    latin: str            # Latin phonetic representation
    tag: str              # Morphological tag, e.g. "DAT", "PST.1SG"
    gloss: str            # English-language gloss


@dataclass
class MorphAnalysis:
    """Complete morphological analysis of a Tulu word."""
    surface_word: str               # Original inflected form (Kannada)
    surface_latin: str              # Latin phonetic of surface word
    lemma_kannada: str              # Recovered base form (Kannada)
    lemma_latin: str                # Latin phonetic of lemma
    lemma_tigalari: str             # Tigalari script of lemma
    pos: POS                        # Part-of-speech
    morphemes: List[Morpheme]       # Ordered morpheme chain
    case: Optional[Case] = None     # Noun case (if applicable)
    tense: Optional[Tense] = None
    person: Optional[Person] = None
    number: Optional[Number] = None
    mood: Optional[Mood] = None
    is_negative: bool = False
    english_meaning: str = ""       # Dictionary meaning if found
    confidence: float = 1.0         # 0.0–1.0 analysis confidence

    def tag_string(self) -> str:
        """Returns a compact morphological tag string.
        e.g. 'NOUN.DAT', 'VERB.PST.1SG', 'VERB.NEG'
        """
        parts = [self.pos.value.upper()]
        if self.case:
            parts.append(self.case.value[:3].upper())
        if self.tense:
            parts.append(self.tense.value[:3].upper())
        if self.person:
            parts.append(self.person.value)
        if self.number:
            parts.append(self.number.value[:2].upper())
        if self.mood and self.mood not in (Mood.INDICATIVE,):
            parts.append(self.mood.value[:3].upper())
        if self.is_negative:
            parts.append("NEG")
        return ".".join(parts)

    def to_dict(self) -> Dict:
        """Serialize to a plain dict for JSON / CSV export."""
        return {
            "surface_word": self.surface_word,
            "surface_latin": self.surface_latin,
            "lemma_kannada": self.lemma_kannada,
            "lemma_latin": self.lemma_latin,
            "lemma_tigalari": self.lemma_tigalari,
            "pos": self.pos.value,
            "tag": self.tag_string(),
            "case": self.case.value if self.case else None,
            "tense": self.tense.value if self.tense else None,
            "person": self.person.value if self.person else None,
            "number": self.number.value if self.number else None,
            "mood": self.mood.value if self.mood else None,
            "is_negative": self.is_negative,
            "english_meaning": self.english_meaning,
            "confidence": self.confidence,
            "morphemes": [
                {"surface": m.surface, "latin": m.latin,
                 "tag": m.tag, "gloss": m.gloss}
                for m in self.morphemes
            ],
        }


@dataclass
class DeclensionTable:
    """Complete case declension paradigm for a noun."""
    lemma_kannada: str
    lemma_latin: str
    forms: Dict[Case, List[Dict[str, str]]]  # case -> [{kannada, latin, tigalari}]


@dataclass
class ConjugationTable:
    """Complete conjugation paradigm for a verb."""
    lemma_kannada: str
    lemma_latin: str
    forms: Dict[str, Dict[str, str]]  # "tense.person.number" -> {kannada, latin, tigalari}
    irregular_forms: Dict[str, Dict[str, str]] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
#  2.  LEXICON & LEMMA LOOKUP TABLE
# ═══════════════════════════════════════════════════════════════

def _build_lemma_index() -> Dict[str, Dict]:
    """
    Lazily builds a Kannada-script lemma → dict-entry index from both
    the 1,000-word dataset and the 204-entry historical dictionary.
    """
    index: Dict[str, Dict] = {}

    # Import here to avoid circular imports at module level
    try:
        try:
            from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000
        except (ImportError, ModuleNotFoundError):
            from lexicon.words_dataset_1000 import WORDS_DATASET_1000
        for item in WORDS_DATASET_1000:
            kn = item["kannada"].strip()
            if kn and kn not in index:
                index[kn] = {
                    "kannada": kn,
                    "latin": item["latin_phonetic"],
                    "english": item["english_meaning"],
                    "category": item["category"],
                    "tigalari": item.get("expected_tigalari", ""),
                }
    except ImportError:
        pass

    try:
        try:
            from kannada_tigalari_converter.lexicon.historical_dictionary import HISTORICAL_TULU_CORPUS
        except (ImportError, ModuleNotFoundError):
            from lexicon.historical_dictionary import HISTORICAL_TULU_CORPUS
        for item in HISTORICAL_TULU_CORPUS:
            kn = item["tulu_kannada"].strip()
            if kn and kn not in index:
                index[kn] = {
                    "kannada": kn,
                    "latin": item["tulu_latin"],
                    "english": item["english"],
                    "category": item.get("domain", ""),
                    "tigalari": item.get("tulu_tigalari", ""),
                    "pos": item.get("part_of_speech", ""),
                }
    except ImportError:
        pass

    return index


# Lazy singleton
_LEMMA_INDEX: Optional[Dict[str, Dict]] = None


def _get_lemma_index() -> Dict[str, Dict]:
    global _LEMMA_INDEX
    if _LEMMA_INDEX is None:
        _LEMMA_INDEX = _build_lemma_index()
    return _LEMMA_INDEX


def lookup_lemma(word_kannada: str) -> Optional[Dict]:
    """Look up a Kannada-script word in the combined lexicon."""
    return _get_lemma_index().get(word_kannada.strip())


# ═══════════════════════════════════════════════════════════════
#  3.  TULU NOUN CASE SUFFIX TABLES
# ═══════════════════════════════════════════════════════════════

# Each tuple: (suffix_kannada, suffix_latin, Case, gloss)
# Ordered longest-first for greedy matching.
NOUN_CASE_SUFFIXES: List[Tuple[str, str, Case, str]] = [
    # Sociative (longest)
    ("ೊಟ್ಟುಗು", "oTTugu", Case.SOCIATIVE, "together with"),
    ("ಒಟ್ಟುಗು", "oTTugu", Case.SOCIATIVE, "together with"),

    # Ablative
    ("ರ್ದ್",   "rd",     Case.ABLATIVE, "from"),
    ("ಡ್ದ್",   "dd",     Case.ABLATIVE, "from"),
    ("ರ್ದು",   "rdu",    Case.ABLATIVE, "from"),

    # Instrumental
    ("ಡೆ",     "De",     Case.INSTRUMENTAL, "by means of"),
    ("ಡ",      "Da",     Case.INSTRUMENTAL, "by / with"),

    # Locative
    ("ಡ್",     "D",      Case.LOCATIVE, "in / at"),
    ("ಡು",     "Du",     Case.LOCATIVE, "in / at"),
    ("ಟ್",     "T",      Case.LOCATIVE, "at / near"),

    # Genitive
    ("ದ",      "da",     Case.GENITIVE, "of"),
    ("ನ",      "na",     Case.GENITIVE, "of"),

    # Dative
    ("ಗ್",     "g",      Case.DATIVE, "to / for"),
    ("ಗು",     "gu",     Case.DATIVE, "to / for"),
    ("ಕ್",     "k",      Case.DATIVE, "to / for"),

    # Accusative
    ("ನ್",     "n",      Case.ACCUSATIVE, "object marker"),
    ("ನು",     "nu",     Case.ACCUSATIVE, "object marker"),
]

# Additional noun number suffixes that appear before case markers
NOUN_PLURAL_SUFFIXES: List[Tuple[str, str, str]] = [
    ("ಕುಲು",   "kulu",   "plural (collective)"),
    ("ಲು",     "lu",     "plural"),
    ("ಕ್ಲು",   "klu",    "plural"),
    ("ಕ್ಳು",   "kLu",    "plural"),
    ("ಕಳ್",    "kaL",    "plural"),
    ("ಳು",     "Lu",     "plural"),
    ("ೆರ್",    "er",     "plural (human)"),
    ("ರ್",     "r",      "plural (human)"),
]

# Oblique plural stems (before case markers: -ಕುಲೆಡ್, -ಕುಲೆಗ್, -ರೆಡ್, etc.)
NOUN_PLURAL_OBLIQUE_SUFFIXES: List[Tuple[str, str, str]] = [
    ("ಕುಲೆ",   "kule",   "plural oblique"),
    ("ಗುಲೆ",   "gule",   "plural oblique"),
    ("ಕ್ಲೆ",   "kle",    "plural oblique"),
    ("ಕ್ಳೆ",   "kLe",    "plural oblique"),
    ("ರೆ",     "re",     "plural oblique (human)"),
    ("ಲೆ",     "le",     "plural oblique"),
]

# Tulu enclitics that attach to inflected nouns, pronouns, or verbs
CLITIC_SUFFIXES: List[Tuple[str, str, str, str]] = [
    ("ಲಾ",    "laa",    "CLITIC.ALSO", "also / too"),
    ("ನೇ",    "nE",     "CLITIC.EMPH", "indeed / emphatic"),
]


# ═══════════════════════════════════════════════════════════════
#  4.  TULU VERB SUFFIX TABLES
# ═══════════════════════════════════════════════════════════════

# Imperative polite suffixes (strip to get verb stem)
VERB_IMPERATIVE_SUFFIXES: List[Tuple[str, str]] = [
    ("ುಲೆ",   "ule"),    # ಮಲ್ಪುಲೆ -> ಮಲ್ಪ್ (malpule -> malp)
    ("್ಲೆ",   "le"),     # ತಿನ್ಲೆ -> ತಿನ್ (tinle -> tin)
    ("ಲೆ",    "le"),     # ಬಲೆ -> ಬ (bale -> ba- / bar-)
]

# Present tense conjugation suffixes
# (suffix_kannada, suffix_latin, person, number)
VERB_PRESENT_SUFFIXES: List[Tuple[str, str, Person, Number]] = [
    ("್ಪೆ",   "pe",   Person.FIRST,  Number.SINGULAR),   # barpe = I come
    ("ುವೆ",   "uve",  Person.FIRST,  Number.SINGULAR),   # malpuve = I do
    ("ಪೆ",    "pe",   Person.FIRST,  Number.SINGULAR),   # barepe = I write
    ("್ಪರ್",  "par",  Person.THIRD,  Number.PLURAL),     # barpar = they come
    ("ುವರ್",  "uvar", Person.THIRD,  Number.PLURAL),     # malpuvar
    ("ಪರ್",   "par",  Person.THIRD,  Number.PLURAL),
    ("್ಪಲ್",  "pal",  Person.THIRD,  Number.SINGULAR),   # 3sg fem
    ("ುವಲ್",  "uval", Person.THIRD,  Number.SINGULAR),   # nalipuval
    ("ುಂಡು",  "uMDu", Person.THIRD,  Number.SINGULAR),   # continuative 3sg
    ("ುಂಡ್",  "uMD",  Person.THIRD,  Number.SINGULAR),
]

# Past tense suffixes
VERB_PAST_SUFFIXES: List[Tuple[str, str, Person, Number]] = [
    ("ಿಯೆರ್",  "iyer",  Person.THIRD,  Number.PLURAL),
    ("ಿಯೆ",    "iye",   Person.FIRST,  Number.SINGULAR),
    ("ೋಯೆರ್",  "Oyer",  Person.THIRD,  Number.PLURAL),   # pOyer
    ("ೋಯೆ",    "Oye",   Person.FIRST,  Number.SINGULAR),  # pOye
    ("್ಯೆರ್",  "yer",   Person.THIRD,  Number.PLURAL),
    ("್ಯೆ",    "ye",    Person.FIRST,  Number.SINGULAR),
    ("ೆರ್",    "er",    Person.THIRD,  Number.PLURAL),    # batter, jetter
    ("ೆ",      "e",     Person.FIRST,  Number.SINGULAR),  # malte, kalte, jette
    ("್ಂಡ್",   "MD",    Person.THIRD,  Number.SINGULAR),  # battMD (neuter)
    ("ಂಡ್",    "MD",    Person.THIRD,  Number.SINGULAR),
    ("ಂಡೆ",    "MDe",   Person.FIRST,  Number.SINGULAR),  # detoMDe
]

# Obligative / must: -ಒಡು (-oDu)
VERB_OBLIGATIVE_SUFFIXES: List[Tuple[str, str]] = [
    ("ೊಡು",   "oDu"),    # toovoDu, pOvoDu
    ("್ನೊಡು", "noDu"),   # tinnoDu
    ("ೋವೊಡು", "OvoDu"),  # pOvoDu
]

# Negative suffixes
VERB_NEGATIVE_SUFFIXES: List[Tuple[str, str]] = [
    ("ಿಜಿ",   "iji"),    # teriyiji, aayiji
    ("ಿಜ್ಜಿ",  "ijji"),   # ijji, teridijji
    ("ಜಿ",    "ji"),     # tikkiji
    ("ಚಿ",    "chi"),    # boDchi
]

# Potential / stative: -ಉಂಡು (-uMDu)
VERB_POTENTIAL_SUFFIXES: List[Tuple[str, str]] = [
    ("ುಂಡು",  "uMDu"),   # teriyuMDu, aapuMDu, tikkuMDu
    ("ುಂಡ್",  "uMD"),
    ("ುಂಡಾ",  "uMDaa"),  # gottuMDaa (interrogative potential)
]

# Infinitive: -ಯೆರೆ / -ಅರೆ / -ಎರೆ
VERB_INFINITIVE_SUFFIXES: List[Tuple[str, str]] = [
    ("ಿಯೆರೆ",  "iyere"),  # bariyere
    ("ಿಯೆರಾ",  "iyeraa"), # interrogative inf.
    ("್ಯೆರೆ",  "yere"),
    ("ೆರೆ",    "ere"),    # meeyere, kalpere
    ("ೆರಾ",    "eraa"),   # pariyeraa
]

# Gerund / participial: -ನಗ / -ದ್
VERB_GERUND_SUFFIXES: List[Tuple[str, str]] = [
    ("ನ್ನಗ",  "nnaga"),   # bannaga
    ("ೋನಗ",   "Onaga"),   # pOnaga
    ("ನಗ",    "naga"),
]


# ═══════════════════════════════════════════════════════════════
#  5.  KNOWN IRREGULAR VERB STEMS (Tulu suppletive paradigms)
# ═══════════════════════════════════════════════════════════════

# Maps conjugated stem (Kannada) -> (lemma_kannada, lemma_latin, english)
# Tulu has several verbs with suppletive (irregular) stem alternation.
IRREGULAR_VERB_MAP: Dict[str, Tuple[str, str, str]] = {
    # bar- / batt- (come)
    "ಬರ್":    ("ಬಲೆ", "bale", "Come"),
    "ಬರ":     ("ಬಲೆ", "bale", "Come"),
    "ಬತ್ತ್":   ("ಬಲೆ", "bale", "Come"),
    "ಬನ್":    ("ಬಲೆ", "bale", "Come"),
    "ಬತ್ತ":   ("ಬಲೆ", "bale", "Come"),
    # pO- / pOy- (go)
    "ಪೋ":     ("ಪೋಲೆ", "pOle", "Go"),
    "ಪೋಯ":   ("ಪೋಲೆ", "pOle", "Go"),
    "ಪೋಪ":   ("ಪೋಲೆ", "pOle", "Go"),
    # tin- / tiMd- (eat)
    "ತಿನ್":   ("ತಿನ್ಲೆ", "tinle", "Eat"),
    "ತಿಂದ":   ("ತಿನ್ಲೆ", "tinle", "Eat"),
    "ತಿನ್ನ":  ("ತಿನ್ಲೆ", "tinle", "Eat"),
    # par- / part- (drink)
    "ಪರ್":    ("ಪರ್ಲೆ", "parle", "Drink"),
    "ಪರ್ತ":   ("ಪರ್ಲೆ", "parle", "Drink"),
    # too- / tooy- (see)
    "ತೂ":     ("ತೂಲೆ", "toole", "See"),
    "ತೂಯ":   ("ತೂಲೆ", "toole", "See"),
    "ತೂಪ":   ("ತೂಲೆ", "toole", "See"),
    "ತೂವ":   ("ತೂಲೆ", "toole", "See"),
    # kEn- / kEMD- (ask / hear)
    "ಕೇನ್":   ("ಕೇನ್ಲೆ", "kEnle", "Ask / Hear"),
    "ಕೇಂಡ":   ("ಕೇನ್ಲೆ", "kEnle", "Ask / Hear"),
    "ಕೇಲ್":   ("ಕೇನ್ಲೆ", "kEnle", "Ask / Hear"),
    # paater- (speak)
    "ಪಾತೆರ್":  ("ಪಾತೆರ್ಲೆ", "paaterle", "Speak"),
    "ಪಾತೆರ":   ("ಪಾತೆರ್ಲೆ", "paaterle", "Speak"),
    # kull- / kull- (sit)
    "ಕುಲ್ಲ":   ("ಕುಲ್ಲೆ", "kulle", "Sit"),
    "ಕುಲ್":    ("ಕುಲ್ಲೆ", "kulle", "Sit"),
    # uMt- (stand)
    "ಉಂತ":    ("ಉಂತುಲೆ", "uMtule", "Stand"),
    # jep- / jett- (sleep)
    "ಜೆಪ":    ("ಜೆಪುಲೆ", "jepule", "Sleep"),
    "ಜೆಪ್ಪ":   ("ಜೆಪುಲೆ", "jepule", "Sleep"),
    "ಜೆತ್ತ":   ("ಜೆಪುಲೆ", "jepule", "Sleep"),
    # kor- / kori- (give)
    "ಕೊರ್":    ("ಕೊರ್ಲೆ", "korle", "Give"),
    "ಕೊರಿ":    ("ಕೊರ್ಲೆ", "korle", "Give"),
    "ಕೊರ್ಪ":   ("ಕೊರ್ಲೆ", "korle", "Give"),
    # deton- / detoMD- (take)
    "ದೆತೊನ್":   ("ದೆತೊನ್ಲೆ", "detonle", "Take"),
    "ದೆತೊಂಡ":   ("ದೆತೊನ್ಲೆ", "detonle", "Take"),
    # malp- / malt- (do)
    "ಮಲ್ಪ":     ("ಮಲ್ಪುಲೆ", "malpule", "Do"),
    "ಮಲ್ಪು":    ("ಮಲ್ಪುಲೆ", "malpule", "Do"),
    "ಮಲ್ತ":     ("ಮಲ್ಪುಲೆ", "malpule", "Do"),
    # kalp- / kalt- (learn)
    "ಕಲ್ಪ":     ("ಕಲ್ಪುಲೆ", "kalpule", "Learn"),
    "ಕಲ್ಪು":    ("ಕಲ್ಪುಲೆ", "kalpule", "Learn"),
    "ಕಲ್ತ":     ("ಕಲ್ಪುಲೆ", "kalpule", "Learn"),
    # pan- / paMD- (tell)
    "ಪನ್":      ("ಪನ್ಲೆ", "panle", "Tell"),
    "ಪನ್ಪು":    ("ಪನ್ಲೆ", "panle", "Tell"),
    "ಪಂಡ":      ("ಪನ್ಲೆ", "panle", "Tell"),
    "ಪನ್ಪ":     ("ಪನ್ಲೆ", "panle", "Tell"),
    # OD- / ODi- (run)
    "ಓಡ":       ("ಓಡುಲೆ", "ODule", "Run"),
    "ಓಡು":      ("ಓಡುಲೆ", "ODule", "Run"),
    "ಓಡಿ":      ("ಓಡುಲೆ", "ODule", "Run"),
    # nalip- / nalit- (dance)
    "ನಲಿಪ":     ("ನಲಿಪುಲೆ", "nalipule", "Dance"),
    "ನಲಿಪು":    ("ನಲಿಪುಲೆ", "nalipule", "Dance"),
    "ನಲಿತ":     ("ನಲಿಪುಲೆ", "nalipule", "Dance"),
    # paaD- / paaDi- (put)
    "ಪಾಡ":      ("ಪಾಡುಲೆ", "paaDule", "Put"),
    "ಪಾಡು":     ("ಪಾಡುಲೆ", "paaDule", "Put"),
    "ಪಾಡಿ":     ("ಪಾಡುಲೆ", "paaDule", "Put"),
    # barep- / baret- (write)
    "ಬರೆಪ":     ("ಬರೆಪುಲೆ", "barepule", "Write"),
    "ಬರೆಪು":    ("ಬರೆಪುಲೆ", "barepule", "Write"),
    "ಬರೆತ":     ("ಬರೆಪುಲೆ", "barepule", "Write"),
    # Od- / Odi- (read)
    "ಓದ":       ("ಓದುಲೆ", "Odule", "Read"),
    "ಓದು":      ("ಓದುಲೆ", "Odule", "Read"),
    "ಓದಿ":      ("ಓದುಲೆ", "Odule", "Read"),
    # kaap- / kaay- (wait)
    "ಕಾಪ":      ("ಕಾಪುಲೆ", "kaapule", "Wait"),
    "ಕಾಪು":     ("ಕಾಪುಲೆ", "kaapule", "Wait"),
    "ಕಾಯ":      ("ಕಾಪುಲೆ", "kaapule", "Wait"),
    # teriy- (know)
    "ತೆರಿಯ":    ("ತೆರಿಯುಲೆ", "teriyule", "Know"),
    "ತೆರಿದ":    ("ತೆರಿಯುಲೆ", "teriyule", "Know"),
    # gelip- (win)
    "ಗೆಲಿಪ":    ("ಗೆಲಿಪುಲೆ", "gelipule", "Win"),
    "ಗೆಲಿಪು":   ("ಗೆಲಿಪುಲೆ", "gelipule", "Win"),
    # bar- / batt- (come negative / variant stems)
    "ಬರ್ಪು":    ("ಬಲೆ", "bale", "Come"),
    "ಬತ್ತಿ":    ("ಬಲೆ", "bale", "Come"),
    # pO- (go)
    "ಪೋಪು":    ("ಪೋಲೆ", "pOle", "Go"),
    # tin- (eat)
    "ತಿನ್ಪು":    ("ತಿನ್ಲೆ", "tinle", "Eat"),
    # par- (drink)
    "ಪರ್ಪು":    ("ಪರ್ಲೆ", "parle", "Drink"),
    # kor- (give)
    "ಕೊರ್ಪು":   ("ಕೊರ್ಲೆ", "korle", "Give"),
    # kull- / jep- / deton- / uMt-
    "ಕುಲ್ಲು":   ("ಕುಲ್ಲೆ", "kulle", "Sit"),
    "ಜೆಪ್ಪು":   ("ಜೆಪುಲೆ", "jepule", "Sleep"),
    "ದೆತೊನು":   ("ದೆತೊನ್ಲೆ", "detonle", "Take"),
    "ಉಂತು":    ("ಉಂತುಲೆ", "uMtule", "Stand"),
    # existential verbs (suppletive)
    "ಉಲ್ಲ":     ("ಉಂಡು", "uMDu", "Exist"),
    "ಇಜ್ಜ":     ("ಇಜ್ಜಿ", "ijji", "Not exist"),
    # aap- (become/happen)
    "ಆಪ":       ("ಆಪುಂಡು", "aapuMDu", "Happen"),
    "ಆಯ":       ("ಆಪುಂಡು", "aapuMDu", "Happen"),
    # tikk- (get/obtain)
    "ತಿಕ್ಕ":    ("ತಿಕ್ಕುಂಡು", "tikkuMDu", "Obtain"),
    # bOD- (want/need)
    "ಬೋಡ":      ("ಬೋಡು", "bODu", "Want"),
    "ಬೊಡ್":     ("ಬೋಡು", "bODu", "Want"),
}


# ═══════════════════════════════════════════════════════════════
#  6.  TULU PRONOUN TABLE
# ═══════════════════════════════════════════════════════════════

TULU_PRONOUNS: Dict[str, Dict[str, str]] = {
    "ಯಾನ್":      {"latin": "yaan",       "english": "I",                     "person": "1sg",         "lemma": "ಯಾನ್"},
    "ಎಂಕ್":      {"latin": "eMk",        "english": "me / to me",            "person": "1sg.dat",     "lemma": "ಯಾನ್"},
    "ಎನ್ನ":      {"latin": "enna",       "english": "my",                    "person": "1sg.gen",     "lemma": "ಯಾನ್"},
    "ಎನ್ನೊಟ್ಟುಗು": {"latin": "ennoTTugu",  "english": "with me",               "person": "1sg.soc",     "lemma": "ಯಾನ್"},
    "ಎನ್ನರ್ದ್":   {"latin": "ennard",     "english": "from me",               "person": "1sg.abl",     "lemma": "ಯಾನ್"},
    "ನಮ":        {"latin": "nama",       "english": "we",                    "person": "1pl",         "lemma": "ನಮ"},
    "ನಂಕ್":      {"latin": "naMk",       "english": "us / to us",            "person": "1pl.dat",     "lemma": "ನಮ"},
    "ನಮ್ಮ":      {"latin": "namma",      "english": "our",                   "person": "1pl.gen",     "lemma": "ನಮ"},
    "ನಮ್ಮೊಟ್ಟುಗು": {"latin": "nammoTTugu", "english": "with us",               "person": "1pl.soc",     "lemma": "ನಮ"},
    "ನಮ್ಮರ್ದ್":   {"latin": "nammard",    "english": "from us",               "person": "1pl.abl",     "lemma": "ನಮ"},
    "ಈರ್":       {"latin": "eer",        "english": "you (polite)",          "person": "2sg.pol",     "lemma": "ಈರ್"},
    "ಈರೆಗ್":     {"latin": "eereg",      "english": "to you (polite)",       "person": "2sg.pol.dat", "lemma": "ಈರ್"},
    "ಈರೆನ":      {"latin": "eerena",     "english": "your (polite)",         "person": "2sg.pol.gen", "lemma": "ಈರ್"},
    "ಈರೆರ್ದ್":    {"latin": "eererd",     "english": "from you (polite)",     "person": "2sg.pol.abl", "lemma": "ಈರ್"},
    "ಈರೆನೊಟ್ಟುಗು": {"latin": "eerenoTTugu","english": "with you (polite)",     "person": "2sg.pol.soc", "lemma": "ಈರ್"},
    "ಈ":         {"latin": "ee",         "english": "you (familiar)",        "person": "2sg",         "lemma": "ಈ"},
    "ನಿಕ್ಕ್":     {"latin": "nikk",       "english": "to you (familiar)",     "person": "2sg.dat",     "lemma": "ಈ"},
    "ನಿನ್ನ":     {"latin": "ninna",      "english": "your (familiar)",       "person": "2sg.gen",     "lemma": "ಈ"},
    "ಆಯೆ":       {"latin": "aaye",       "english": "he",                    "person": "3sg.m",       "lemma": "ಆಯೆ"},
    "ಆಯಗ್":      {"latin": "aayag",      "english": "to him",                "person": "3sg.m.dat",   "lemma": "ಆಯೆ"},
    "ಆಯನ":       {"latin": "aayana",     "english": "his",                   "person": "3sg.m.gen",   "lemma": "ಆಯೆ"},
    "ಆಲ್":       {"latin": "aal",        "english": "she",                   "person": "3sg.f",       "lemma": "ಆಲ್"},
    "ಆಲೆಗ್":      {"latin": "aaleg",      "english": "to her",                "person": "3sg.f.dat",   "lemma": "ಆಲ್"},
    "ಆಲೆನ":      {"latin": "aalena",     "english": "her",                   "person": "3sg.f.gen",   "lemma": "ಆಲ್"},
    "ಅವು":       {"latin": "avu",        "english": "it",                    "person": "3sg.n",       "lemma": "ಅವು"},
    "ಅಯಿಕ್ಕ್":     {"latin": "ayikk",      "english": "to it",                 "person": "3sg.n.dat",   "lemma": "ಅವು"},
    "ಅಯಿತ":      {"latin": "ayita",      "english": "its",                   "person": "3sg.n.gen",   "lemma": "ಅವು"},
    "ಅಕುಲು":      {"latin": "akulu",      "english": "they",                  "person": "3pl",         "lemma": "ಅಕುಲು"},
    "ಅಕುಲೆಗ್":    {"latin": "akuleg",     "english": "to them",               "person": "3pl.dat",     "lemma": "ಅಕುಲು"},
    "ಅಕುಲೆನ":    {"latin": "akulena",    "english": "their",                 "person": "3pl.gen",     "lemma": "ಅಕುಲು"},
}


# ═══════════════════════════════════════════════════════════════
#  7.  CORE ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════

def _gerund_form(verb: str) -> str:
    """Convert a verb like 'Come' to 'coming' for gerund glosses."""
    v = verb.lower().rstrip()
    # Handle common English irregular gerunds
    _GERUND_MAP = {
        "come": "coming", "go": "going", "eat": "eating",
        "drink": "drinking", "see": "seeing", "give": "giving",
        "take": "taking", "do": "doing", "tell": "telling",
        "run": "running", "sit": "sitting", "stand": "standing",
        "sleep": "sleeping", "write": "writing", "read": "reading",
        "learn": "learning", "dance": "dancing", "put": "putting",
        "wait": "waiting", "know": "knowing", "win": "winning",
        "speak": "speaking", "ask": "asking", "hear": "hearing",
    }
    return _GERUND_MAP.get(v, v + "ing")


def _strip_suffix(word: str, suffix: str) -> Optional[str]:
    """Strip a suffix from a Kannada word, returning the stem or None."""
    if word.endswith(suffix) and len(word) > len(suffix):
        return word[:-len(suffix)]
    return None


def _try_verb_analysis(word_kn: str) -> Optional[MorphAnalysis]:
    """
    Attempt to parse a Tulu verb form by stripping tense/person/number
    suffixes and matching the residual stem against the irregular verb
    map or the lexicon.
    """
    surface_latin = kannada_to_latin(word_kn)

    # Try negative suffixes first (they're distinctive)
    for suffix_kn, suffix_lat in VERB_NEGATIVE_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat, "NEG", "not"),
                    ],
                    mood=Mood.NEGATIVE, is_negative=True,
                    english_meaning=f"Not {eng.lower()}",
                )

    # Try obligative
    for suffix_kn, suffix_lat in VERB_OBLIGATIVE_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat, "OBL", "must"),
                    ],
                    mood=Mood.OBLIGATIVE,
                    english_meaning=f"Must {eng.lower()}",
                )

    # Try infinitive
    for suffix_kn, suffix_lat in VERB_INFINITIVE_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat, "INF", "to (do)"),
                    ],
                    mood=Mood.INFINITIVE,
                    english_meaning=f"To {eng.lower()}",
                )

    # Try gerund
    for suffix_kn, suffix_lat in VERB_GERUND_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat, "GER", "while"),
                    ],
                    mood=Mood.GERUND,
                    english_meaning=f"While {_gerund_form(eng)}",
                )

    # Try potential
    for suffix_kn, suffix_lat in VERB_POTENTIAL_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat, "POT", "is/can"),
                    ],
                    mood=Mood.POTENTIAL,
                    english_meaning=eng,
                )

    # Try past tense (longer suffixes first)
    for suffix_kn, suffix_lat, person, number in VERB_PAST_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat,
                                 f"PST.{person.value}.{number.value[:2].upper()}",
                                 f"past {person.value} {number.value}"),
                    ],
                    tense=Tense.PAST, person=person, number=number,
                    mood=Mood.INDICATIVE,
                    english_meaning=eng,
                )

    # Try present tense
    for suffix_kn, suffix_lat, person, number in VERB_PRESENT_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if stem:
            lemma_info = IRREGULAR_VERB_MAP.get(stem)
            if lemma_info:
                lemma_kn, lemma_lat, eng = lemma_info
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=lemma_kn, lemma_latin=lemma_lat,
                    lemma_tigalari=kannada_to_tigalari(lemma_kn),
                    pos=POS.VERB,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM", eng),
                        Morpheme(suffix_kn, suffix_lat,
                                 f"PRS.{person.value}.{number.value[:2].upper()}",
                                 f"present {person.value} {number.value}"),
                    ],
                    tense=Tense.PRESENT, person=person, number=number,
                    mood=Mood.INDICATIVE,
                    english_meaning=eng,
                )

    return None


def _try_noun_analysis(word_kn: str) -> Optional[MorphAnalysis]:
    """
    Attempt to parse a Tulu noun form by stripping case suffixes,
    oblique plural markers, or nominative plural suffixes, and looking up
    the residual stem in the lexicon.
    """
    surface_latin = kannada_to_latin(word_kn)

    # 1. Try Case Suffixes (with optional oblique plural marker inside)
    for suffix_kn, suffix_lat, case, gloss in NOUN_CASE_SUFFIXES:
        stem = _strip_suffix(word_kn, suffix_kn)
        if not stem:
            continue

        # Check A: Direct lemma lookup of stem
        entry = lookup_lemma(stem)
        if entry:
            return MorphAnalysis(
                surface_word=word_kn, surface_latin=surface_latin,
                lemma_kannada=entry["kannada"],
                lemma_latin=entry["latin"],
                lemma_tigalari=(entry.get("tigalari")
                                or kannada_to_tigalari(entry["kannada"])),
                pos=POS.NOUN,
                morphemes=[
                    Morpheme(stem, kannada_to_latin(stem), "STEM",
                             entry["english"]),
                    Morpheme(suffix_kn, suffix_lat,
                             case.value[:3].upper(), gloss),
                ],
                case=case,
                english_meaning=entry["english"],
            )

        # Check B: Adding back inherent vowel to stem
        for vowel_restore in ["", "ು", "ೆ", "ಿ"]:
            candidate = stem + vowel_restore
            entry = lookup_lemma(candidate)
            if entry:
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=entry["kannada"],
                    lemma_latin=entry["latin"],
                    lemma_tigalari=(entry.get("tigalari")
                                    or kannada_to_tigalari(entry["kannada"])),
                    pos=POS.NOUN,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM",
                                 entry["english"]),
                        Morpheme(suffix_kn, suffix_lat,
                                 case.value[:3].upper(), gloss),
                    ],
                    case=case,
                    english_meaning=entry["english"],
                )

        # Check C: Oblique plural marker before case suffix (e.g. ಇಲ್ಲ + ಕುಲೆ + ಡ್)
        for pl_obl_kn, pl_obl_lat, pl_obl_gloss in NOUN_PLURAL_OBLIQUE_SUFFIXES:
            pl_stem = _strip_suffix(stem, pl_obl_kn)
            if not pl_stem:
                continue
            for vowel_restore in ["", "ು", "ೆ", "ಿ"]:
                candidate = pl_stem + vowel_restore
                entry = lookup_lemma(candidate)
                if entry:
                    return MorphAnalysis(
                        surface_word=word_kn, surface_latin=surface_latin,
                        lemma_kannada=entry["kannada"],
                        lemma_latin=entry["latin"],
                        lemma_tigalari=(entry.get("tigalari")
                                        or kannada_to_tigalari(entry["kannada"])),
                        pos=POS.NOUN,
                        morphemes=[
                            Morpheme(pl_stem, kannada_to_latin(pl_stem), "STEM",
                                     entry["english"]),
                            Morpheme(pl_obl_kn, pl_obl_lat, "PL.OBL", pl_obl_gloss),
                            Morpheme(suffix_kn, suffix_lat,
                                     case.value[:3].upper(), gloss),
                        ],
                        case=case,
                        number=Number.PLURAL,
                        english_meaning=entry["english"],
                    )

    # 2. Try Nominative Plural Suffixes (e.g. ಇಲ್ಲಕುಲು, ಮರಕುಲು)
    for pl_kn, pl_lat, pl_gloss in NOUN_PLURAL_SUFFIXES:
        stem = _strip_suffix(word_kn, pl_kn)
        if not stem:
            continue
        for vowel_restore in ["", "ು", "ೆ", "ಿ"]:
            candidate = stem + vowel_restore
            entry = lookup_lemma(candidate)
            if entry:
                return MorphAnalysis(
                    surface_word=word_kn, surface_latin=surface_latin,
                    lemma_kannada=entry["kannada"],
                    lemma_latin=entry["latin"],
                    lemma_tigalari=(entry.get("tigalari")
                                    or kannada_to_tigalari(entry["kannada"])),
                    pos=POS.NOUN,
                    morphemes=[
                        Morpheme(stem, kannada_to_latin(stem), "STEM",
                                 entry["english"]),
                        Morpheme(pl_kn, pl_lat, "PL", pl_gloss),
                    ],
                    case=Case.NOMINATIVE,
                    number=Number.PLURAL,
                    english_meaning=entry["english"],
                )

    return None


def _try_pronoun(word_kn: str) -> Optional[MorphAnalysis]:
    """Check if the word is a known Tulu pronoun."""
    info = TULU_PRONOUNS.get(word_kn)
    if info:
        lemma_kn = info.get("lemma", word_kn)
        lemma_lat = info.get("latin", kannada_to_latin(lemma_kn))
        return MorphAnalysis(
            surface_word=word_kn,
            surface_latin=info["latin"],
            lemma_kannada=lemma_kn,
            lemma_latin=lemma_lat,
            lemma_tigalari=kannada_to_tigalari(lemma_kn),
            pos=POS.PRONOUN,
            morphemes=[
                Morpheme(word_kn, info["latin"], info["person"],
                         info["english"]),
            ],
            english_meaning=info["english"],
        )
    return None


# ═══════════════════════════════════════════════════════════════
#  8.  PUBLIC API — ANALYZE
# ═══════════════════════════════════════════════════════════════

def analyze(word: str, script: str = "auto") -> MorphAnalysis:
    """
    Perform morphological analysis on a single Tulu word.

    :param word:   The word to analyze (Kannada script, Latin phonetic,
                   or Tigalari script).
    :param script: 'kannada', 'latin', 'tigalari', or 'auto' (detect).
    :returns:      A MorphAnalysis dataclass with lemma, POS, morphemes,
                   case/tense/person/number, and English meaning.

    Examples:
        >>> analyze("ಇಲ್ಲಗ್").tag_string()
        'NOUN.DAT'
        >>> analyze("ಬರ್ಪೆ").lemma_kannada
        'ಬಲೆ'
        >>> analyze("barpe", script="latin").pos
        POS.VERB
    """
    word = word.strip()
    if not word:
        return MorphAnalysis(
            surface_word="", surface_latin="", lemma_kannada="",
            lemma_latin="", lemma_tigalari="", pos=POS.UNKNOWN,
            morphemes=[], confidence=0.0,
        )

    # Normalize to Kannada script for all internal processing
    if script == "auto":
        script = detect_script(word)

    if script == "latin":
        word_kn = latin_to_kannada(word)
    elif script == "tigalari":
        word_kn = tigalari_to_kannada(word)
    else:
        word_kn = word

    surface_latin = kannada_to_latin(word_kn)

    # 1. Try pronoun lookup first (pronouns should not be analyzed as nouns)
    result = _try_pronoun(word_kn)
    if result:
        return result

    # 2. Try verb morphological analysis BEFORE lexicon lookup.
    #    Many conjugated verb forms (ಬರ್ಪೆ, ಬತ್ತ್ಂಡ್, ಪೋಯೆ) are stored
    #    as complete entries in the dataset. We prefer the decomposed
    #    analysis (stem + suffix) over a flat "STEM" tag.
    result = _try_verb_analysis(word_kn)
    if result:
        result.confidence = 0.95
        return result

    # 3. Try noun case analysis (strip case markers) before bare lookup
    result = _try_noun_analysis(word_kn)
    if result:
        result.confidence = 0.9
        return result

    # 4. Direct lexicon lookup (exact match = uninflected lemma / base form)
    entry = lookup_lemma(word_kn)
    if entry:
        pos_str = entry.get("pos", "")
        cat = entry.get("category", "").lower()

        if pos_str:
            pos = POS(pos_str) if pos_str in POS._value2member_map_ else POS.UNKNOWN
        elif "verb" in cat:
            pos = POS.VERB
        elif "adjective" in cat:
            pos = POS.ADJECTIVE
        elif "adverb" in cat:
            pos = POS.ADVERB
        elif "number" in cat or "numeral" in cat:
            pos = POS.NUMERAL
        else:
            pos = POS.NOUN

        return MorphAnalysis(
            surface_word=word_kn, surface_latin=surface_latin,
            lemma_kannada=entry["kannada"],
            lemma_latin=entry["latin"],
            lemma_tigalari=(entry.get("tigalari")
                            or kannada_to_tigalari(entry["kannada"])),
            pos=pos,
            morphemes=[
                Morpheme(word_kn, surface_latin, "STEM", entry["english"]),
            ],
            english_meaning=entry["english"],
            confidence=1.0,
        )

    # 5. Try peeling enclitics (-ಲಾ 'also', -ನೇ 'indeed') from the word
    for clitic_kn, clitic_lat, clitic_tag, clitic_gloss in CLITIC_SUFFIXES:
        if word_kn.endswith(clitic_kn) and len(word_kn) > len(clitic_kn) + 1:
            base_kn = word_kn[:-len(clitic_kn)]
            base_analysis = analyze(base_kn, script="kannada")
            if base_analysis.pos != POS.UNKNOWN and base_analysis.confidence >= 0.5:
                gloss_suffix = f" ({clitic_gloss})" if base_analysis.english_meaning else ""
                return MorphAnalysis(
                    surface_word=word_kn,
                    surface_latin=surface_latin,
                    lemma_kannada=base_analysis.lemma_kannada,
                    lemma_latin=base_analysis.lemma_latin,
                    lemma_tigalari=base_analysis.lemma_tigalari,
                    pos=base_analysis.pos,
                    morphemes=base_analysis.morphemes + [
                        Morpheme(clitic_kn, clitic_lat, clitic_tag, clitic_gloss)
                    ],
                    case=base_analysis.case,
                    tense=base_analysis.tense,
                    person=base_analysis.person,
                    number=base_analysis.number,
                    mood=base_analysis.mood,
                    is_negative=base_analysis.is_negative,
                    english_meaning=f"{base_analysis.english_meaning}{gloss_suffix}",
                    confidence=base_analysis.confidence * 0.95,
                )

    # 6. Fallback: return as unknown with the word itself as lemma
    return MorphAnalysis(
        surface_word=word_kn, surface_latin=surface_latin,
        lemma_kannada=word_kn, lemma_latin=surface_latin,
        lemma_tigalari=kannada_to_tigalari(word_kn),
        pos=POS.UNKNOWN,
        morphemes=[
            Morpheme(word_kn, surface_latin, "UNK", "unknown"),
        ],
        confidence=0.3,
    )


def analyze_sentence(sentence: str, script: str = "auto") -> List[MorphAnalysis]:
    """
    Perform morphological analysis on every word in a sentence.

    :param sentence: Input sentence (any script).
    :param script:   'kannada', 'latin', 'tigalari', or 'auto'.
    :returns:        List of MorphAnalysis, one per whitespace-delimited token.
    """
    if not sentence or not sentence.strip():
        return []

    # Normalize script once
    if script == "auto":
        script = detect_script(sentence)

    tokens = sentence.strip().split()
    return [analyze(token, script=script) for token in tokens]


def lemmatize(word: str, script: str = "auto") -> str:
    """
    Quick lemmatization: returns just the base form (lemma) in Kannada script.

    :param word:   Inflected Tulu word.
    :param script: 'kannada', 'latin', 'tigalari', or 'auto'.
    :returns:      Lemma in Kannada script.

    Examples:
        >>> lemmatize("ಇಲ್ಲಗ್")
        'ಇಲ್ಲ'
        >>> lemmatize("ಬರ್ಪೆ")
        'ಬಲೆ'
        >>> lemmatize("ಬತ್ತ್ಂಡ್")
        'ಬಲೆ'
    """
    return analyze(word, script=script).lemma_kannada


def pos_tag(word: str, script: str = "auto") -> str:
    """
    Quick POS tagging: returns the part-of-speech tag string.

    :param word:   Tulu word.
    :param script: Script hint.
    :returns:      POS tag string (e.g. 'noun', 'verb').
    """
    return analyze(word, script=script).pos.value


# ═══════════════════════════════════════════════════════════════
#  9.  NOUN DECLENSION GENERATOR
# ═══════════════════════════════════════════════════════════════

# For declension generation: representative suffix per case
_DECLENSION_SUFFIXES: Dict[Case, List[Tuple[str, str]]] = {
    Case.NOMINATIVE:   [("", "")],
    Case.ACCUSATIVE:   [("ನ್", "n"), ("ನು", "nu")],
    Case.DATIVE:       [("ಗ್", "g"), ("ಗು", "gu")],
    Case.GENITIVE:     [("ದ", "da"), ("ನ", "na")],
    Case.LOCATIVE:     [("ಡ್", "D"), ("ಡು", "Du")],
    Case.ABLATIVE:     [("ರ್ದ್", "rd")],
    Case.INSTRUMENTAL: [("ಡ", "Da")],
    Case.SOCIATIVE:    [("ೊಟ್ಟುಗು", "oTTugu")],
}


def decline_noun(lemma: str, script: str = "auto") -> DeclensionTable:
    """
    Generate the full 8-case declension paradigm for a Tulu noun.

    :param lemma:  Noun lemma (nominative form).
    :param script: 'kannada', 'latin', 'tigalari', or 'auto'.
    :returns:      DeclensionTable with all case forms.

    Example:
        >>> table = decline_noun("ಇಲ್ಲ")
        >>> table.forms[Case.DATIVE]
        [{'kannada': 'ಇಲ್ಲಗ್', 'latin': 'illag', 'tigalari': '...'}]
    """
    lemma = lemma.strip()
    if script == "auto":
        script = detect_script(lemma)
    if script == "latin":
        lemma_kn = latin_to_kannada(lemma)
    elif script == "tigalari":
        lemma_kn = tigalari_to_kannada(lemma)
    else:
        lemma_kn = lemma

    lemma_latin = kannada_to_latin(lemma_kn)
    forms: Dict[Case, List[Dict[str, str]]] = {}

    for case, suffixes in _DECLENSION_SUFFIXES.items():
        case_forms = []
        for suf_kn, suf_lat in suffixes:
            inflected_kn = lemma_kn + suf_kn
            inflected_lat = kannada_to_latin(inflected_kn)
            inflected_tg = kannada_to_tigalari(inflected_kn)
            case_forms.append({
                "kannada": inflected_kn,
                "latin": inflected_lat,
                "tigalari": inflected_tg,
            })
        forms[case] = case_forms

    return DeclensionTable(
        lemma_kannada=lemma_kn,
        lemma_latin=lemma_latin,
        forms=forms,
    )


# ═══════════════════════════════════════════════════════════════
# 10.  VERB CONJUGATION GENERATOR
# ═══════════════════════════════════════════════════════════════

# Template-based conjugation patterns for regular Tulu verbs.
# Key: pattern_type, Value: dict of slot -> (suffix_kn, suffix_lat)
# Verb types determined by stem ending:
#   Type A: C-stem (e.g. bar-, tin-, par-, pan-)   → -pu suffix class
#   Type B: V-stem (e.g. pO-, too-)               → -pu suffix class
#   Type C: Causative -pu stem (e.g. malpu-, kalpu-) → -v- infix class

_CONJUGATION_TEMPLATES: Dict[str, Dict[str, Tuple[str, str]]] = {
    # Present
    "prs.1sg":  ("್ಪೆ",   "pe"),
    "prs.3pl":  ("್ಪರ್",  "par"),
    "prs.3sg":  ("್ಪುಂಡು", "puMDu"),
    # Past
    "pst.1sg":  ("ಿಯೆ",   "iye"),
    "pst.3pl":  ("ಿಯೆರ್", "iyer"),
    "pst.3sg":  ("್ಂಡ್",  "MD"),
    # Imperative
    "imp.pol":  ("್ಲೆ",   "le"),
    # Obligative
    "obl":      ("ೊಡು",   "oDu"),
    # Infinitive
    "inf":      ("ಿಯೆರೆ", "iyere"),
    # Gerund
    "ger":      ("ನ್ನಗ",  "nnaga"),
    # Negative
    "neg":      ("ಿಜಿ",   "iji"),
}


def conjugate_verb(lemma: str, script: str = "auto") -> ConjugationTable:
    """
    Generate a conjugation paradigm table for a Tulu verb.

    :param lemma:  Verb lemma (imperative polite form, e.g. ಬಲೆ / ತಿನ್ಲೆ).
    :param script: 'kannada', 'latin', 'tigalari', or 'auto'.
    :returns:      ConjugationTable with all tense × person × number forms.

    Example:
        >>> table = conjugate_verb("ತಿನ್ಲೆ")
        >>> table.forms["prs.1sg"]
        {'kannada': 'ತಿನ್ಪೆ', 'latin': 'tinpe', 'tigalari': '...'}
    """
    lemma = lemma.strip()
    if script == "auto":
        script = detect_script(lemma)
    if script == "latin":
        lemma_kn = latin_to_kannada(lemma)
    elif script == "tigalari":
        lemma_kn = tigalari_to_kannada(lemma)
    else:
        lemma_kn = lemma

    lemma_latin = kannada_to_latin(lemma_kn)

    # Extract stem by stripping imperative suffix
    stem_kn = lemma_kn
    for suf_kn, suf_lat in VERB_IMPERATIVE_SUFFIXES:
        stripped = _strip_suffix(lemma_kn, suf_kn)
        if stripped:
            stem_kn = stripped
            break

    forms: Dict[str, Dict[str, str]] = {}
    irregular: Dict[str, Dict[str, str]] = {}

    # Check if we have known irregular forms in IRREGULAR_VERB_MAP
    # by reverse-mapping: find all conjugated entries whose lemma matches
    known_conjugated: Dict[str, str] = {}
    for conj_stem, (irr_lemma, _, _) in IRREGULAR_VERB_MAP.items():
        if irr_lemma == lemma_kn:
            known_conjugated[conj_stem] = irr_lemma

    # Generate regular forms from stem + template suffixes
    for slot, (suf_kn, suf_lat) in _CONJUGATION_TEMPLATES.items():
        inflected_kn = stem_kn + suf_kn
        inflected_lat = kannada_to_latin(inflected_kn)
        inflected_tg = kannada_to_tigalari(inflected_kn)
        forms[slot] = {
            "kannada": inflected_kn,
            "latin": inflected_lat,
            "tigalari": inflected_tg,
        }

    # Override with known irregular/suppletive forms from dataset
    try:
        try:
            from kannada_tigalari_converter.lexicon.words_dataset_1000 import WORDS_DATASET_1000
        except (ImportError, ModuleNotFoundError):
            from lexicon.words_dataset_1000 import WORDS_DATASET_1000
        for item in WORDS_DATASET_1000:
            if item["category"] == "Tulu Verb Conjugations":
                eng = item["english_meaning"].lower()
                kn = item["kannada"]
                lat = item["latin_phonetic"]
                # Check if this conjugated form derives from our lemma
                for conj_stem in known_conjugated:
                    if kn.startswith(conj_stem) or conj_stem.startswith(kn[:3]):
                        tg = kannada_to_tigalari(kn)
                        # Classify the form
                        slot = _classify_verb_form(eng)
                        if slot:
                            irregular[slot] = {
                                "kannada": kn,
                                "latin": lat,
                                "tigalari": tg,
                            }
                        break
    except ImportError:
        pass

    return ConjugationTable(
        lemma_kannada=lemma_kn,
        lemma_latin=lemma_latin,
        forms=forms,
        irregular_forms=irregular,
    )


def _classify_verb_form(english_desc: str) -> Optional[str]:
    """Classify an English verb description into a conjugation slot."""
    desc = english_desc.lower()
    if "not" in desc or "unavailable" in desc or "did not" in desc:
        return "neg"
    if "must" in desc:
        return "obl"
    if "while" in desc:
        return "ger"
    if "to " in desc and ("arrive" in desc or "come" in desc):
        return "inf"
    if "i " in desc:
        if any(w in desc for w in ["went", "came", "ate", "drank", "looked",
                                    "gave", "took", "did", "learned", "stated",
                                    "ran", "danced", "placed", "wrote",
                                    "read ", "waited", "slept"]):
            return "pst.1sg"
        return "prs.1sg"
    if "they " in desc:
        if any(w in desc for w in ["arrived", "went", "ate", "did", "stated",
                                    "slept", "looked"]):
            return "pst.3pl"
        return "prs.3pl"
    if "it " in desc:
        return "pst.3sg"
    return None


# ═══════════════════════════════════════════════════════════════
# 11.  BATCH ANALYSIS & EXPORT UTILITIES
# ═══════════════════════════════════════════════════════════════

def analyze_batch(words: Sequence[str], script: str = "auto") -> List[MorphAnalysis]:
    """Analyze a batch of words, returning a list of MorphAnalysis."""
    return [analyze(w, script=script) for w in words]


def export_analysis_to_dicts(analyses: List[MorphAnalysis]) -> List[Dict]:
    """Convert a list of MorphAnalysis to a list of plain dicts."""
    return [a.to_dict() for a in analyses]


class TuluMorphAnalyzer:
    """Class wrapper providing lemmatization, POS tagging, and morpheme parsing

    Compatible with standard microservice interfaces.
    """

    def __init__(self, default_script: str = "auto"):
        self.default_script = default_script

    def lemmatize(self, word: str, script: Optional[str] = None) -> str:
        res = analyze(word, script=script or self.default_script)
        return res.lemma_kannada if res and res.lemma_kannada else word

    def predict_pos(self, word: str, script: Optional[str] = None) -> str:
        tag = pos_tag(word, script=script or self.default_script)
        return tag.value if hasattr(tag, "value") else str(tag)

    def parse(self, word: str, script: Optional[str] = None) -> List[Dict[str, str]]:
        res = analyze(word, script=script or self.default_script)
        if not res:
            return []
        return [
            {
                "surface": m.surface,
                "latin": getattr(m, "latin", ""),
                "tag": m.tag,
                "gloss": getattr(m, "gloss", ""),
                "meaning": getattr(m, "gloss", ""),
            }
            for m in res.morphemes
        ]

    def analyze(self, word: str, script: Optional[str] = None) -> MorphAnalysis:
        return analyze(word, script=script or self.default_script)


# ═══════════════════════════════════════════════════════════════
# 12.  MODULE-LEVEL CONVENIENCE — QUICK DEMO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Quick smoke test
    test_words = [
        "ಇಲ್ಲ",      # house (base noun)
        "ಇಲ್ಲಗ್",    # to the house (dative)
        "ಇಲ್ಲಡ್",    # in the house (locative)
        "ಇಲ್ಲದ",     # of the house (genitive)
        "ಕುಡ್ಲಗ್",   # to Mangalore (dative)
        "ಬರ್ಪೆ",     # I come (present 1sg)
        "ಬರ್ಪರ್",    # they come (present 3pl)
        "ಬತ್ತ್ಂಡ್",  # it arrived (past 3sg)
        "ಬನ್ನಗ",     # while coming (gerund)
        "ಬರಿಯೆರೆ",   # to come (infinitive)
        "ಯಾನ್",      # I (pronoun)
        "ಪೋಯೆ",      # I went (past 1sg)
        "ತಿಂದೆರ್",   # they ate (past 3pl)
        "ಪಾತೆರ್ಲೆ",  # speak (imperative)
        "ತೆರಿಯಿಜಿ",  # not understood (negative)
    ]

    print("=" * 80)
    print("  Tulu Morphological Analyzer — Demo")
    print("=" * 80)
    for w in test_words:
        result = analyze(w)
        print(f"\n  {w} ({result.surface_latin})")
        print(f"    Lemma   : {result.lemma_kannada} ({result.lemma_latin})")
        print(f"    Tigalari: {result.lemma_tigalari}")
        print(f"    Tag     : {result.tag_string()}")
        print(f"    POS     : {result.pos.value}")
        if result.case:
            print(f"    Case    : {result.case.value}")
        if result.tense:
            print(f"    Tense   : {result.tense.value}")
        if result.person:
            print(f"    Person  : {result.person.value}")
        if result.is_negative:
            print(f"    Negative: True")
        if result.english_meaning:
            print(f"    Meaning : {result.english_meaning}")
        print(f"    Morphs  : {' + '.join(m.tag for m in result.morphemes)}")
