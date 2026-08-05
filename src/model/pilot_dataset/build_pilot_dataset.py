import json
import os
import sys
import uuid
import re
import glob

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_DIR = os.path.join(BASE_DIR, "data", "pilot_dataset")
MERGED_PATH = os.path.join(BASE_DIR, "data", "scraped", "all_languages_merged.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pilot_dataset")
os.makedirs(OUTPUT_DIR, exist_ok=True)

REF_PATTERN = re.compile(r"^\(?\d+:\d+\)?$")

with open(MERGED_PATH, "r", encoding="utf-8") as f:
    all_data = json.load(f)

ayt_data = all_data["ayt"]
nasb_data = all_data["nasb"]


def build_ref_lookup(lang_books):
    lookup = {}
    for book in lang_books:
        book_id = book["book_id"]
        for chapter in book.get("chapters", []):
            ch_num = chapter["chapter_number"]
            for verse in chapter.get("verses", []):
                v_num = verse["verse_number"]
                text = verse.get("text", "").strip()
                key = (book_id, ch_num, v_num)
                lookup[key] = text
    return lookup


print("Building reference lookups for ayt and nasb...")
ayt_lookup = build_ref_lookup(ayt_data)
nasb_lookup = build_ref_lookup(nasb_data)
print(f"  ayt: {len(ayt_lookup):,} verses")
print(f"  nasb: {len(nasb_lookup):,} verses")

family_files = sorted(glob.glob(os.path.join(PILOT_DIR, "*.json")))
print(f"\nFound {len(family_files)} family files in pilot_dataset/")

total_records = 0
total_skipped = 0

for family_file in family_files:
    filename = os.path.basename(family_file)
    family_stem = os.path.splitext(filename)[0]

    with open(family_file, "r", encoding="utf-8") as f:
        family_data = json.load(f)

    family_name = family_data["family"]
    languages = family_data["languages"]

    output_filename = f"pilot_dataset_{family_stem}.jsonl"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    print(f"\n{'=' * 60}")
    print(f"Family: {family_name}")
    print(f"Languages: {list(languages.keys())}")
    print(f"Output: {output_filename}")
    print(f"{'=' * 60}")

    records = []
    skipped = 0

    for lang_key, lang_info in languages.items():
        iso_code = lang_info["iso_639_3"]
        source_lang_label = iso_code if iso_code else lang_key

        books = lang_info["books"]

        for book in books:
            book_id = book["book_id"]
            for chapter in book.get("chapters", []):
                ch_num = chapter["chapter_number"]
                for verse in chapter.get("verses", []):
                    v_num = verse["verse_number"]
                    source_text = verse.get("text", "").strip()

                    if not source_text or REF_PATTERN.match(source_text):
                        skipped += 1
                        continue

                    key = (book_id, ch_num, v_num)
                    ref_ind = ayt_lookup.get(key, "")
                    ref_eng = nasb_lookup.get(key, "")

                    if not ref_ind or REF_PATTERN.match(ref_ind):
                        skipped += 1
                        continue
                    if not ref_eng or REF_PATTERN.match(ref_eng):
                        skipped += 1
                        continue

                    alignment_id = f"{book_id}_{ch_num}_{v_num}"
                    translation_direction = f"{source_lang_label}_to_ind_eng"

                    record = {
                        "data_id": str(uuid.uuid4()),
                        "alignment_id": alignment_id,
                        "family": family_name,
                        "translation_direction": translation_direction,
                        "source_lang": source_lang_label,
                        "target_lang": ["ind", "eng"],
                        "source_text": source_text,
                        "reference_text_ind": ref_ind,
                        "reference_text_eng": ref_eng
                    }
                    records.append(record)

        lang_count = sum(1 for r in records if r["source_lang"] == source_lang_label)
        print(f"  {lang_key} ({source_lang_label}): {lang_count:,} records")

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"  Total records: {len(records):,} | Skipped: {skipped:,}")
    print(f"  Saved: {output_path}")
    total_records += len(records)
    total_skipped += skipped

print(f"\n{'=' * 60}")
print(f"PILOT DATASET BUILD COMPLETE")
print(f"{'=' * 60}")
print(f"Total JSONL files: {len(family_files)}")
print(f"Total records: {total_records:,}")
print(f"Total skipped (dirty/missing): {total_skipped:,}")
print(f"Output directory: {OUTPUT_DIR}")
