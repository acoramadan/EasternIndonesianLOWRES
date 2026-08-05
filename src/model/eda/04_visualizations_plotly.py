import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


def save_html(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.write_html(path, include_plotlyjs="cdn")
    print(f"  Saved: {name}")


print("\n[Plotly 01] Verses per language...")
stats_sorted = stats.sort_values("n_verses", ascending=True)
fig = px.bar(
    stats_sorted, x="n_verses", y="language", orientation="h",
    color="n_verses", color_continuous_scale="Viridis",
    labels={"n_verses": "Number of Verses", "language": "Language"},
    hover_data=["n_books", "n_chapters", "vocabulary_size"]
)
fig.update_layout(height=700, template="plotly_white", title=None)
save_html(fig, "plotly_01_verses_per_language.html")

print("[Plotly 02] Word count distribution per language...")
lang_order = stats.sort_values("word_mean", ascending=False)["language"].tolist()
fig = px.box(
    df_text, x="language", y="word_count",
    category_orders={"language": lang_order},
    color="language",
    labels={"word_count": "Word Count per Verse", "language": "Language"},
)
fig.update_layout(height=600, showlegend=False, template="plotly_white", title=None)
fig.update_xaxes(tickangle=45)
save_html(fig, "plotly_02_word_dist_per_language.html")

print("[Plotly 03] Vocabulary scatter...")
fig = px.scatter(
    stats, x="total_tokens", y="vocabulary_size",
    color="type_token_ratio", size="n_verses",
    text="language",
    color_continuous_scale="RdYlBu_r",
    labels={
        "total_tokens": "Total Tokens",
        "vocabulary_size": "Vocabulary Size",
        "type_token_ratio": "TTR",
        "n_verses": "Number of Verses"
    },
)
fig.update_traces(textposition="top center", textfont_size=9)
fig.update_layout(height=650, template="plotly_white", title=None)
save_html(fig, "plotly_03_vocab_scatter.html")

print("[Plotly 04] TTR vs Hapax bubble...")
fig = px.scatter(
    stats, x="type_token_ratio", y="hapax_ratio",
    size="vocabulary_size", color="n_books",
    text="language",
    color_continuous_scale="Plasma",
    labels={
        "type_token_ratio": "Type-Token Ratio (TTR)",
        "hapax_ratio": "Hapax Legomena Ratio",
        "vocabulary_size": "Vocabulary Size",
        "n_books": "Number of Books"
    },
)
fig.update_traces(textposition="top center", textfont_size=8)
fig.update_layout(height=650, template="plotly_white", title=None)
save_html(fig, "plotly_04_ttr_hapax_bubble.html")

print("[Plotly 05] Book coverage heatmap...")
fig = px.imshow(
    coverage,
    labels=dict(x="Book", y="Language", color="Coverage"),
    color_continuous_scale="YlGnBu",
    aspect="auto"
)
fig.update_layout(height=700, width=1400, template="plotly_white", title=None)
fig.update_xaxes(tickangle=90, tickfont_size=7)
save_html(fig, "plotly_05_book_coverage_heatmap.html")

print("[Plotly 06] Sunburst structure (sampled)...")
sample_langs = stats.nlargest(5, "n_verses")["language"].tolist()
df_sample = df_text[df_text["language"].isin(sample_langs)].copy()

sunburst_data = df_sample.groupby(["language", "book_name"]).agg(
    n_verses=("verse_number", "count"),
    total_words=("word_count", "sum")
).reset_index()

fig = px.sunburst(
    sunburst_data,
    path=["language", "book_name"],
    values="n_verses",
    color="total_words",
    color_continuous_scale="Viridis",
    labels={"n_verses": "Number of Verses", "total_words": "Total Words"}
)
fig.update_layout(height=700, template="plotly_white", title=None)
save_html(fig, "plotly_06_sunburst_structure.html")

print("[Plotly 07] Parallel coordinates...")
norm_cols = ["n_books", "n_verses", "word_mean", "char_mean", "vocabulary_size", "type_token_ratio", "hapax_ratio", "avg_word_len_mean"]
stats_norm = stats.copy()
for col in norm_cols:
    mn, mx = stats_norm[col].min(), stats_norm[col].max()
    if mx > mn:
        stats_norm[col + "_n"] = (stats_norm[col] - mn) / (mx - mn)
    else:
        stats_norm[col + "_n"] = 0

dims = []
for col in norm_cols:
    dims.append(dict(
        range=[0, 1],
        label=col.replace("_", " ").title(),
        values=stats_norm[col + "_n"]
    ))

fig = go.Figure(data=go.Parcoords(
    line=dict(
        color=stats_norm["n_verses"],
        colorscale="Viridis",
        showscale=True,
        cmin=stats_norm["n_verses"].min(),
        cmax=stats_norm["n_verses"].max(),
        colorbar=dict(title="Verses")
    ),
    dimensions=dims,
    labelside="top"
))
fig.update_layout(height=600, template="plotly_white", title=None)
save_html(fig, "plotly_07_parallel_coordinates.html")

print("\nScript 04 finished. Proceed to 05_text_analysis.py")
