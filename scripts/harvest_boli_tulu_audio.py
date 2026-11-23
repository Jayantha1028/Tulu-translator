"""
Harvest authentic native Tulu audio recordings and transcriptions from
the BoLI Tulu Translation Showcase (LIFE / Bhasha platform).
======================================================================
Target URL: https://life.unreal-tece.co.in/showcase/boli-tulu-translation/audio-browse

This script:
1. Enumerates all 200 audio records across the showcase pagination.
2. Fetches audioView transcription metadata (Kannada script, IPA, English translation).
3. Downloads native 16kHz mono audio (.wav) files.
4. Converts Kannada text to official Unicode 16.0 Tigalari script (U+11380–U+113FF).
5. Computes canonical Roman transliteration.
6. Merges and updates datasets/subsets/real_speech_manifest.csv.
"""

import os
import sys
import io
import time
import json
import ssl
import csv
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import soundfile as sf
import numpy as np

# Set project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.kannada_tigalari import kannada_to_tigalari
from kannada_tigalari_converter.lexicon.romanization_scheme import to_canonical_roman

SHOWCASE_PAGE_URL = "https://life.unreal-tece.co.in/showcase/boli-tulu-translation/audio-browse/page"
SHOWCASE_VIEW_URL = "https://life.unreal-tece.co.in/showcase/boli-tulu-translation/audio-browse/view"
SHOWCASE_AUDIO_BASE = "https://life.unreal-tece.co.in/showcase/boli-tulu-translation/audio"

OUTPUT_DIR = os.path.join(BASE_DIR, "datasets", "subsets", "real_speech_data", "boli_tulu")
MANIFEST_PATH = os.path.join(BASE_DIR, "datasets", "subsets", "real_speech_manifest.csv")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def get_all_audio_ids(total_pages: int = 20) -> list:
    audio_ids = []
    print(f"[BoLI Harvester] Querying {total_pages} showcase pages...")
    for page in range(1, total_pages + 1):
        params = {"a": json.dumps({"pageId": page, "activeSpeakerId": "", "browseActionSelectedOption": 0})}
        full_url = f"{SHOWCASE_PAGE_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                res = json.loads(resp.read().decode())
                for row in res.get("audioData", []):
                    aid = row.get("audioId")
                    if aid and aid not in audio_ids:
                        audio_ids.append(aid)
        except Exception as e:
            print(f"  [Warning] Failed page {page}: {e}")
    print(f"[BoLI Harvester] Collected {len(audio_ids)} unique audio IDs.")
    return audio_ids


def harvest_single_record(audio_id: str) -> dict:
    """
    Fetches metadata and downloads audio for a single audio_id.
    """
    # 1. Fetch metadata
    params = {
        "a": json.dumps({
            "audioInfo": {audio_id: ""},
            "audioBrowseInfo": {"pageId": 1, "activeSpeakerId": "", "browseActionSelectedOption": 0},
            "audioViewSelectedOptions": [],
            "viewMode": "panel"
        })
    }
    view_url = f"{SHOWCASE_VIEW_URL}?{urllib.parse.urlencode(params)}"
    req_view = urllib.request.Request(view_url, headers={"User-Agent": "Mozilla/5.0"})

    kannada_text = ""
    ipa_text = ""
    english_trans = ""

    with urllib.request.urlopen(req_view, context=ctx, timeout=20) as resp:
        meta = json.loads(resp.read().decode())
        td = meta.get("transcriptionDetails", {})
        sentences = td.get("sentence", {})
        for _, s_v in sentences.items():
            tr = s_v.get("transcription", {})
            tl = s_v.get("translation", {})
            kn_part = tr.get("Kannada", "").strip()
            ipa_part = tr.get("IPA", "").strip()
            en_part = tl.get("English-Latin", "").strip()
            if kn_part:
                kannada_text = f"{kannada_text} {kn_part}".strip()
            if ipa_part:
                ipa_text = f"{ipa_text} {ipa_part}".strip()
            if en_part:
                english_trans = f"{english_trans} {en_part}".strip()

        # Fallback to audioPrompt if translation is empty
        if not english_trans:
            prompt = meta.get("audioPrompt", {}).get("content", {})
            english_trans = prompt.get("English-Latin", {}).get("text", {})
            if isinstance(english_trans, dict):
                # Flatten textspans
                spans = [v.get("textspan", {}).get("Latin", "") for v in english_trans.values() if isinstance(v, dict)]
                english_trans = " ".join(s for s in spans if s).strip()

    if not kannada_text:
        return None

    # 2. Download audio
    audio_url = f"{SHOWCASE_AUDIO_BASE}/{audio_id}"
    req_audio = urllib.request.Request(audio_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_audio, context=ctx, timeout=20) as resp:
        raw_audio_bytes = resp.read()

    # Parse and write standardized 16kHz mono WAV
    audio_data, sr = sf.read(io.BytesIO(raw_audio_bytes))
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=-1)

    duration_sec = round(len(audio_data) / sr, 2)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_filename = f"{audio_id}.wav"
    out_filepath = os.path.join(OUTPUT_DIR, out_filename)
    sf.write(out_filepath, audio_data, sr, subtype="PCM_16")

    # 3. Tigalari and Romanization
    tigalari_text = kannada_to_tigalari(kannada_text)
    latin_text = to_canonical_roman(kannada_text)

    rel_path = os.path.relpath(out_filepath, BASE_DIR)

    return {
        "audio_id": f"boli_{audio_id}",
        "audio_path": rel_path,
        "duration_sec": duration_sec,
        "tulu_kannada": kannada_text,
        "tulu_tigalari": tigalari_text,
        "tulu_latin": latin_text,
        "english_translation": english_trans,
        "source": "BoLI Tulu Translation Showcase",
    }


def main():
    audio_ids = get_all_audio_ids(total_pages=20)
    print(f"[BoLI Harvester] Processing {len(audio_ids)} records (5 parallel workers)...")

    success_records = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_id = {executor.submit(harvest_single_record, aid): aid for aid in audio_ids}
        for idx, future in enumerate(as_completed(future_to_id), 1):
            aid = future_to_id[future]
            try:
                rec = future.result()
                if rec:
                    success_records.append(rec)
                    if idx % 20 == 0 or idx == len(audio_ids):
                        print(f"  Harvested {len(success_records)}/{idx} ({aid}: '{rec['tulu_kannada'][:25]}...' -> '{rec['english_translation'][:30]}')")
            except Exception as e:
                print(f"  [Error] {aid}: {e}")

    print(f"\n[BoLI Harvester] Successfully downloaded and transcribed {len(success_records)} clips.")

    # Read existing manifest (LanguagesHome, etc.) to merge
    existing_rows = []
    if os.path.isfile(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Exclude old boli_ entries if re-running
                if not r.get("audio_id", "").startswith("boli_"):
                    existing_rows.append(r)

    print(f"[BoLI Harvester] Merging with {len(existing_rows)} existing manifest records...")
    combined_rows = existing_rows + success_records

    # Write combined manifest
    fieldnames = [
        "audio_id", "audio_path", "duration_sec", "tulu_kannada",
        "tulu_tigalari", "tulu_latin", "english_translation", "source"
    ]
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"[BoLI Harvester] Updated manifest written to: {MANIFEST_PATH}")
    print(f"  Total records in manifest: {len(combined_rows)}")


if __name__ == "__main__":
    main()
