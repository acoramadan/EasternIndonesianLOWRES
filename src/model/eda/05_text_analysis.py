import os
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "eda")
PARQUET_PATH = os.path.join(OUTPUT_DIR, "verses_flat.parquet")

WORDFREQ_DIR = os.path.join(OUTPUT_DIR, "wordfreq")
WORDCLOUD_DIR = os.path.join(OUTPUT_DIR, "wordcloud")
NGRAM_DIR = os.path.join(OUTPUT_DIR, "ngrams")

for d in [WORDFREQ_DIR, WORDCLOUD_DIR, NGRAM_DIR]:
    os.makedirs(d, exist_ok=True)

print("Loading data...")
df = pd.read_parquet(PARQUET_PATH)
df_text = df.copy()

FIG_DPI = 150
TOP_N = 50


def tokenize(text):
    if not isinstance(text, str) or len(text) == 0:
        return []
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


def get_ngrams(tokens, n=2):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


languages = sorted(df_text["language"].unique())
all_top_words = {}

print(f"\nProcessing {len(languages)} languages...")

for lang in languages:
    print(f"\n  [{lang}]")
    lang_df = df_text[df_text["language"] == lang]

    all_tokens = []
    for text in lang_df["text_clean"]:
        all_tokens.extend(tokenize(text))

    freq = Counter(all_tokens)
    top_words = freq.most_common(TOP_N)
    all_top_words[lang] = {w: c for w, c in top_words}

    freq_df = pd.DataFrame(top_words, columns=["word", "frequency"])
    freq_df["rank"] = range(1, len(freq_df) + 1)
    freq_df.to_csv(os.path.join(WORDFREQ_DIR, f"{lang}_top{TOP_N}_words.csv"), index=False)

    try:
        from wordcloud import WordCloud
        wc = WordCloud(
            width=1200, height=600,
            background_color="white",
            max_words=150,
            colormap="viridis",
            collocations=False,
            min_font_size=8
        ).generate_from_frequencies(freq)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(WORDCLOUD_DIR, f"{lang}_wordcloud.png"),
                    dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"    Wordcloud saved")
    except ImportError:
        print(f"    wordcloud library not installed, skipping wordcloud generation")

    bigrams = Counter(get_ngrams(all_tokens, 2)).most_common(TOP_N)
    trigrams = Counter(get_ngrams(all_tokens, 3)).most_common(TOP_N)

    pd.DataFrame(bigrams, columns=["bigram", "frequency"]).to_csv(
        os.path.join(NGRAM_DIR, f"{lang}_bigrams.csv"), index=False)
    pd.DataFrame(trigrams, columns=["trigram", "frequency"]).to_csv(
        os.path.join(NGRAM_DIR, f"{lang}_trigrams.csv"), index=False)
    print(f"    Words: {len(freq):,} types, {len(all_tokens):,} tokens")

print("\n[Fig 11] Zipf's law plot...")
fig, ax = plt.subplots(figsize=(12, 8))
sample_langs = sorted(languages)[:6]

for lang in sample_langs:
    lang_df = df_text[df_text["language"] == lang]
    all_tokens = []
    for text in lang_df["text_clean"]:
        all_tokens.extend(tokenize(text))
    freq = Counter(all_tokens)
    counts = sorted(freq.values(), reverse=True)
    ranks = range(1, len(counts) + 1)
    ax.loglog(ranks, counts, label=lang, alpha=0.7, linewidth=1.5)

x = np.arange(1, 10000)
ax.loglog(x, x[0] * 1.0 / x, "k--", alpha=0.3, label="Ideal Zipf (1/rank)")

ax.set_xlabel("Rank (log)")
ax.set_ylabel("Frequency (log)")
ax.legend(fontsize=8, loc="upper right")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_11_zipf_law.png"), dpi=FIG_DPI, bbox_inches="tight")
plt.close(fig)
print("  Saved: fig_11_zipf_law.png")

print("[Fig 12] Character frequency comparison...")
char_freqs = {}
for lang in languages:
    lang_df = df_text[df_text["language"] == lang]
    all_text = " ".join(lang_df["text_clean"].dropna()).lower()
    all_text = re.sub(r"[^a-z]", "", all_text)
    freq = Counter(all_text)
    total = sum(freq.values())
    char_freqs[lang] = {c: freq.get(c, 0)/total for c in "abcdefghijklmnopqrstuvwxyz"}

char_df = pd.DataFrame(char_freqs).T
char_df.columns = list("abcdefghijklmnopqrstuvwxyz")

fig, ax = plt.subplots(figsize=(18, 10))
sns.heatmap(char_df, cmap="YlOrRd", annot=False, ax=ax, linewidths=0.2)
ax.set_xlabel("Letter")
ax.set_ylabel("Language")
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_12_char_frequency.png"), dpi=FIG_DPI, bbox_inches="tight")
plt.close(fig)
print("  Saved: fig_12_char_frequency.png")

print("[Fig 13] Top shared words heatmap...")
global_freq = Counter()
for lang_words in all_top_words.values():
    global_freq.update(lang_words)
top_global = [w for w, _ in global_freq.most_common(25)]

heatmap_data = pd.DataFrame(index=languages, columns=top_global, dtype=float)
for lang in languages:
    for word in top_global:
        heatmap_data.loc[lang, word] = all_top_words.get(lang, {}).get(word, 0)

heatmap_data = heatmap_data.astype(float)

fig, ax = plt.subplots(figsize=(16, 10))
sns.heatmap(heatmap_data, cmap="Blues", annot=True, fmt=".0f", ax=ax,
            linewidths=0.3, cbar_kws={"label": "Frequency"})
ax.set_xlabel("Word")
ax.set_ylabel("Language")
plt.xticks(fontsize=9)
plt.yticks(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, "fig_13_top_words_heatmap.png"), dpi=FIG_DPI, bbox_inches="tight")
plt.close(fig)
print("  Saved: fig_13_top_words_heatmap.png")

print("\nScript 05 finished. All EDA analyses completed.")
print(f"   All output saved in: {OUTPUT_DIR}")
