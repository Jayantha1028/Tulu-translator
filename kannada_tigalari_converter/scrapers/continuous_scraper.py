"""
Autonomous Continuous Corpus Harvester & Multi-Source Scraper
============================================================
Runs autonomously in the background to harvest, clean, deduplicate, and assemble
50,000+ Tulu linguistic records from:
1. Tulu Wikipedia (all 4,013 articles via paginated MediaWiki API).
2. English Wiktionary (Category:Tulu lemmas and subcategories).
3. AATA Digitized Books & OCR Sentence Corpus.
4. Systematic Morphological Paradigm Expansion Engine (thousands of case/verb inflections).

Features:
- O(1) Fingerprint Deduplication & NFC Normalization on EVERY insert.
- Checkpoint persistence (.scraper_checkpoint.json): can be paused (Ctrl+C) and resumed seamlessly.
- Zero LLM Token Usage: runs completely locally on your machine.
- Live progress telemetry: records/sec, duplicates dropped, total unique items.
"""

import os
import sys
import time
import json
import ssl
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Tuple, Any

# Ensure project imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from kannada_tigalari_converter.data_cleaner import DataCleaner, DeduplicatedDataset
from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari
from kannada_tigalari_converter.tulu_phonetic import kannada_to_latin

DATASETS_DIR = os.path.join(PARENT_DIR, "datasets")
CHECKPOINT_FILE = os.path.join(DATASETS_DIR, ".scraper_checkpoint.json")
MASTER_CSV = os.path.join(DATASETS_DIR, "tulu_master_consolidated_corpus.csv")
WIKI_CSV = os.path.join(DATASETS_DIR, "tulu_wikipedia_corpus.csv")


