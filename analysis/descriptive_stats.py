import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HOME = Path.home()
ARABIZI_WORDS = HOME / "cs496-codeswitching/data/arabizi-wanlp/words_annotated.csv"
ARABIZI_SENTS = HOME / "cs496-codeswitching/data/arabizi-wanlp/sen_annotated.csv"
ARCS_FILE     = HOME / "cs496-codeswitching/data/arabic-english-cs/AR-EN Intra-word CS Corpus.txt"
FIGS          = HOME / "cs496-codeswitching/analysis/figures"
FIGS.mkdir(exist_ok=True)

# Corrected mapping based on original authors' source code (main.py line 21):
# categ_names = ['Arabizi', 'English', 'French', 'Arabic', 'Shared', 'Other']
CATEG_MAP = {
    0: "AR-LAT",   # Arabizi (Arabic in Latin script)
    1: "EN",       # English
    2: "OL",       # French -> Other Language
    3: "AR",       # Arabic (Arabic script)
    4: "AR-LAT",   # Shared (Arabic-origin words in Latin script, e.g. Mashallah, allah)
    5: "OTHER",    # Punctuation, digits, symbols
}

COLORS = {
    "AR": "#534AB7",
    "EN": "#1D9E75",
    "AR-LAT": "#D85A30",
    "OL": "#D4537E",
    "OTHER": "#888780",
    "MIX": "#BA7517",
    "NE.AR": "#3C3489",
    "NE.EN": "#0F6E56",
    "AMBIG": "#BA7517",
    "LANG3": "#993C1D",
}

def analyze_arabizi():
    print("\n=== Arabizi Dataset (WANLP 2022) ===")
    df = pd.read_csv(ARABIZI_WORDS)
    df["label"] = df["categ"].map(CATEG_MAP)
    total_tokens = len(df)
    total_sents  = df["sen_id"].nunique()
    sources = df["source"].value_counts()
    dist    = df["label"].value_counts()
    lens    = df.groupby("sen_id").size()
    print(f"  Total tokens:      {total_tokens:,}")
    print(f"  Total sentences:   {total_sents:,}")
    print(f"  Avg tokens/sent:   {lens.mean():.1f}")
    print(f"  Max tokens/sent:   {lens.max()}")
    print(f"  Min tokens/sent:   {lens.min()}")
    print(f"\n  Source breakdown:")
    for src, count in sources.items():
        print(f"    {src:10s}: {count:6,} tokens ({100*count/total_tokens:.1f}%)")
    print(f"\n  Label distribution (after mapping):")
    for label, count in dist.items():
        print(f"    {label:10s}: {count:6,}  ({100*count/total_tokens:.1f}%)")

    # Also show original categ distribution for transparency
    orig_dist = df["categ"].value_counts().sort_index()
    orig_names = {0: "Arabizi", 1: "English", 2: "French", 3: "Arabic", 4: "Shared", 5: "Other"}
    print(f"\n  Original category distribution (before mapping):")
    for categ, count in orig_dist.items():
        name = orig_names.get(categ, f"Unknown({categ})")
        mapped = CATEG_MAP.get(categ, "???")
        print(f"    categ {categ} ({name:8s}) -> {mapped:7s}: {count:6,}  ({100*count/total_tokens:.1f}%)")

    cs_sents = df[df["label"].isin(["AR","AR-LAT"])]["sen_id"].nunique()
    print(f"\n  Code-switched sentences: {cs_sents:,} / {total_sents:,} ({100*cs_sents/total_sents:.1f}%)")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    dist.plot(kind="bar", ax=axes[0], color=[COLORS.get(l,"#888780") for l in dist.index], edgecolor="none")
    axes[0].set_title("Label distribution — Arabizi WANLP 2022", fontsize=11)
    axes[0].set_xlabel("Label"); axes[0].set_ylabel("Token count")
    axes[0].tick_params(axis="x", rotation=0)
    sources.plot(kind="bar", ax=axes[1], color=["#534AB7","#1D9E75"], edgecolor="none")
    axes[1].set_title("Source breakdown — Arabizi WANLP 2022", fontsize=11)
    axes[1].set_xlabel("Source"); axes[1].set_ylabel("Token count")
    axes[1].tick_params(axis="x", rotation=0)
    plt.tight_layout()
    plt.savefig(FIGS / "arabizi_stats.png", dpi=150)
    plt.close()
    print(f"\n  Saved: figures/arabizi_stats.png")
    return total_tokens, total_sents

