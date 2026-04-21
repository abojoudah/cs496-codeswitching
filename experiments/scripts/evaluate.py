"""
evaluate.py
============================================================
CS496 Code-Switching Project — Evaluation Script
============================================================

Computes evaluation metrics for both experiments:

LID (Language Identification):
  - Token-level accuracy
  - Macro F1, Micro F1
  - Per-label precision, recall, F1
  - 5x5 confusion matrix
  - Parse failure rate

MT (Machine Translation):
  - BLEU (SacreBLEU)
  - chrF++
  - BERTScore (precision, recall, F1)
  - Parse failure rate

Usage:
  python evaluate.py --parsed <parsed_file.json> --sample <sample_500.json> [--out <output_dir>]

The script auto-detects whether the parsed file is LID or MT.
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

import pandas as pd
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
    confusion_matrix,
)

VALID_LABELS = ["AR", "EN", "AR-LAT", "OTHER", "OL"]


# ─────────────────────────────────────────────────────────────────────────────
#  LID Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_lid(parsed_data: dict, sample_data: dict) -> dict:
    """Compute all LID metrics."""

    # Build gold lookup by sentence id
    gold_lookup = {r["id"]: r for r in sample_data["records"]}

    y_true = []
    y_pred = []
    aligned_sentences = 0
    skipped_sentences = 0
    skipped_details = []

    for s in parsed_data["sentences"]:
        sid = s["id"]
        if sid not in gold_lookup:
            continue

        gold_labels = gold_lookup[sid]["gold_labels"]
        pred_tokens = s.get("predicted_tokens", [])

        # Skip sentences with mismatched token counts
        if len(pred_tokens) != len(gold_labels):
            skipped_sentences += 1
            skipped_details.append({
                "id": sid,
                "expected": len(gold_labels),
                "got": len(pred_tokens),
            })
            continue

        for gold, pred in zip(gold_labels, pred_tokens):
            pred_label = pred.get("label")
            if pred_label not in VALID_LABELS:
                pred_label = "OTHER"  # fallback for invalid labels
            y_true.append(gold)
            y_pred.append(pred_label)

        aligned_sentences += 1

    # Overall metrics
    accuracy = accuracy_score(y_true, y_pred) if y_true else 0.0

    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=VALID_LABELS, average="macro", zero_division=0
    )
    micro_p, micro_r, micro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=VALID_LABELS, average="micro", zero_division=0
    )

    # Per-label metrics
    per_label_p, per_label_r, per_label_f1, per_label_support = precision_recall_fscore_support(
        y_true, y_pred, labels=VALID_LABELS, zero_division=0
    )

    per_label_metrics = []
    for i, label in enumerate(VALID_LABELS):
        per_label_metrics.append({
            "label": label,
            "precision": round(float(per_label_p[i]), 4),
            "recall": round(float(per_label_r[i]), 4),
            "f1": round(float(per_label_f1[i]), 4),
            "support": int(per_label_support[i]),
        })

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=VALID_LABELS)
    cm_df = pd.DataFrame(cm, index=VALID_LABELS, columns=VALID_LABELS)

    # Parse failure rate (from the parsed file metadata)
    parse_failures = parsed_data.get("parse_failures", 0)
    total_sentences = parsed_data.get("total_sentences", len(parsed_data["sentences"]))
    parse_failure_rate = (parse_failures / total_sentences * 100) if total_sentences else 0.0

    return {
        "experiment": "lid",
        "model": parsed_data.get("model"),
        "strategy": parsed_data.get("strategy"),
        "total_sentences": total_sentences,
        "aligned_sentences": aligned_sentences,
        "skipped_sentences": skipped_sentences,
        "total_tokens_evaluated": len(y_true),
        "accuracy": round(float(accuracy), 4),
        "macro_precision": round(float(macro_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "macro_f1": round(float(macro_f1), 4),
        "micro_precision": round(float(micro_p), 4),
        "micro_recall": round(float(micro_r), 4),
        "micro_f1": round(float(micro_f1), 4),
        "parse_failure_rate": round(parse_failure_rate, 2),
        "per_label_metrics": per_label_metrics,
        "confusion_matrix": cm_df.to_dict(),
        "skipped_details": skipped_details[:20],  # cap at 20 for readability
    }


# ─────────────────────────────────────────────────────────────────────────────
#  MT Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_mt(parsed_data: dict, sample_data: dict, references_path: str = None) -> dict:
    """
    Compute MT metrics.

    Reference translations must be provided in a separate JSON file:
    {
      "references": {
        "arabizi_001": "I am going to the university...",
        "arencs_001": "...",
        ...
      }
    }
    """
    try:
        from sacrebleu.metrics import BLEU, CHRF
    except ImportError:
        print("ERROR: sacrebleu not installed. Run: pip install sacrebleu")
        sys.exit(1)

    try:
        from bert_score import score as bert_score
    except ImportError:
        print("WARNING: bert-score not installed. BERTScore will be skipped.")
        print("  Install with: pip install bert-score")
        bert_score = None

    if not references_path or not os.path.exists(references_path):
        print(f"ERROR: References file required for MT evaluation: {references_path}")
        sys.exit(1)

    with open(references_path, "r", encoding="utf-8") as f:
        ref_data = json.load(f)

    references_lookup = ref_data["references"]

    hypotheses = []
    references = []
    matched = 0

    for s in parsed_data["sentences"]:
        sid = s["id"]
        if sid not in references_lookup:
            continue
        translation = s.get("translation", "").strip()
        if not translation:
            continue
        hypotheses.append(translation)
        references.append(references_lookup[sid])
        matched += 1

    # Compute BLEU
    bleu = BLEU()
    bleu_score = bleu.corpus_score(hypotheses, [references])

    # Compute chrF++
    chrf = CHRF(word_order=2)  # word_order=2 makes it chrF++
    chrf_score = chrf.corpus_score(hypotheses, [references])

    # Compute BERTScore
    bert_p, bert_r, bert_f1 = (None, None, None)
    if bert_score is not None:
        P, R, F1 = bert_score(hypotheses, references, lang="en", verbose=False)
        bert_p = round(float(P.mean()), 4)
        bert_r = round(float(R.mean()), 4)
        bert_f1 = round(float(F1.mean()), 4)

    # Parse failure rate
    parse_failures = parsed_data.get("parse_failures", 0)
    total_sentences = parsed_data.get("total_sentences", len(parsed_data["sentences"]))
    parse_failure_rate = (parse_failures / total_sentences * 100) if total_sentences else 0.0

    return {
        "experiment": "mt",
        "model": parsed_data.get("model"),
        "strategy": parsed_data.get("strategy"),
        "total_sentences": total_sentences,
        "matched_sentences": matched,
        "bleu": round(bleu_score.score, 2),
        "chrf_pp": round(chrf_score.score, 2),
        "bertscore_precision": bert_p,
        "bertscore_recall": bert_r,
        "bertscore_f1": bert_f1,
        "parse_failure_rate": round(parse_failure_rate, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Reporting
# ─────────────────────────────────────────────────────────────────────────────

def print_lid_report(metrics: dict):
    """Print a human-readable LID evaluation report."""
    print("=" * 70)
    print(f"LID EVALUATION REPORT — {metrics['model']} ({metrics['strategy']})")
    print("=" * 70)
    print(f"Total sentences        : {metrics['total_sentences']}")
    print(f"Aligned sentences      : {metrics['aligned_sentences']}")
    print(f"Skipped (count mismatch): {metrics['skipped_sentences']}")
    print(f"Total tokens evaluated : {metrics['total_tokens_evaluated']}")
    print(f"Parse failure rate     : {metrics['parse_failure_rate']}%")
    print()
    print("OVERALL METRICS")
    print("-" * 70)
    print(f"  Accuracy   : {metrics['accuracy']:.4f}")
    print(f"  Macro F1   : {metrics['macro_f1']:.4f}  (P={metrics['macro_precision']:.4f}, R={metrics['macro_recall']:.4f})")
    print(f"  Micro F1   : {metrics['micro_f1']:.4f}  (P={metrics['micro_precision']:.4f}, R={metrics['micro_recall']:.4f})")
    print()
    print("PER-LABEL METRICS")
    print("-" * 70)
    print(f"{'Label':<10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    for m in metrics["per_label_metrics"]:
        print(f"{m['label']:<10} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1']:>10.4f} {m['support']:>10}")
    print()
    print("CONFUSION MATRIX")
    print("-" * 70)
    cm = pd.DataFrame(metrics["confusion_matrix"])
    cm = cm.reindex(index=VALID_LABELS, columns=VALID_LABELS).fillna(0).astype(int)
    print("Rows = gold, Columns = predicted")
    print(cm)
    print("=" * 70)


def print_mt_report(metrics: dict):
    """Print a human-readable MT evaluation report."""
    print("=" * 70)
    print(f"MT EVALUATION REPORT — {metrics['model']} ({metrics['strategy']})")
    print("=" * 70)
    print(f"Total sentences        : {metrics['total_sentences']}")
    print(f"Matched with references: {metrics['matched_sentences']}")
    print(f"Parse failure rate     : {metrics['parse_failure_rate']}%")
    print()
    print("TRANSLATION METRICS")
    print("-" * 70)
    print(f"  BLEU                 : {metrics['bleu']}")
    print(f"  chrF++               : {metrics['chrf_pp']}")
    if metrics["bertscore_f1"] is not None:
        print(f"  BERTScore Precision  : {metrics['bertscore_precision']:.4f}")
        print(f"  BERTScore Recall     : {metrics['bertscore_recall']:.4f}")
        print(f"  BERTScore F1         : {metrics['bertscore_f1']:.4f}")
    else:
        print(f"  BERTScore            : skipped (bert-score not installed)")
    print("=" * 70)


def save_csv_outputs(metrics: dict, output_dir: str):
    """Save metric tables as CSV for easy import into reports."""
    os.makedirs(output_dir, exist_ok=True)

    base = f"{metrics['model'].replace('/', '-')}_{metrics['strategy']}_{metrics['experiment']}"

    if metrics["experiment"] == "lid":
        # Overall metrics row
        overall = pd.DataFrame([{
            "model": metrics["model"],
            "strategy": metrics["strategy"],
            "accuracy": metrics["accuracy"],
            "macro_precision": metrics["macro_precision"],
            "macro_recall": metrics["macro_recall"],
            "macro_f1": metrics["macro_f1"],
            "micro_precision": metrics["micro_precision"],
            "micro_recall": metrics["micro_recall"],
            "micro_f1": metrics["micro_f1"],
            "parse_failure_rate": metrics["parse_failure_rate"],
        }])
        overall.to_csv(f"{output_dir}/{base}_overall.csv", index=False)

        # Per-label metrics
        per_label = pd.DataFrame(metrics["per_label_metrics"])
        per_label.to_csv(f"{output_dir}/{base}_per_label.csv", index=False)

        # Confusion matrix
        cm = pd.DataFrame(metrics["confusion_matrix"])
        cm = cm.reindex(index=VALID_LABELS, columns=VALID_LABELS).fillna(0).astype(int)
        cm.to_csv(f"{output_dir}/{base}_confusion_matrix.csv")

        print(f"\nCSV outputs saved to: {output_dir}/{base}_*.csv")

    elif metrics["experiment"] == "mt":
        overall = pd.DataFrame([{
            "model": metrics["model"],
            "strategy": metrics["strategy"],
            "bleu": metrics["bleu"],
            "chrf_pp": metrics["chrf_pp"],
            "bertscore_precision": metrics["bertscore_precision"],
            "bertscore_recall": metrics["bertscore_recall"],
            "bertscore_f1": metrics["bertscore_f1"],
            "parse_failure_rate": metrics["parse_failure_rate"],
        }])
        overall.to_csv(f"{output_dir}/{base}_overall.csv", index=False)
        print(f"\nCSV outputs saved to: {output_dir}/{base}_overall.csv")


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evaluate LID or MT model outputs.")
    parser.add_argument("--parsed", required=True, help="Path to parsed output JSON file.")
    parser.add_argument("--sample", required=True, help="Path to sample_500.json.")
    parser.add_argument("--references", default=None, help="Path to MT references JSON (required for MT).")
    parser.add_argument("--out", default="experiments/results", help="Output directory for CSV files.")
    parser.add_argument("--save-json", action="store_true", help="Also save full metrics as JSON.")
    args = parser.parse_args()

    # Load inputs
    with open(args.parsed, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    with open(args.sample, "r", encoding="utf-8") as f:
        sample_data = json.load(f)

    experiment = parsed_data.get("experiment", "lid")

    # Run evaluation
    if experiment == "lid":
        metrics = evaluate_lid(parsed_data, sample_data)
        print_lid_report(metrics)
    elif experiment == "mt":
        metrics = evaluate_mt(parsed_data, sample_data, args.references)
        print_mt_report(metrics)
    else:
        print(f"Unknown experiment type: {experiment}")
        sys.exit(1)

    # Save outputs
    save_csv_outputs(metrics, args.out)

    if args.save_json:
        base = f"{metrics['model'].replace('/', '-')}_{metrics['strategy']}_{metrics['experiment']}"
        json_path = f"{args.out}/{base}_metrics.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2, default=str)
        print(f"Full metrics JSON saved to: {json_path}")


if __name__ == "__main__":
    main()