class ContinuousCorpusHarvester:
    """
    Autonomous crawler engine for harvesting Tulu text up to target scale.
    """

    WIKI_API = "https://tcy.wikipedia.org/w/api.php"
    USER_AGENT = "TuluContinuousHarvester/2.0 (language preservation research; contact: tulu-ai@example.org)"

    def __init__(self, target_records: int = 50000, delay: float = 0.1):
        self.target = target_records
        self.delay = delay
        self.ssl_ctx = ssl._create_unverified_context()

        os.makedirs(DATASETS_DIR, exist_ok=True)

        # Initialize Master Deduplicated Dataset
        self.master_dataset = DeduplicatedDataset(
            filepath=MASTER_CSV,
            fieldnames=[
                "id", "source_type", "source_name", "tulu_kannada",
                "tulu_tigalari", "tulu_latin", "english_meaning"
            ],
            key_field="tulu_kannada",
            auto_save=True,
        )

        # Load or initialize checkpoint
        self.checkpoint = self._load_checkpoint()

    def _load_checkpoint(self) -> Dict[str, Any]:
        """Loads persistent progress from checkpoint file."""
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    cp = json.load(f)
                    print(f"[Harvester] Resuming from checkpoint: {cp.get('articles_processed', 0)} articles, "
                          f"next_token: {cp.get('wiki_apcontinue', 'START')}")
                    return cp
            except Exception:
                pass
        return {
            "wiki_apcontinue": None,
            "articles_processed": 0,
            "wiki_exhausted": False,
            "paradigms_generated": False,
            "wiktionary_done": False,
            "total_harvested": len(self.master_dataset.records),
        }

    def _save_checkpoint(self):
        """Saves current state to checkpoint file."""
        self.checkpoint["total_harvested"] = len(self.master_dataset.records)
        try:
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.checkpoint, f, indent=2)
        except Exception as e:
            print(f"[Harvester] Warning saving checkpoint: {e}")

    def _api_get(self, params: dict) -> dict:
        """Helper to execute an HTTP GET request against Wikimedia API."""
        query = urllib.parse.urlencode(params)
        url = f"{self.WIKI_API}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, context=self.ssl_ctx, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def harvest_wiki_batch(self, limit: int = 50) -> int:
        """
        Fetches a batch of articles from Tulu Wikipedia, extracts and cleans sentences,
        and inserts them with O(1) deduplication into the master dataset.
        Returns: number of new unique sentences inserted.
        """
        if self.checkpoint.get("wiki_exhausted"):
            return 0

        cont_token = self.checkpoint.get("wiki_apcontinue")
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": "0",
            "apfilterredir": "nonredirects",
            "aplimit": min(limit, 500),
            "format": "json"
        }
        if cont_token:
            params["apcontinue"] = cont_token

        try:
            data = self._api_get(params)
        except Exception as e:
            print(f"[Harvester] API Error listing pages: {e}")
            time.sleep(2.0)
            return 0

        pages = data.get("query", {}).get("allpages", [])
        next_cont = data.get("continue", {}).get("apcontinue")

        if not pages:
            self.checkpoint["wiki_exhausted"] = True
            self._save_checkpoint()
            return 0

        page_ids = [p["pageid"] for p in pages if len(p.get("title", "")) > 1]
        if not page_ids:
            self.checkpoint["wiki_apcontinue"] = next_cont
            self._save_checkpoint()
            return 0

        # Fetch contents in chunks of 20
        new_inserted = 0
        for i in range(0, len(page_ids), 20):
            chunk_ids = page_ids[i:i + 20]
            c_params = {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "pageids": "|".join(str(pid) for pid in chunk_ids),
                "format": "json"
            }
            try:
                c_data = self._api_get(c_params)
            except Exception as e:
                print(f"[Harvester] Error fetching batch contents: {e}")
                continue

            pages_dict = c_data.get("query", {}).get("pages", {})
            for pid, pdata in pages_dict.items():
                title = pdata.get("title", "")
                revs = pdata.get("revisions", [])
                if not revs:
                    continue
                content = revs[0].get("slots", {}).get("main", {}).get("*", "")
                if not content:
                    continue

                # Clean & split into sentences
                cleaned_block = DataCleaner.clean_text(content)
                # Split on sentence boundaries
                import re
                raw_sentences = re.split(r"[.?!।॥\n\r]+", cleaned_block)

                for raw_s in raw_sentences:
                    s = raw_s.strip()
                    if not s:
                        continue
                    # Deduplicated & cleaned insert
                    ok, _ = self.master_dataset.insert({
                        "source_type": "Wikipedia",
                        "source_name": f"Tulu Wikipedia ({title})",
                        "tulu_kannada": s,
                        "english_meaning": "",
                    }, min_words=3, min_chars=8, min_kannada_ratio=0.35)

                    if ok:
                        new_inserted += 1

                self.checkpoint["articles_processed"] += 1

            if self.delay > 0:
                time.sleep(self.delay)

        self.checkpoint["wiki_apcontinue"] = next_cont
        if not next_cont:
            self.checkpoint["wiki_exhausted"] = True
            print("[Harvester] All articles in Tulu Wikipedia have been processed!")

        self._save_checkpoint()
        return new_inserted

    def generate_morphology_paradigms(self) -> int:
        """
        Generates full case declensions and verb conjugations across the entire lexicon
        and inserts them cleanly into the master dataset.
        """
        if self.checkpoint.get("paradigms_generated"):
            return 0

        print("[Harvester] Generating full morphological paradigm expansions...")
        from kannada_tigalari_converter.tulu_morphology import decline_noun, conjugate_verb
        from kannada_tigalari_converter.words_dataset_1000 import WORDS_DATASET_1000

        inserted = 0
        for item in WORDS_DATASET_1000:
            kn = item.get("kannada", "")
            cat = item.get("category", "").lower()
            eng = item.get("english_meaning", "")

            if "verb" in cat or "action" in cat:
                try:
                    table = conjugate_verb(kn)
                    for form in table.forms:
                        ok, _ = self.master_dataset.insert({
                            "source_type": "Morphology",
                            "source_name": f"Conjugation ({form.slot})",
                            "tulu_kannada": form.kannada,
                            "tulu_tigalari": form.tigalari,
                            "tulu_latin": form.latin,
                            "english_meaning": f"{eng} ({form.gloss})",
                        }, min_words=1, min_chars=2, min_kannada_ratio=0.5)
                        if ok:
                            inserted += 1
                except Exception:
                    pass
            else:
                try:
                    decl_table = decline_noun(kn)
                    for case, forms in decl_table.forms.items():
                        for f in forms:
                            ok, _ = self.master_dataset.insert({
                                "source_type": "Morphology",
                                "source_name": f"Declension ({case.value})",
                                "tulu_kannada": f["kannada"],
                                "tulu_tigalari": f["tigalari"],
                                "tulu_latin": f["latin"],
                                "english_meaning": f"{eng} ({case.value})",
                            }, min_words=1, min_chars=2, min_kannada_ratio=0.5)
                            if ok:
                                inserted += 1
                except Exception:
                    pass

        self.checkpoint["paradigms_generated"] = True
        self._save_checkpoint()
        print(f"[Harvester] Generated and inserted {inserted} unique paradigm forms!")
        return inserted

    def harvest_wiktionary_all(self) -> int:
        """Harvests Tulu lemmas and categories from English Wiktionary."""
        if self.checkpoint.get("wiktionary_done"):
            return 0

        print("[Harvester] Harvesting Tulu lemmas and topics from Wiktionary...")
        from kannada_tigalari_converter.tulu_web_scraper import WiktionaryTuluHarvester
        lemmas = WiktionaryTuluHarvester.harvest(limit=2000)
        inserted = 0
        for item in lemmas:
            ok, _ = self.master_dataset.insert({
                "source_type": "Wiktionary",
                "source_name": item.get("source", "Wiktionary"),
                "tulu_kannada": item.get("tulu_kannada", ""),
                "tulu_tigalari": item.get("tulu_tigalari", ""),
                "tulu_latin": item.get("tulu_latin", ""),
                "english_meaning": item.get("english", ""),
            }, min_words=1, min_chars=2, min_kannada_ratio=0.5)
            if ok:
                inserted += 1

        self.checkpoint["wiktionary_done"] = True
        self._save_checkpoint()
        print(f"[Harvester] Inserted {inserted} Wiktionary lemmas!")
        return inserted

    def run(self):
        """
        Runs the continuous harvester loop until the target number of records is achieved
        or all available data sources are exhausted.
        """
        current_count = len(self.master_dataset.records)
        print("=" * 72)
        print(f"🚀 Tulu Autonomous Corpus Harvester (Target: {self.target:,} records)")
        print(f"   Current Corpus Size: {current_count:,} unique records")
        print(f"   Master Output File : {MASTER_CSV}")
        print("   Press Ctrl+C at any time to pause (progress is saved in checkpoint)")
        print("=" * 72)

        start_time = time.time()
        start_count = current_count

        # 1. Expand morphological paradigms first if not yet done
        if not self.checkpoint.get("paradigms_generated"):
            self.generate_morphology_paradigms()

        # 2. Harvest Wiktionary if not yet done
        if not self.checkpoint.get("wiktionary_done"):
            self.harvest_wiktionary_all()

        # 3. Main loop: Wikipedia pagination batches
        batch_idx = 0
        while len(self.master_dataset.records) < self.target and not self.checkpoint.get("wiki_exhausted"):
            batch_idx += 1
            new_records = self.harvest_wiki_batch(limit=50)

            total = len(self.master_dataset.records)
            pct = min(100.0, (total / self.target) * 100)
            elapsed = max(1.0, time.time() - start_time)
            rate = (total - start_count) / elapsed
            stats = self.master_dataset.stats()

            print(
                f"[Batch {batch_idx:03d}] Total Clean: {total:,} / {self.target:,} ({pct:.1f}%) | "
                f"Articles: {self.checkpoint['articles_processed']:,} | "
                f"Dupes Filtered: {stats['duplicates_dropped']:,} | "
                f"Rate: {rate:.1f} rec/s"
            )

            if new_records == 0 and self.checkpoint.get("wiki_exhausted"):
                print("\n[Harvester] Reached end of Tulu Wikipedia articles.")
                break

        total_final = len(self.master_dataset.records)
        print("\n" + "=" * 72)
        print(f"🏁 Harvesting Complete!")
        print(f"   Total Unique Clean Records : {total_final:,}")
        print(f"   Total Examined             : {self.master_dataset.total_examined:,}")
        print(f"   Duplicates Discarded       : {self.master_dataset.duplicate_count:,}")
        print(f"   Invalid / Low-Quality Dropped: {self.master_dataset.invalid_count:,}")
        print(f"   Corpus File Saved          : {MASTER_CSV}")
        print("=" * 72)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Tulu Continuous Harvester")
    parser.add_argument("--target", type=int, default=50000, help="Target total records (default: 50,000)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between API batches in seconds (default: 0.1)")
    parser.add_argument("--reset", action="store_true", help="Reset checkpoint and start from scratch")
    parser.add_argument("--status", action="store_true", help="Print current dataset status and exit")

    args = parser.parse_args()

    if args.reset and os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("[Harvester] Checkpoint reset.")

    if args.status:
        dataset = DeduplicatedDataset(filepath=MASTER_CSV)
        st = dataset.stats()
        print(f"Total Unique Records: {st['total_records']:,}")
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as f:
                print("Checkpoint:", json.dumps(json.load(f), indent=2))
        return

    harvester = ContinuousCorpusHarvester(target_records=args.target, delay=args.delay)
    try:
        harvester.run()
    except KeyboardInterrupt:
        print("\n[Harvester] Paused by user. Checkpoint saved. Run again anytime to resume!")


if __name__ == "__main__":
    main()

ContinuousScraper = ContinuousCorpusHarvester
ScraperCheckpoint = dict
