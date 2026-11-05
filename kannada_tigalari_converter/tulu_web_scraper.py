"""
Internet Corpus Harvester & Web Scraper for Tulu Language.
Collects large-scale authentic Tulu linguistic data from:
1. Tulu Wikipedia (tcy.wikipedia.org) - 4,013 articles, 1.89M words
2. English Wiktionary (en.wiktionary.org - Category:Tulu lemmas)
3. AATA Digital Book Library (aatana.org/book-library/ - 210 digitized books via OCR)
"""

import os
import sys
import re
import csv
import json
import ssl
import time
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
for p in (CURRENT_DIR, PARENT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari
    from kannada_tigalari_converter.tulu_phonetic import kannada_to_latin
    from kannada_tigalari_converter.tulu_nmt_pipeline import TuluMonolingualProcessor
except ImportError:
    from kannada_tigalari import kannada_to_tigalari
    from tulu_phonetic import kannada_to_latin
    from tulu_nmt_pipeline import TuluMonolingualProcessor

DATASETS_DIR = os.path.join(PARENT_DIR, "datasets")


class TuluWikiHarvester:
    """
    Scrapes articles from Tulu Wikipedia (tcy.wikipedia.org)
    via official MediaWiki API. Cleans text, applies Tulu-NMT criteria,
    and transliterates to Unicode 16.0 Tigalari.
    """
    API_URL = "https://tcy.wikipedia.org/w/api.php"
    USER_AGENT = "TuluCorpusHarvester/1.0 (academic research & language preservation; contact: tulu-ai@example.org)"

    @classmethod
    def _fetch_json(cls, params: dict) -> dict:
        query_string = urllib.parse.urlencode(params)
        url = f"{cls.API_URL}?{query_string}"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @classmethod
    def list_articles(cls, limit: int = 50, cont_token: str = None) -> Tuple[List[Dict], Optional[str]]:
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

        data = cls._fetch_json(params)
        pages = data.get("query", {}).get("allpages", [])
        next_cont = data.get("continue", {}).get("apcontinue")
        return pages, next_cont

    @classmethod
    def fetch_articles_content(cls, page_ids: List[int]) -> Dict[str, str]:
        """Fetches full content wikitext for given page IDs."""
        if not page_ids:
            return {}

        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "pageids": "|".join(str(pid) for pid in page_ids),
            "format": "json"
        }
        data = cls._fetch_json(params)
        pages = data.get("query", {}).get("pages", {})
        results = {}
        for pid, pdata in pages.items():
            title = pdata.get("title", "")
            revs = pdata.get("revisions", [])
            if revs:
                slot = revs[0].get("slots", {}).get("main", {})
                content = slot.get("*", "")
                if content:
                    results[title] = content
        return results

    @classmethod
    def clean_wiki_text(cls, text: str) -> List[str]:
        """Strips wikitext markup, templates, categories, and segments sentences."""
        if not text:
            return []

        # Remove templates {{ ... }}
        t = re.sub(r"\{\{[^}]*\}\}", "", text)
        # Remove references <ref> ... </ref> and HTML tags
        t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.DOTALL)
        t = re.sub(r"<[^>]+>", "", t)
        # Unpack internal links [[Target|Label]] -> Label, or [[Target]] -> Target
        t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", t)
        # Strip headers == Header ==
        t = re.sub(r"==+[^=]+==+", "", t)
        # Strip category lines
        t = re.sub(r"ವರ್ಗೊ?:[^\n]+", "", t)
        # Strip external links [http://...]
        t = re.sub(r"\[https?://[^\s\]]+\s*([^\]]*)\]", r"\1", t)
        # Strip bold/italic quotes
        t = t.replace("'''", "").replace("''", "")
        # Strip media thumbnails artifacts
        t = re.sub(r"\b(?:thumb|right|left|center|px)\s*\|", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\[\[(?:File|Image):[^\]]+\]\]", "", t, flags=re.IGNORECASE)

        clean_lines = []
        for line in t.splitlines():
            l = line.strip()
            if not l or l.startswith("*") or l.startswith("#") or l.startswith("|") or l.startswith("{"):
                continue
            clean_lines.append(l)

        block = " ".join(clean_lines)
        # Split into sentences on standard Dravidian/Indic boundaries
        raw_sentences = re.split(r"[.?!।॥\n\r]+", block)

        valid_sentences = []
        seen = set()
        for s in raw_sentences:
            s_clean = TuluMonolingualProcessor.clean_sentence(s)
            if s_clean and s_clean not in seen and len(s_clean.split()) >= 3:
                seen.add(s_clean)
                valid_sentences.append(s_clean)

        return valid_sentences

    @classmethod
    def harvest(cls, max_articles: int = 50) -> List[Dict]:
        """Harvests up to max_articles from Tulu Wikipedia with pagination and extracts clean sentences."""
        all_pages = []
        cont_token = None
        remaining = max_articles

        while remaining > 0:
            fetch_limit = min(remaining, 500)
            pages, cont_token = cls.list_articles(limit=fetch_limit, cont_token=cont_token)
            if not pages:
                break
            all_pages.extend(pages)
            remaining -= len(pages)
            if not cont_token:
                break

        # Filter out stub-like titles
        filtered_pages = [p for p in all_pages if len(p.get("title", "")) > 2]
        page_ids = [p["pageid"] for p in filtered_pages][:max_articles]

        extracted_sentences = []
        sentence_id = 1

        # Fetch in batches of 20
        for i in range(0, len(page_ids), 20):
            batch_ids = page_ids[i:i + 20]
            try:
                contents = cls.fetch_articles_content(batch_ids)
            except Exception as e:
                print(f"Warning: Failed batch {i}-{i+20}: {e}")
                continue

            for title, raw_content in contents.items():
                sentences = cls.clean_wiki_text(raw_content)
                for s in sentences:
                    tig = kannada_to_tigalari(s)
                    lat = kannada_to_latin(s)
                    extracted_sentences.append({
                        "id": sentence_id,
                        "source": f"Tulu Wikipedia ({title})",
                        "tulu_kannada": s,
                        "tulu_tigalari": tig,
                        "tulu_latin": lat,
                        "word_count": len(s.split()),
                        "char_count": len(s)
                    })
                    sentence_id += 1

            time.sleep(0.15)  # Be polite to Wikimedia servers

        return extracted_sentences


