"""
compile_results.py
============================================================
CS496 Code-Switching Project — Phase 4: Results Compilation
============================================================

Reads all per-model evaluation outputs from /experiments/results/
and produces three comparison tables:

  Table 1 — Overall Results (Accuracy, Macro F1, Micro F1, Parse Failures)
  Table 2 — Per-Label F1 Breakdown (AR, EN, AR-LAT, OTHER, OL)
  Table 3 — Per-Dataset Comparison (Arabizi vs AR-EN CS)

Usage:
  python compile_results.py --results-dir experiments/results --sample experiments/data/sample_500.json

Output:
  experiments/results/comparison_table1_overall.csv
  experiments/results/comparison_table2_per_label_f1.csv
  experiments/results/comparison_table3_per_dataset.csv
"""

import argparse
import glob
import json
import os

import pandas as pd
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
)

VALID_LABELS = ["AR", "EN", "AR-LAT", "OTHER", "OL"]

# Friendly display names — adjust if needed
MODEL_DISPLAY = {
    "o4-mini": "GPT o4-mini",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "meta-llama-Llama-3.3-70B-Instruct-Turbo": "LLaMA 3.3 70B",
}

STRATEGY_ORDER = ["zero_shot", "few_shot"]
MODEL_ORDER = list(MODEL_DISPLAY.keys())


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def discover_models(results_dir: str) -> list[tuple[str, str, str]]:
    """Find all (model, strategy, prefix) tuples from _metrics.json files."""
    entries = []
    for path in sorted(glob.glob(f"{results_dir}/*_lid_metrics.json")):
        fname = os.path.basename(path)
        # Pattern: {model}_{strategy}_lid_metrics.json
        suffix = "_lid_metrics.json"
        stem = fname[: -len(suffix)]
        # Strategy is the last part before _lid
        for strat in ["zero_shot", "few_shot"]:
            if stem.endswith(f"_{strat}"):
                model = stem[: -len(f"_{strat}")]
                entries.append((model, strat, path))
                break
    return entries


def sort_key(model: str, strategy: str) -> tuple:
    """Sort by model order then strategy order."""
    m_idx = MODEL_ORDER.index(model) if model in MODEL_ORDER else 99
    s_idx = STRATEGY_ORDER.index(strategy) if strategy in STRATEGY_ORDER else 99
    return (m_idx, s_idx)


# ─────────────────────────────────────────────────────────────────────────────
#  Table 1 — Overall Results
# ─────────────────────────────────────────────────────────────────────────────

def build_table1(results_dir: str) -> pd.DataFrame:
    """Build Table 1 from _overall.csv files."""
    rows = []
    for path in sorted(glob.glob(f"{results_dir}/*_lid_overall.csv")):
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            rows.append(row.to_dict())

    if not rows:
        # Fallback: try _metrics.json
        for model, strat, path in discover_models(results_dir):
            with open(path) as f:
                m = json.load(f)
            rows.append({
                "model": m.get("model", model),
                "strategy": m.get("strategy", strat),
                "accuracy": m["accuracy"],
                "macro_f1": m["macro_f1"],
                "micro_f1": m["micro_f1"],
                "parse_failure_rate": m["parse_failure_rate"],
            })

    df = pd.DataFrame(rows)

    # Add display name
    df["Model"] = df["model"].map(lambda x: MODEL_DISPLAY.get(x, x))
    df["Strategy"] = df["strategy"].map({"zero_shot": "Zero-shot", "few_shot": "Few-shot"})

    # Sort
    df["_sort"] = df.apply(lambda r: sort_key(r["model"], r["strategy"]), axis=1)
    df = df.sort_values("_sort").drop(columns=["_sort"])

    # Select and rename columns
    table = df[["Model", "Strategy", "accuracy", "macro_f1", "micro_f1", "parse_failure_rate"]].copy()
    table.columns = ["Model", "Strategy", "Accuracy", "Macro F1", "Micro F1", "Parse Fail %"]
    table = table.reset_index(drop=True)
    return table


# ─────────────────────────────────────────────────────────────────────────────
#  Table 2 — Per-Label F1 Breakdown
# ─────────────────────────────────────────────────────────────────────────────

def build_table2(results_dir: str) -> pd.DataFrame:
    """Build Table 2 from _per_label.csv files."""
    rows = []
    for path in sorted(glob.glob(f"{results_dir}/*_lid_per_label.csv")):
        fname = os.path.basename(path)
        suffix = "_lid_per_label.csv"
        stem = fname[: -len(suffix)]
        model, strat = None, None
        for s in STRATEGY_ORDER:
            if stem.endswith(f"_{s}"):
                model = stem[: -len(f"_{s}")]
                strat = s
                break
        if model is None:
            continue

        df = pd.read_csv(path)
        f1_row = {"model": model, "strategy": strat}
        for _, r in df.iterrows():
            f1_row[r["label"]] = r["f1"]
        rows.append(f1_row)

    df = pd.DataFrame(rows)
    df["Model"] = df["model"].map(lambda x: MODEL_DISPLAY.get(x, x))
    df["Strategy"] = df["strategy"].map({"zero_shot": "Zero-shot", "few_shot": "Few-shot"})
    df["_sort"] = df.apply(lambda r: sort_key(r["model"], r["strategy"]), axis=1)
    df = df.sort_values("_sort").drop(columns=["_sort"])

    table = df[["Model", "Strategy"] + VALID_LABELS].copy()
    table = table.reset_index(drop=True)
    return table


