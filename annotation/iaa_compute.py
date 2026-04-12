"""
Inter-Annotator Agreement (IAA) computation using Fleiss' Kappa.
For use with annotation_sample.csv produced during Task 2.

Usage:
    python iaa_compute.py --file annotation_sample.csv

Requirements:
    pip install pandas numpy
"""

import argparse
import numpy as np
import pandas as pd
from itertools import combinations


LABELS = ["AR", "EN", "AR-LAT", "OTHER", "OL"]

def fleiss_kappa(matrix):
    """
    Compute Fleiss' Kappa for multiple annotators.

    Args:
        matrix: numpy array of shape (n_items, n_categories)
                Each row is one item; each column is a category.
                Cell [i][j] = number of annotators who assigned category j to item i.

    Returns:
        kappa (float): Fleiss' Kappa score
    """
    n_items, n_categories = matrix.shape
    n_annotators = int(matrix[0].sum())

    # Proportion of all assignments to each category
    p_j = matrix.sum(axis=0) / (n_items * n_annotators)

    # Expected agreement by chance
    P_e = (p_j ** 2).sum()

    # Observed agreement per item
    P_i = ((matrix ** 2).sum(axis=1) - n_annotators) / (n_annotators * (n_annotators - 1))
    P_bar = P_i.mean()

    if P_e == 1.0:
        return 1.0

    kappa = (P_bar - P_e) / (1 - P_e)
    return kappa


def interpret_kappa(kappa):
    if kappa < 0:
        return "Poor (worse than chance)"
    elif kappa < 0.20:
        return "Slight"
    elif kappa < 0.40:
        return "Fair"
    elif kappa < 0.60:
        return "Moderate"
    elif kappa < 0.80:
        return "Substantial"
    elif kappa < 0.90:
        return "Good"
    else:
        return "Almost perfect"


def pairwise_cohen_kappa(a1, a2, labels):
    """Compute Cohen's Kappa between two annotators for diagnostic purposes."""
    from collections import Counter

    n = len(a1)
    agree = sum(x == y for x, y in zip(a1, a2))
    P_o = agree / n

    counts_1 = Counter(a1)
    counts_2 = Counter(a2)
    P_e = sum((counts_1.get(l, 0) / n) * (counts_2.get(l, 0) / n) for l in labels)

    if P_e == 1.0:
        return 1.0
    return (P_o - P_e) / (1 - P_e)


def main():
    parser = argparse.ArgumentParser(description="Compute Fleiss Kappa for annotation_sample.csv")
    parser.add_argument("--file", default="annotation_sample.csv", help="Path to annotation CSV")
    args = parser.parse_args()

    print(f"Loading annotations from: {args.file}\n")
    df = pd.read_csv(args.file)

    required_cols = ["sentence_id", "token_id", "token", "annotator_1", "annotator_2", "annotator_3"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Drop rows where any annotator is missing
    annotator_cols = ["annotator_1", "annotator_2", "annotator_3"]
    df_clean = df.dropna(subset=annotator_cols)
    n_dropped = len(df) - len(df_clean)
    if n_dropped > 0:
        print(f"Warning: {n_dropped} rows dropped (missing annotations)\n")

    print(f"Tokens annotated by all 3 annotators: {len(df_clean)}\n")

    # Build Fleiss matrix
    matrix = np.zeros((len(df_clean), len(LABELS)), dtype=int)
    for i, (_, row) in enumerate(df_clean.iterrows()):
        for ann in annotator_cols:
            label = str(row[ann]).strip().upper()
            if label in LABELS:
                j = LABELS.index(label)
                matrix[i][j] += 1
            else:
                print(f"  Warning: Unknown label '{label}' at row {i} — skipped")

    # Fleiss Kappa
    kappa = fleiss_kappa(matrix)
    print("=" * 50)
    print(f"  Fleiss' Kappa (all annotators): {kappa:.4f}")
    print(f"  Interpretation: {interpret_kappa(kappa)}")
    print("=" * 50)

    # Pairwise Cohen Kappa
    print("\nPairwise Cohen's Kappa (diagnostic):")
    pairs = list(combinations(annotator_cols, 2))
    for a, b in pairs:
        k = pairwise_cohen_kappa(
            df_clean[a].str.strip().str.upper().tolist(),
            df_clean[b].str.strip().str.upper().tolist(),
            LABELS
        )
        print(f"  {a} vs {b}: κ = {k:.4f}  ({interpret_kappa(k)})")

    # Per-label agreement
    print("\nPer-label agreement rate:")
    for j, label in enumerate(LABELS):
        col = matrix[:, j]
        perfect = (col == 3).sum()
        total = (col > 0).sum()
        if total > 0:
            print(f"  {label:8s}: {perfect}/{total} tokens fully agreed ({100*perfect/total:.1f}%)")

    # Disagreement analysis
    disagreements = df_clean[
        ~(df_clean["annotator_1"].str.upper() == df_clean["annotator_2"].str.upper()) |
        ~(df_clean["annotator_2"].str.upper() == df_clean["annotator_3"].str.upper())
    ]
    print(f"\nTokens with any disagreement: {len(disagreements)} / {len(df_clean)} "
          f"({100*len(disagreements)/len(df_clean):.1f}%)")

    if len(disagreements) > 0:
        print("\nSample disagreements (first 10):")
        print(disagreements[["sentence_id", "token", "annotator_1", "annotator_2", "annotator_3"]].head(10).to_string(index=False))

    print("\nDone.")


if __name__ == "__main__":
    main()
