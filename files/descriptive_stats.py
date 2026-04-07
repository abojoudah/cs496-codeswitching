"""
Descriptive statistics for both datasets.
Run after downloading datasets with the download scripts.

Usage:
    python descriptive_stats.py

Outputs:
    - Console summary table
    - figures/class_distribution.png
    - figures/sentence_length_dist.png
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

os.makedirs("figures", exist_ok=True)

ARABIZI_WORDS  = "../data/arabizi-wanlp/words_annotated.csv"
ARABIZI_SENTS  = "../data/arabizi-wanlp/sen_annotated.csv"
ARCS_FILE      = "../data/arabic-english-cs/AR-EN Intra-word CS Corpus.txt"

LABEL_COLORS = {
    "AR":     "#534AB7",
    "EN":     "#1D9E75",
    "AR-LAT": "#D85A30",
    "MIX":    "#BA7517",
    "OTHER":  "#888780",
    "ar":     "#534AB7",
    "en":     "#1D9E75",
    "ar-lat": "#D85A30",
    "fr":     "#D4537E",
    "other":  "#888780",
}


def analyze_arabizi():
    print("\n=== Arabizi Dataset (WANLP 2022) ===")
    try:
        words = pd.read_csv(ARABIZI_WORDS)
        print(f"  Total tokens:    {len(words):,}")
        print(f"  Columns:         {list(words.columns)}")

        if "label" in words.columns:
            dist = words["label"].value_counts()
            print("\n  Label distribution:")
            for label, count in dist.items():
                pct = 100 * count / len(words)
                print(f"    {label:10s}: {count:6,}  ({pct:.1f}%)")

            fig, ax = plt.subplots(figsize=(7, 4))
            colors = [LABEL_COLORS.get(str(l).lower(), "#888780") for l in dist.index]
            dist.plot(kind="bar", ax=ax, color=colors, edgecolor="none")
            ax.set_title("Token label distribution — Arabizi (WANLP 2022)", fontsize=12)
            ax.set_xlabel("Label")
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=0)
            plt.tight_layout()
            plt.savefig("figures/arabizi_label_dist.png", dpi=150)
            plt.close()
            print("\n  Saved: figures/arabizi_label_dist.png")

    except FileNotFoundError:
        print(f"  File not found: {ARABIZI_WORDS}")
        print("  Run: bash data/arabizi-wanlp/download.sh first.")

    try:
        sents = pd.read_csv(ARABIZI_SENTS)
        print(f"\n  Total sentences: {len(sents):,}")
        print(f"  Columns:         {list(sents.columns)}")
    except FileNotFoundError:
        pass


def analyze_arcs():
    print("\n=== Arabic-English CS Corpus (Kaggle 2021) ===")
    try:
        tokens, labels, sent_lengths = [], [], []
        current_sent = []

        with open(ARCS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    if current_sent:
                        sent_lengths.append(len(current_sent))
                        current_sent = []
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        tokens.append(parts[0])
                        labels.append(parts[-1])
                        current_sent.append(parts[0])

        if current_sent:
            sent_lengths.append(len(current_sent))

        print(f"  Total tokens:    {len(tokens):,}")
        print(f"  Total sentences: {len(sent_lengths):,}")
        print(f"  Avg tokens/sent: {sum(sent_lengths)/len(sent_lengths):.1f}")
        print(f"  Max tokens/sent: {max(sent_lengths)}")
        print(f"  Min tokens/sent: {min(sent_lengths)}")

        label_series = pd.Series(labels)
        dist = label_series.value_counts()
        print("\n  Label distribution:")
        for label, count in dist.items():
            pct = 100 * count / len(labels)
            print(f"    {label:10s}: {count:6,}  ({pct:.1f}%)")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        colors = [LABEL_COLORS.get(str(l).upper(), "#888780") for l in dist.index]
        dist.plot(kind="bar", ax=axes[0], color=colors, edgecolor="none")
        axes[0].set_title("Label distribution — Arabic-English CS Corpus", fontsize=11)
        axes[0].set_xlabel("Label")
        axes[0].set_ylabel("Count")
        axes[0].tick_params(axis="x", rotation=0)

        pd.Series(sent_lengths).plot(kind="hist", ax=axes[1], bins=30, color="#534AB7", edgecolor="none")
        axes[1].set_title("Sentence length distribution (tokens)", fontsize=11)
        axes[1].set_xlabel("Tokens per sentence")
        axes[1].set_ylabel("Frequency")

        plt.tight_layout()
        plt.savefig("figures/arcs_stats.png", dpi=150)
        plt.close()
        print("\n  Saved: figures/arcs_stats.png")

    except FileNotFoundError:
        print(f"  File not found: {ARCS_FILE}")
        print("  Run: bash data/arabic-english-cs/download.sh first.")


def combined_summary():
    print("\n=== Combined Dataset Summary ===")
    rows = [
        ["Arabizi (WANLP 2022)", "~12,000", "~80,000", "AR / EN / AR-LAT / FR / OTHER",
         "Reddit + Twitter", "Manual + auto", "WANLP @ ACL 2022"],
        ["Arabic-English CS Corpus", "~10,000", "~60,000", "AR / EN / MIX / OTHER",
         "Mixed social media", "Manual", "Kaggle 2021"],
    ]
    df = pd.DataFrame(rows, columns=[
        "Dataset", "Sentences", "Tokens", "Labels",
        "Source", "Annotation", "Venue"
    ])
    print(df.to_string(index=False))


if __name__ == "__main__":
    analyze_arabizi()
    analyze_arcs()
    combined_summary()
    print("\nDescriptive statistics complete.")
