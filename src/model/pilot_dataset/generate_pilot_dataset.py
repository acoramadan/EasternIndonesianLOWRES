import json
import os
import sys
import uuid
import re

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED_PATH = os.path.join(BASE_DIR, "data", "scraped", "all_languages_merged.json")
FAMILY_DIR = os.path.join(BASE_DIR, "data", "pilot_dataset")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pilot_dataset")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(MERGED_PATH, "r", encoding="utf-8") as f:
    all_data = json.load(f)

REFERENCE_PATTERN = re.compile(r"^\(?\d+:\d+\)?$")


def is_dirty(text):
    if not text or not isinstance(text, str):
        return True
    t = text.strip()
    if len(t) == 0:
        return True
    if REFERENCE_PATTERN.match(t):
        return True
    return False


def build_lookup(lang_data):
    lookup = {}
    for book in lang_data:
        book_id = book.get("book_id", "")
        for chapter in book.get("chapters", []):
            ch_num = chapter.get("chapter_number", 0)
            for verse in chapter.get("verses", []):
                v_num = verse.get("verse_number", 0)
                text = verse.get("text", "")
                key = f"{book_id}_{ch_num}_{v_num}"
                lookup[key] = text
    return lookup


print("Building reference lookups for ayt (ind) and nasb (eng)...")
ayt_lookup = build_lookup(all_data["ayt"])
nasb_lookup = build_lookup(all_data["nasb"])
print(f"  ayt entries: {len(ayt_lookup):,}")
print(f"  nasb entries: {len(nasb_lookup):,}")

family_files = [f for f in os.listdir(FAMILY_DIR) if f.endswith(".json")]
print(f"\nFound {len(family_files)} family files in {FAMILY_DIR}")

total_records = 0
total_skipped = 0

for family_file in sorted(family_files):
    family_path = os.path.join(FAMILY_DIR, family_file)
    with open(family_path, "r", encoding="utf-8") as f:
        family_data = json.load(f)

    family_name = family_data["family"]
    languages = family_data["languages"]

    output_name = family_file.replace(".json", ".jsonl")
    output_path = os.path.join(OUTPUT_DIR, output_name)

    print(f"\n{'=' * 60}")
    print(f"Family: {family_name}")
    print(f"Languages: {list(languages.keys())}")
    print(f"{'=' * 60}")

    records = []
    skipped = 0

    for lang_key, lang_info in languages.items():
        iso_code = lang_info.get("iso_639_3")
        source_lang_label = iso_code if iso_code else lang_key

        direction = f"{source_lang_label}_to_ind_eng"

        for book in lang_info.get("books", []):
            book_id = book.get("book_id", "")
            for chapter in book.get("chapters", []):
                ch_num = chapter.get("chapter_number", 0)
                for verse in chapter.get("verses", []):
                    v_num = verse.get("verse_number", 0)
                    source_text = verse.get("text", "")

                    if is_dirty(source_text):
                        skipped += 1
                        continue

                    alignment_key = f"{book_id}_{ch_num}_{v_num}"

                    ref_ind = ayt_lookup.get(alignment_key, "")
                    ref_eng = nasb_lookup.get(alignment_key, "")

                    if is_dirty(ref_ind) or is_dirty(ref_eng):
                        skipped += 1
                        continue

                    record = {
                        "data_id": str(uuid.uuid4()),
                        "alignment_id": alignment_key,
                        "family": family_name,
                        "translation_direction": direction,
                        "source_lang": source_lang_label,
                        "target_lang": ["ind", "eng"],
                        "source_text": source_text.strip(),
                        "reference_text_ind": ref_ind.strip(),
                        "reference_text_eng": ref_eng.strip(),
                    }
                    records.append(record)

        print(f"  {lang_key} ({source_lang_label}): {sum(1 for r in records if r['source_lang'] == source_lang_label):,} records")

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"  Skipped (dirty): {skipped:,}")
    print(f"  Total records: {len(records):,}")
    print(f"  -> Saved: {output_path}")

    total_records += len(records)
    total_skipped += skipped

print(f"\n{'=' * 60}")
print(f"PILOT DATASET GENERATION COMPLETE")
print(f"{'=' * 60}")
print(f"Total records written: {total_records:,}")
print(f"Total skipped (dirty): {total_skipped:,}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Files generated: {len(family_files)}")
