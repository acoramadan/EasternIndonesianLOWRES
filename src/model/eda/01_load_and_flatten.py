import os
import json
import pandas as pd
import numpy as np
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "output", "pilot_dataset")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "eda")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Loading data from: {DATA_DIR}")

rows = []
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".jsonl"):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                
                parts = data.get("alignment_id", "").split("_")
                book_name = parts[0] if len(parts) > 0 else ""
                ch_num = parts[1] if len(parts) > 1 else 0
                v_num = parts[2] if len(parts) > 2 else 0
                
                source_lang = data.get("source_lang", "unknown")
                source_text = data.get("source_text", "")
                ref_ind = data.get("reference_text_ind", "")
                ref_eng = data.get("reference_text_eng", "")
                
                # Add source language
                if source_text:
                    rows.append({
                        "language": source_lang,
                        "book_name": book_name,
                        "chapter_number": ch_num,
                        "verse_number": v_num,
                        "text": source_text,
                    })
                
                # Add Indonesian
                if ref_ind:
                    rows.append({
                        "language": "ind",
                        "book_name": book_name,
                        "chapter_number": ch_num,
                        "verse_number": v_num,
                        "text": ref_ind,
                    })
                    
                # Add English
                if ref_eng:
                    rows.append({
                        "language": "eng",
                        "book_name": book_name,
                        "chapter_number": ch_num,
                        "verse_number": v_num,
                        "text": ref_eng,
                    })

df = pd.DataFrame(rows)
# Remove duplicate ind and eng entries across different source languages since they share the same alignments
df = df.drop_duplicates(subset=["language", "book_name", "chapter_number", "verse_number"])

print(f"Total verses (rows): {len(df):,}")

df["text_clean"] = df["text"].str.strip().str.replace(r"\s+", " ", regex=True)


df["char_count"] = df["text_clean"].str.len()
df["word_count"] = df["text_clean"].apply(lambda x: len(x.split()) if isinstance(x, str) and len(x) > 0 else 0)
df["avg_word_length"] = df.apply(
    lambda r: np.mean([len(w) for w in r["text_clean"].split()]) if r["word_count"] > 0 else 0,
    axis=1
)

csv_path = os.path.join(OUTPUT_DIR, "verses_flat.csv")
parquet_path = os.path.join(OUTPUT_DIR, "verses_flat.parquet")

df.to_csv(csv_path, index=False, encoding="utf-8-sig")
df.to_parquet(parquet_path, index=False)

print(f"Saved CSV   : {csv_path}")
print(f"Saved Parquet: {parquet_path}")

summary_lines = []
summary_lines.append("=" * 70)
summary_lines.append("DATASET LOAD & FLATTEN SUMMARY")
summary_lines.append("=" * 70)
summary_lines.append(f"Total languages        : {df['language'].nunique()}")
summary_lines.append(f"Total books (unique)   : {df['book_name'].nunique()}")
summary_lines.append(f"Total verses (rows)    : {len(df):,}")
summary_lines.append("")
summary_lines.append("Languages:")
for lang in sorted(df["language"].unique()):
    n_books = df[df["language"] == lang]["book_name"].nunique()
    n_verses = len(df[df["language"] == lang])
    summary_lines.append(f"  {lang:<20} | {n_books:>3} books | {n_verses:>6,} verses")
summary_lines.append("")
summary_lines.append("Columns:")
for col in df.columns:
    summary_lines.append(f"  {col:<25} {df[col].dtype}")
summary_lines.append("=" * 70)

summary_text = "\n".join(summary_lines)
print(summary_text)

summary_path = os.path.join(OUTPUT_DIR, "load_summary.txt")
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_text)
print(f"\nSaved summary: {summary_path}")

print("\nScript 01 finished. Proceed to 02_descriptive_stats.py")