def analyze_arcs():
    print("\n=== Arabic-English CS Corpus (Kaggle 2021) ===")
    tokens, labels, sent_lengths, current = [], [], [], []
    with open(ARCS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "":
                if current:
                    sent_lengths.append(len(current)); current = []
            else:
                parts = line.split()
                if len(parts) >= 2:
                    tokens.append(parts[0]); labels.append(parts[-1]); current.append(parts[0])
    if current: sent_lengths.append(len(current))
    total_tokens = len(tokens); total_sents = len(sent_lengths)

    # Map AR-EN CS labels to our unified scheme
    arcs_map = {
        "AR": "AR", "EN": "EN", "OTHER": "OTHER",
        "NE.AR": "AR", "NE.EN": "EN",
        "LANG3": "OL", "AMBIG": "OTHER",
    }
    mapped_labels = [arcs_map.get(l, l) for l in labels]
    dist_orig = pd.Series(labels).value_counts()
    dist = pd.Series(mapped_labels).value_counts()

    print(f"  Total tokens:      {total_tokens:,}")
    print(f"  Total sentences:   {total_sents:,}")
    print(f"  Avg tokens/sent:   {sum(sent_lengths)/total_sents:.1f}")
    print(f"  Max tokens/sent:   {max(sent_lengths)}")
    print(f"  Min tokens/sent:   {min(sent_lengths)}")
    print(f"\n  Original label distribution:")
    for label, count in dist_orig.items():
        print(f"    {label:10s}: {count:6,}  ({100*count/total_tokens:.1f}%)")
    print(f"\n  Mapped label distribution (unified scheme):")
    for label, count in dist.items():
        print(f"    {label:10s}: {count:6,}  ({100*count/total_tokens:.1f}%)")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    dist.plot(kind="bar", ax=axes[0], color=[COLORS.get(l,"#444441") for l in dist.index], edgecolor="none")
    axes[0].set_title("Label distribution — Arabic-English CS Corpus", fontsize=11)
    axes[0].set_xlabel("Label"); axes[0].set_ylabel("Token count")
    axes[0].tick_params(axis="x", rotation=15)
    pd.Series(sent_lengths).plot(kind="hist", ax=axes[1], bins=30, color="#534AB7", edgecolor="none")
    axes[1].set_title("Sentence length distribution", fontsize=11)
    axes[1].set_xlabel("Tokens per sentence"); axes[1].set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(FIGS / "arcs_stats.png", dpi=150)
    plt.close()
    print(f"\n  Saved: figures/arcs_stats.png")
    return total_tokens, total_sents

def combined_summary(arab_tok, arab_sen, arcs_tok, arcs_sen):
    print("\n=== Combined Dataset Summary ===")
    print(f"{'Dataset':<30} {'Sentences':>10} {'Tokens':>10}")
    print("-" * 55)
    print(f"{'Arabizi (WANLP 2022)':<30} {arab_sen:>10,} {arab_tok:>10,}")
    print(f"{'Arabic-English CS Corpus':<30} {arcs_sen:>10,} {arcs_tok:>10,}")
    print(f"{'TOTAL':<30} {arab_sen+arcs_sen:>10,} {arab_tok+arcs_tok:>10,}")
    print("\n  Observed biases:")
    print("  - Arabizi dataset is Reddit/Twitter-dominant: informal register only")
    print("  - Arabic-English CS Corpus skews heavily toward AR (62.9%) vs EN (22.5%)")
    print("  - Shared tokens (4.7%) mapped to AR-LAT may introduce boundary ambiguity")

if __name__ == "__main__":
    arab_tok, arab_sen = analyze_arabizi()
    arcs_tok, arcs_sen = analyze_arcs()
    combined_summary(arab_tok, arab_sen, arcs_tok, arcs_sen)
    print("\nDescriptive statistics complete.")
