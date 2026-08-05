import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED_PATH = os.path.join(BASE_DIR, "data", "scraped", "all_languages_merged.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "pilot_dataset")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(MERGED_PATH, "r", encoding="utf-8") as f:
    all_data = json.load(f)

LANGUAGE_METADATA = {
    "mongondow": {
        "iso_639_3": "mog",
        "glottolog": "mong1342",
        "family": "Philippine (Greater Central Philippine)",
        "branch": "Gorontalo-Mongondow > Mongondowic"
    },
    "gorontalo": {
        "iso_639_3": "gor",
        "glottolog": "goro1259",
        "family": "Philippine (Greater Central Philippine)",
        "branch": "Gorontalo-Mongondow > Gorontalic"
    },
    "sangir": {
        "iso_639_3": "sxn",
        "glottolog": "nort2871",
        "family": "Philippine",
        "branch": "Sangiric"
    },
    "balantak": {
        "iso_639_3": "blz",
        "glottolog": "bala1315",
        "family": "Celebic",
        "branch": "Saluan-Banggai > Eastern"
    },
    "kaili_daa": {
        "iso_639_3": "kzf",
        "glottolog": "comm1248",
        "family": "Celebic",
        "branch": "Kaili-Pamona > Northern > Kaili"
    },
    "napu": {
        "iso_639_3": "npy",
        "glottolog": "napu1241",
        "family": "Celebic",
        "branch": "Kaili-Pamona > Southern > Badaic"
    },
    "uma": {
        "iso_639_3": "ppk",
        "glottolog": "umaa1242",
        "family": "Celebic",
        "branch": "Kaili-Pamona > Southern"
    },
    "taa": {
        "iso_639_3": None,
        "glottolog": None,
        "family": "Celebic",
        "branch": "Kaili-Pamona > Pamona"
    },
    "aralle": {
        "iso_639_3": "atq",
        "glottolog": "aral1243",
        "family": "South Sulawesi",
        "branch": "Northern > Pitu Ulunna Salu"
    },
    "bambam": {
        "iso_639_3": "ptu",
        "glottolog": "bamb1270",
        "family": "South Sulawesi",
        "branch": "Northern > Pitu Ulunna Salu"
    },
    "duri": {
        "iso_639_3": "mvp",
        "glottolog": "duri1242",
        "family": "South Sulawesi",
        "branch": "Northern > Massenrempulu"
    },
    "mamasa": {
        "iso_639_3": "mqj",
        "glottolog": "mama1276",
        "family": "South Sulawesi",
        "branch": "Northern > Toraja-Sa'dan"
    },
    "toraja": {
        "iso_639_3": "sda",
        "glottolog": "tora1261",
        "family": "South Sulawesi",
        "branch": "Northern > Toraja-Sa'dan"
    },
    "bugis": {
        "iso_639_3": "bug",
        "glottolog": "bugi1244",
        "family": "South Sulawesi",
        "branch": "Bugis-Tamanic > Bugis"
    },
    "makasar": {
        "iso_639_3": "mak",
        "glottolog": "maka1311",
        "family": "South Sulawesi",
        "branch": "Makassaric"
    },
    "kupang": {
        "iso_639_3": "mkn",
        "glottolog": "kupa1239",
        "family": "Malayic",
        "branch": "Eastern Indonesian Malay"
    },
    "sabu": {
        "iso_639_3": "hvn",
        "glottolog": "sabu1255",
        "family": "Central Malayo-Polynesian",
        "branch": "Sumba-Flores > Sumba-Hawu > Savu"
    },
    "manggarai": {
        "iso_639_3": "mqy",
        "glottolog": "mang1405",
        "family": "Central Malayo-Polynesian",
        "branch": "Sumba-Flores > Ende-Manggarai > Manggarai-Rembong"
    },
    "rote": {
        "iso_639_3": None,
        "glottolog": "rote1234",
        "family": "Central Malayo-Polynesian",
        "branch": "Timor-Babar > Rote-Meto"
    },
    "sasak": {
        "iso_639_3": "sas",
        "glottolog": "sasa1249",
        "family": "Malayo-Sumbawan",
        "branch": "Bali-Sasak-Sumbawa > Sasak-Sumbawa"
    },
    "yawa": {
        "iso_639_3": "yva",
        "glottolog": "nucl1454",
        "family": "Papuan (Yawan)",
        "branch": "Yawa-Saweru"
    },
    "meyah": {
        "iso_639_3": "mej",
        "glottolog": "meya1236",
        "family": "Papuan (West Papuan)",
        "branch": "East Bird's Head > Mantion-Meyah"
    },
    "abun": {
        "iso_639_3": "kgr",
        "glottolog": "abun1252",
        "family": "Papuan (Isolate)",
        "branch": None
    },
    "berik": {
        "iso_639_3": "bkl",
        "glottolog": "beri1254",
        "family": "Papuan (Tor-Kwerba)",
        "branch": "Tor-Kwerba (Foja Range) > Orya-Tor > Tor > Berik-Bonerif"
    },
    "yali": {
        "iso_639_3": "yli",
        "glottolog": "yali1257",
        "family": "Papuan (Trans-New Guinea)",
        "branch": "West Trans-New Guinea > Irian Highlands > Dani > Ngalik"
    },
    "Bauzi": {
        "iso_639_3": "bvz",
        "glottolog": "bauz1241",
        "family": "Papuan (East Geelvink Bay)",
        "branch": "Bauzi-Demisa"
    },
    "tabaru": {
        "iso_639_3": "tby",
        "glottolog": "taba1263",
        "family": "Papuan (North Halmahera)",
        "branch": "Galela-Tobelo"
    },
    "galela": {
        "iso_639_3": "gbi",
        "glottolog": "gale1259",
        "family": "Papuan (North Halmahera)",
        "branch": "Galela-Tobelo"
    },
}

EXCLUDE = {"ayt", "nasb"}

family_groups = {}
for lang_key, meta in LANGUAGE_METADATA.items():
    if lang_key in EXCLUDE:
        continue
    family = meta["family"]
    if family not in family_groups:
        family_groups[family] = []
    family_groups[family].append(lang_key)

for family, lang_keys in sorted(family_groups.items()):
    print(f"\n{'=' * 60}")
    print(f"Family: {family}")
    print(f"Languages: {lang_keys}")
    print(f"{'=' * 60}")

    family_output = {
        "family": family,
        "languages": {}
    }

    for lang_key in lang_keys:
        meta = LANGUAGE_METADATA[lang_key]

        if lang_key not in all_data:
            print(f"  WARNING: '{lang_key}' not found in merged data, skipping")
            continue

        lang_data = all_data[lang_key]

        family_output["languages"][lang_key] = {
            "iso_639_3": meta["iso_639_3"],
            "glottolog": meta["glottolog"],
            "branch": meta["branch"],
            "books": lang_data
        }

        book_count = len(lang_data)
        verse_count = sum(
            len(v)
            for book in lang_data
            for ch in book.get("chapters", [])
            for v in [ch.get("verses", [])]
        )
        print(f"  {lang_key}: {book_count} books, {verse_count} verses")

    safe_name = family.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
    output_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(family_output, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved: {output_path}")

print(f"\n{'=' * 60}")
print(f"Total families: {len(family_groups)}")
print(f"Total languages processed: {sum(len(v) for v in family_groups.values())}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"{'=' * 60}")
