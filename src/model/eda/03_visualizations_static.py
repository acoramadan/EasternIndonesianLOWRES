import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "eda")
PARQUET_PATH = os.path.join(OUTPUT_DIR, "verses_flat.parquet")
STATS_PATH = os.path.join(OUTPUT_DIR, "stats_per_language.csv")
COVERAGE_PATH = os.path.join(OUTPUT_DIR, "book_coverage_binary.csv")

print("Loading data...")
df = pd.read_parquet(PARQUET_PATH)
df_text = df.copy()
stats = pd.read_csv(STATS_PATH)
coverage = pd.read_csv(COVERAGE_PATH, index_col=0)

sns.set_theme(style="whitegrid", font_scale=1.1)
PALETTE = "viridis"
FIG_DPI = 150


def save_fig(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Saved: {name}")


print("\n[Fig 01] Verses per language...")
fig, ax = plt.subplots(figsize=(14, 8))
order = stats.sort_values("n_verses", ascending=True)
colors = sns.color_palette(PALETTE, len(order))
ax.barh(order["language"], order["n_verses"], color=colors)
ax.set_xlabel("Number of Verses")
ax.set_ylabel("Language")
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
for i, (v, lang) in enumerate(zip(order["n_verses"], order["language"])):
    ax.text(v + 50, i, f"{int(v):,}", va="center", fontsize=8)
fig.tight_layout()
save_fig(fig, "fig_01_verses_per_language.png")

print("[Fig 02] Word count distribution...")
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df_text["word_count"], bins=80, color="#4C72B0", edgecolor="white", alpha=0.85)
ax.axvline(df_text["word_count"].mean(), color="red", linestyle="--", label=f"Mean = {df_text['word_count'].mean():.1f}")
ax.axvline(df_text["word_count"].median(), color="orange", linestyle="--", label=f"Median = {df_text['word_count'].median():.0f}")
ax.set_xlabel("Word Count per Verse")
ax.set_ylabel("Frequency")
ax.legend()
fig.tight_layout()
save_fig(fig, "fig_02_word_count_distribution.png")

print("[Fig 03] Boxplot char count per language...")
lang_order = stats.sort_values("char_mean", ascending=False)["language"].tolist()
fig, ax = plt.subplots(figsize=(16, 8))
sns.boxplot(data=df_text, x="language", y="char_count", order=lang_order, palette=PALETTE, fliersize=1.5, ax=ax)
ax.set_xlabel("Language")
ax.set_ylabel("Character Count per Verse")
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
save_fig(fig, "fig_03_char_count_boxplot.png")

print("[Fig 04] Boxplot word count per language...")
lang_order_w = stats.sort_values("word_mean", ascending=False)["language"].tolist()
fig, ax = plt.subplots(figsize=(16, 8))
sns.boxplot(data=df_text, x="language", y="word_count", order=lang_order_w, palette="magma", fliersize=1.5, ax=ax)
ax.set_xlabel("Language")
ax.set_ylabel("Word Count per Verse")
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
save_fig(fig, "fig_04_word_count_boxplot.png")

print("[Fig 05] Vocabulary vs tokens scatter...")
fig, ax = plt.subplots(figsize=(10, 8))
scatter = ax.scatter(stats["total_tokens"], stats["vocabulary_size"], c=stats["type_token_ratio"], cmap="coolwarm", s=120, edgecolors="black", linewidth=0.5)
for _, row in stats.iterrows():
    ax.annotate(row["language"], (row["total_tokens"], row["vocabulary_size"]), fontsize=7, ha="left", va="bottom", xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("Total Tokens")
ax.set_ylabel("Vocabulary Size (Types)")
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Type-Token Ratio (TTR)")
fig.tight_layout()
save_fig(fig, "fig_05_vocabulary_vs_tokens.png")

print("[Fig 06] TTR per language...")
ttr_order = stats.sort_values("type_token_ratio", ascending=True)
fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("coolwarm", len(ttr_order))
ax.barh(ttr_order["language"], ttr_order["type_token_ratio"], color=colors)
ax.set_xlabel("Type-Token Ratio (TTR)")
ax.set_ylabel("Language")
ax.axvline(ttr_order["type_token_ratio"].mean(), color="red", linestyle="--", alpha=0.7, label=f"Mean TTR = {ttr_order['type_token_ratio'].mean():.4f}")
ax.legend()
fig.tight_layout()
save_fig(fig, "fig_06_ttr_per_language.png")

print("[Fig 07] Avg word length per language...")
awl_order = stats.sort_values("avg_word_len_mean", ascending=True)
fig, ax = plt.subplots(figsize=(14, 8))
colors = sns.color_palette("crest", len(awl_order))
ax.barh(awl_order["language"], awl_order["avg_word_len_mean"], color=colors)
ax.set_xlabel("Average Word Length (Characters)")
ax.set_ylabel("Language")
fig.tight_layout()
save_fig(fig, "fig_07_avg_word_length.png")

print("[Fig 08] Book coverage heatmap...")
fig, ax = plt.subplots(figsize=(24, 10))
sns.heatmap(coverage, cmap="YlGnBu", cbar_kws={"label": "Available (1) / Not (0)"}, linewidths=0.3, linecolor="white", ax=ax)
ax.set_xlabel("Book")
ax.set_ylabel("Language")
plt.xticks(rotation=90, fontsize=6)
plt.yticks(fontsize=8)
fig.tight_layout()
save_fig(fig, "fig_08_book_coverage_heatmap.png")

print("[Fig 09] Violin plot word count (top 10)...")
top10 = stats.nlargest(10, "n_verses")["language"].tolist()
df_top10 = df_text[df_text["language"].isin(top10)]
fig, ax = plt.subplots(figsize=(14, 7))
sns.violinplot(data=df_top10, x="language", y="word_count", order=top10, palette="Set2", inner="box", ax=ax)
ax.set_xlabel("Language")
ax.set_ylabel("Word Count per Verse")
plt.xticks(rotation=30, ha="right")
fig.tight_layout()
save_fig(fig, "fig_09_word_count_violin.png")

print("[Fig 10] Correlation heatmap...")
corr_cols = ["n_books", "n_chapters", "n_verses", "char_mean", "word_mean", "avg_word_len_mean", "vocabulary_size", "total_tokens", "type_token_ratio", "hapax_ratio"]
corr = stats[corr_cols].corr()
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, square=True, linewidths=0.5, ax=ax)
ax.set_xlabel("Metric")
ax.set_ylabel("Metric")
fig.tight_layout()
save_fig(fig, "fig_10_correlation_heatmap.png")

print("\nScript 03 finished. Proceed to 04_visualizations_plotly.py")
