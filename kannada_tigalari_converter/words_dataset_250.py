"""
250 Canonical Tulu & Kannada Words Dataset for Unit Testing & Validation.
Covers 10 diverse categories (25 words each):
  1. Greetings, Courtesies & Pleasantries (1-25)
  2. Kinship, Family & Pronouns (26-50)
  3. Food, Dining, Drinks & Grains (51-75)
  4. Nature, Elements, Flora & Geography (76-100)
  5. Animals, Birds, Aquatic Life & Insects (101-125)
  6. Human Anatomy, Health & Senses (126-150)
  7. Household Objects, Tools & Town (151-175)
  8. Time, Calendar, Days & Numbers (176-200)
  9. Everyday Verbs, Commands & Actions (201-225)
  10. Adjectives, Tulu 'ae' Nuances & Complex Ottakshara Conjuncts (226-250)

Derived as the canonical base vocabulary subset from WORDS_DATASET_1000.
"""

from typing import Dict, List
from .words_dataset_1000 import WORDS_DATASET_1000, RAW_WORDS_1000

# Canonical 250 words extracted from the master 1,000 words dataset without redundant execution
RAW_WORDS = RAW_WORDS_1000[:250]
WORDS_DATASET_250: List[Dict[str, any]] = WORDS_DATASET_1000[:250]
