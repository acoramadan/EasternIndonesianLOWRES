import os
import pandas as pd
import numpy as np
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "eda")
PARQUET_PATH = os.path.join(OUTPUT_DIR, "verses_flat.parquet")

print(f"Loading data from: {PARQUET_PATH}")
df = pd.read_parquet(PARQUET_PATH)
df_text = df.copy()
print(f"Working with {len(df_text):,} text verses")


def compute_lexical_stats(group):
    all_words = []
    for text in group["text_clean"]:
        if isinstance(text, str) and len(text) > 0:
            words = text.lower().split()
            all_words.extend(words)

    total_tokens = len(all_words)
    freq = Counter(all_words)
    vocab_size = len(freq)
    ttr = vocab_size / total_tokens if total_tokens > 0 else 0
    hapax = sum(1 for w, c in freq.items() if c == 1)
    hapax_ratio = hapax / vocab_size if vocab_size > 0 else 0

    return pd.Series({
        "total_tokens": total_tokens,
        "vocabulary_size": vocab_size,
        "type_token_ratio": round(ttr, 6),
        "hapax_legomena": hapax,
        "hapax_ratio": round(hapax_ratio, 4),
    })


print("\nComputing per-language statistics...")

stats_basic = df_text.groupby("language").agg(
    n_books=("book_name", "nunique"),
    n_chapters=("chapter_number", lambda x: len(x.groupby([df_text.loc[x.index, "book_name"], x]))),
    n_verses=("verse_number", "count"),
    char_mean=("char_count", "mean"),
    char_median=("char_count", "median"),
    char_std=("char_count", "std"),
    char_min=("char_count", "min"),
    char_max=("char_count", "max"),
    word_mean=("word_count", "mean"),
    word_median=("word_count", "median"),
    word_std=("word_count", "std"),
    word_min=("word_count", "min"),
    word_max=("word_count", "max"),
    avg_word_len_mean=("avg_word_length", "mean"),
).round(2)

chapter_counts = df_text.groupby("language").apply(
    lambda g: g.groupby(["book_name", "chapter_number"]).ngroups
)
stats_basic["n_chapters"] = chapter_counts

lexical_stats = df_text.groupby("language").apply(compute_lexical_stats, include_groups=False)

stats_per_lang = stats_basic.join(lexical_stats)
stats_per_lang = stats_per_lang.reset_index()

stats_per_lang = stats_per_lang.sort_values("language").reset_index(drop=True)

print("Computing overall statistics...")
overall = pd.DataFrame([{
    "total_languages": df_text["language"].nunique(),
    "total_unique_books": df_text["book_name"].nunique(),
    "total_verses": len(df_text),
    "char_mean": round(df_text["char_count"].mean(), 2),
    "char_median": df_text["char_count"].median(),
    "char_std": round(df_text["char_count"].std(), 2),
    "word_mean": round(df_text["word_count"].mean(), 2),
    "word_median": df_text["word_count"].median(),
    "word_std": round(df_text["word_count"].std(), 2),
    "avg_word_len_mean": round(df_text["avg_word_length"].mean(), 2),
}])

print("Computing book coverage matrix...")
coverage = df_text.groupby(["language", "book_name"]).size().unstack(fill_value=0)
coverage_binary = (coverage > 0).astype(int)

stats_per_lang.to_csv(os.path.join(OUTPUT_DIR, "stats_per_language.csv"), index=False)
overall.to_csv(os.path.join(OUTPUT_DIR, "stats_overall.csv"), index=False)
coverage.to_csv(os.path.join(OUTPUT_DIR, "book_coverage.csv"))
coverage_binary.to_csv(os.path.join(OUTPUT_DIR, "book_coverage_binary.csv"))

print(f"Saved: stats_per_language.csv")
print(f"Saved: stats_overall.csv")
print(f"Saved: book_coverage.csv")
print(f"Saved: book_coverage_binary.csv")

report = []
report.append("=" * 70)
report.append("DESCRIPTIVE STATISTICS REPORT")
report.append("=" * 70)
report.append("")
report.append("OVERALL:")
report.append(f"  Languages              : {overall['total_languages'].values[0]}")
report.append(f"  Unique books           : {overall['total_unique_books'].values[0]}")
report.append(f"  Total verses           : {overall['total_verses'].values[0]:,}")
report.append(f"  Avg chars per verse    : {overall['char_mean'].values[0]:.1f}")
report.append(f"  Avg words per verse    : {overall['word_mean'].values[0]:.1f}")
report.append(f"  Avg word length        : {overall['avg_word_len_mean'].values[0]:.2f}")
report.append("")
report.append("-" * 70)
report.append("PER-LANGUAGE SUMMARY:")
report.append("-" * 70)
for _, row in stats_per_lang.iterrows():
    report.append(f"\n  [{row['language']}]")
    report.append(f"    Books: {int(row['n_books'])} | Chapters: {int(row['n_chapters'])} | Verses: {int(row['n_verses']):,}")
    report.append(f"    Chars/verse : mean={row['char_mean']:.1f}, median={row['char_median']:.0f}, std={row['char_std']:.1f}")
    report.append(f"    Words/verse : mean={row['word_mean']:.1f}, median={row['word_median']:.0f}, std={row['word_std']:.1f}")
    report.append(f"    Vocabulary  : {int(row['vocabulary_size']):,} types / {int(row['total_tokens']):,} tokens")
    report.append(f"    TTR         : {row['type_token_ratio']:.4f}")
    report.append(f"    Hapax ratio : {row['hapax_ratio']:.4f} ({int(row['hapax_legomena']):,} words)")

report.append("")
report.append("-" * 70)
report.append("BOOK COVERAGE:")
report.append(f"  Total unique books across all languages: {coverage_binary.shape[1]}")
report.append(f"  Languages with most books : "
              + ", ".join(coverage_binary.sum(axis=1).nlargest(3).index.tolist()))
report.append(f"  Languages with fewest books: "
              + ", ".join(coverage_binary.sum(axis=1).nsmallest(3).index.tolist()))
report.append("=" * 70)

report_text = "\n".join(report)
print(report_text)

report_path = os.path.join(OUTPUT_DIR, "descriptive_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write(report_text)

print(f"\nSaved report: {report_path}")
print("\nScript 02 finished. Proceed to 03_visualizations_static.py")