# ─────────────────────────────────────────────────────────────────────────────
#  Table 3 — Per-Dataset Comparison (requires re-evaluation)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_subset(parsed_data: dict, sample_data: dict, dataset_filter: str) -> dict:
    """Evaluate on a subset of sentences filtered by dataset field."""
    gold_lookup = {r["id"]: r for r in sample_data["records"] if r["dataset"] == dataset_filter}

    y_true, y_pred = [], []
    aligned = 0

    for s in parsed_data["sentences"]:
        sid = s["id"]
        if sid not in gold_lookup:
            continue

        gold_labels = gold_lookup[sid]["gold_labels"]
        pred_tokens = s.get("predicted_tokens", [])

        if len(pred_tokens) != len(gold_labels):
            continue

        for gold, pred in zip(gold_labels, pred_tokens):
            pred_label = pred.get("label")
            if pred_label not in VALID_LABELS:
                pred_label = "OTHER"
            y_true.append(gold)
            y_pred.append(pred_label)

        aligned += 1

    if not y_true:
        return {"accuracy": 0.0, "macro_f1": 0.0, "micro_f1": 0.0, "aligned": 0, "tokens": 0}

    acc = accuracy_score(y_true, y_pred)
    _, _, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=VALID_LABELS, average="macro", zero_division=0
    )
    _, _, micro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=VALID_LABELS, average="micro", zero_division=0
    )

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "micro_f1": round(float(micro_f1), 4),
        "aligned": aligned,
        "tokens": len(y_true),
    }


def build_table3(results_dir: str, sample_path: str) -> pd.DataFrame:
    """Build Table 3 by re-evaluating parsed outputs per dataset."""
    with open(sample_path) as f:
        sample_data = json.load(f)

    rows = []
    for path in sorted(glob.glob(f"{results_dir}/*_lid_parsed.json")):
        fname = os.path.basename(path)
        suffix = "_lid_parsed.json"
        stem = fname[: -len(suffix)]
        model, strat = None, None
        for s in STRATEGY_ORDER:
            if stem.endswith(f"_{s}"):
                model = stem[: -len(f"_{s}")]
                strat = s
                break
        if model is None:
            continue

        with open(path) as f:
            parsed_data = json.load(f)

        for ds_name in ["arabizi", "ar_en_cs"]:
            metrics = evaluate_subset(parsed_data, sample_data, ds_name)
            rows.append({
                "model": model,
                "strategy": strat,
                "dataset": ds_name,
                "accuracy": metrics["accuracy"],
                "macro_f1": metrics["macro_f1"],
                "micro_f1": metrics["micro_f1"],
                "aligned_sentences": metrics["aligned"],
                "tokens_evaluated": metrics["tokens"],
            })

    df = pd.DataFrame(rows)
    if df.empty:
        print("WARNING: No _lid_parsed.json files found. Table 3 cannot be built.")
        return df

    df["Model"] = df["model"].map(lambda x: MODEL_DISPLAY.get(x, x))
    df["Strategy"] = df["strategy"].map({"zero_shot": "Zero-shot", "few_shot": "Few-shot"})
    df["Dataset"] = df["dataset"].map({"arabizi": "Arabizi", "ar_en_cs": "AR-EN CS"})
    df["_sort"] = df.apply(lambda r: sort_key(r["model"], r["strategy"]), axis=1)
    df = df.sort_values(["_sort", "dataset"]).drop(columns=["_sort"])

    table = df[["Model", "Strategy", "Dataset", "accuracy", "macro_f1", "micro_f1"]].copy()
    table.columns = ["Model", "Strategy", "Dataset", "Accuracy", "Macro F1", "Micro F1"]
    table = table.reset_index(drop=True)
    return table


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase 4: Compile comparison tables.")
    parser.add_argument("--results-dir", default="experiments/results",
                        help="Directory containing per-model evaluation outputs.")
    parser.add_argument("--sample", default="experiments/data/sample_500.json",
                        help="Path to sample_500.json (needed for Table 3).")
    parser.add_argument("--out", default=None,
                        help="Output directory for tables (defaults to results-dir).")
    args = parser.parse_args()

    out_dir = args.out or args.results_dir
    os.makedirs(out_dir, exist_ok=True)

    # ── Table 1 ──────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("TABLE 1 — Overall Results")
    print("=" * 80)
    t1 = build_table1(args.results_dir)
    if not t1.empty:
        print(t1.to_string(index=False))
        t1_path = f"{out_dir}/comparison_table1_overall.csv"
        t1.to_csv(t1_path, index=False)
        print(f"\nSaved: {t1_path}")
    else:
        print("No data found for Table 1.")

    # ── Table 2 ──────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("TABLE 2 — Per-Label F1 Breakdown")
    print("=" * 80)
    t2 = build_table2(args.results_dir)
    if not t2.empty:
        print(t2.to_string(index=False))
        t2_path = f"{out_dir}/comparison_table2_per_label_f1.csv"
        t2.to_csv(t2_path, index=False)
        print(f"\nSaved: {t2_path}")
    else:
        print("No data found for Table 2.")

    # ── Table 3 ──────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("TABLE 3 — Per-Dataset Comparison (Arabizi vs AR-EN CS)")
    print("=" * 80)
    if os.path.exists(args.sample):
        t3 = build_table3(args.results_dir, args.sample)
        if not t3.empty:
            print(t3.to_string(index=False))
            t3_path = f"{out_dir}/comparison_table3_per_dataset.csv"
            t3.to_csv(t3_path, index=False)
            print(f"\nSaved: {t3_path}")
        else:
            print("No parsed JSON files found. Table 3 requires *_lid_parsed.json files.")
    else:
        print(f"Sample file not found: {args.sample}")
        print("Table 3 requires sample_500.json for per-dataset re-evaluation.")

    print("\n" + "=" * 80)
    print("Phase 4 compilation complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