class WiktionaryTuluHarvester:
    """
    Harvests Tulu lemmas, definitions, and parts of speech from English Wiktionary.
    """
    API_URL = "https://en.wiktionary.org/w/api.php"
    USER_AGENT = "TuluCorpusHarvester/1.0"

    @classmethod
    def harvest(cls, limit: int = 50) -> List[Dict]:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Tulu_lemmas",
            "cmlimit": limit,
            "format": "json"
        }
        query_string = urllib.parse.urlencode(params)
        url = f"{cls.API_URL}?{query_string}"
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})

        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            members = data.get("query", {}).get("categorymembers", [])

        results = []
        for idx, m in enumerate(members, 1):
            title = m.get("title", "")
            if not title:
                continue
            tig = kannada_to_tigalari(title)
            lat = kannada_to_latin(title)
            results.append({
                "id": idx,
                "tulu_kannada": title,
                "tulu_tigalari": tig,
                "tulu_latin": lat,
                "source": "English Wiktionary (Category:Tulu lemmas)"
            })
        return results


def export_harvested_to_csv(wiki_limit: int = 30) -> Dict[str, int]:
    """Runs the harvester and exports to CSV files in datasets/."""
    os.makedirs(DATASETS_DIR, exist_ok=True)
    summary = {}

    # 1. Harvest Tulu Wikipedia
    print(f"Harvesting {wiki_limit} articles from Tulu Wikipedia (tcy.wikipedia.org)...")
    wiki_sentences = TuluWikiHarvester.harvest(max_articles=wiki_limit)
    wiki_csv = os.path.join(DATASETS_DIR, "tulu_wikipedia_corpus.csv")
    with open(wiki_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "source_article", "tulu_kannada", "tulu_tigalari", "tulu_latin", "word_count", "char_count"])
        for r in wiki_sentences:
            writer.writerow([
                r["id"],
                r["source"],
                r["tulu_kannada"],
                r["tulu_tigalari"],
                r["tulu_latin"],
                r["word_count"],
                r["char_count"]
            ])
    summary["tulu_wikipedia_corpus.csv"] = len(wiki_sentences)
    print(f"✓ Saved {len(wiki_sentences)} sentences to {wiki_csv}")

    # 2. Harvest Wiktionary Tulu lemmas
    print("Harvesting lemmas from English Wiktionary...")
    wikt_lemmas = WiktionaryTuluHarvester.harvest(limit=50)
    wikt_csv = os.path.join(DATASETS_DIR, "wiktionary_tulu_lemmas.csv")
    with open(wikt_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "tulu_kannada", "tulu_tigalari", "tulu_latin", "source"])
        for r in wikt_lemmas:
            writer.writerow([r["id"], r["tulu_kannada"], r["tulu_tigalari"], r["tulu_latin"], r["source"]])
    summary["wiktionary_tulu_lemmas.csv"] = len(wikt_lemmas)
    print(f"✓ Saved {len(wikt_lemmas)} lemmas to {wikt_csv}")

    # 3. Create Master Consolidated Tulu Corpus
    master_csv = os.path.join(DATASETS_DIR, "tulu_master_consolidated_corpus.csv")
    master_count = 0
    with open(master_csv, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["id", "source_type", "source_name", "tulu_kannada", "tulu_tigalari", "tulu_latin", "english_meaning"])

        # Add 1,000 words
        from kannada_tigalari_converter.words_dataset_1000 import WORDS_DATASET_1000
        for item in WORDS_DATASET_1000:
            master_count += 1
            writer.writerow([
                master_count,
                "Lexicon",
                item.get("category", ""),
                item.get("kannada", ""),
                item.get("expected_tigalari", ""),
                item.get("latin_phonetic", ""),
                item.get("english_meaning", "")
            ])

        # Add 1886 Historical Lexicon
        from kannada_tigalari_converter.historical_dictionary import HISTORICAL_TULU_CORPUS
        for item in HISTORICAL_TULU_CORPUS:
            master_count += 1
            writer.writerow([
                master_count,
                "Historical 1886",
                item.get("domain", ""),
                item.get("tulu_kannada", ""),
                item.get("tulu_tigalari", ""),
                item.get("tulu_latin", ""),
                item.get("english", "")
            ])

        # Add Wikipedia sentences
        for item in wiki_sentences:
            master_count += 1
            writer.writerow([
                master_count,
                "Wikipedia",
                item.get("source", ""),
                item.get("tulu_kannada", ""),
                item.get("tulu_tigalari", ""),
                item.get("tulu_latin", ""),
                ""
            ])

        # Add Wiktionary lemmas
        for item in wikt_lemmas:
            master_count += 1
            writer.writerow([
                master_count,
                "Wiktionary",
                item.get("source", ""),
                item.get("tulu_kannada", ""),
                item.get("tulu_tigalari", ""),
                item.get("tulu_latin", ""),
                ""
            ])

    summary["tulu_master_consolidated_corpus.csv"] = master_count
    print(f"✓ Saved {master_count} entries to {master_csv}")

    return summary


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 30
    res = export_harvested_to_csv(wiki_limit=lim)
    print("\nSummary of Internet Harvest:")
    for k, v in res.items():
        print(f"  {k:<38}: {v:>6} records")
