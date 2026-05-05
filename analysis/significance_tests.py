"""
Task 4: Statistical Significance Tests and Extended Error Analysis
CS496 Code-Switching Project — Kuwait University

This script performs:
1. Gold-label correction (Latin-script AR → AR-LAT)
2. Corrected evaluation for all 8 Task 3 runs + ablation
3. McNemar's test: zero-shot vs few-shot, pairwise model comparison, ablation
4. Extended error taxonomy with frequency counts

Usage:
    python significance_tests.py

Requires: scipy
Input files expected in ../experiments/results/ and ../experiments/data/
"""

import json
import os
import csv
from collections import Counter, defaultdict
from scipy.stats import chi2

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "..", "experiments", "results")
DATA_DIR = os.path.join(BASE_DIR, "..", "experiments", "data")
OUTPUT_DIR = BASE_DIR  # outputs go into /analysis/

GOLD_PATH = os.path.join(DATA_DIR, "sample_500.json")

LABELS = ["AR", "EN", "AR-LAT", "OTHER", "OL"]

TASK3_FILES = {
    "GPT o4-mini ZS": "o4-mini_zero_shot_lid_parsed.json",
    "GPT o4-mini FS": "o4-mini_few_shot_lid_parsed.json",
    "Claude ZS": "claude-sonnet-4-6_zero_shot_lid_parsed.json",
    "Claude FS": "claude-sonnet-4-6_few_shot_lid_parsed.json",
    "Gemini ZS": "gemini-2_5-flash_zero_shot_lid_parsed.json",
    "Gemini FS": "gemini-2_5-flash_few_shot_lid_parsed.json",
    "LLaMA ZS": "meta-llama-Llama-3_3-70B-Instruct-Turbo_zero_shot_lid_parsed.json",
    "LLaMA FS": "meta-llama-Llama-3_3-70B-Instruct-Turbo_few_shot_lid_parsed.json",
}

ABLATION_FILES = {
    "Claude Ablation (10-shot)": "claude-sonnet-4-6_ablation_fewshot10_lid_parsed.json",
}

ALL_FILES = {**TASK3_FILES, **ABLATION_FILES}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def correct_gold_label(gold_label, token_text):
    """If gold=AR but token is Latin script, correct to AR-LAT."""
    if gold_label == "AR" and not any("\u0600" <= c <= "\u06FF" for c in token_text):
        return "AR-LAT"
    return gold_label


def load_gold():
    """Load gold standard records."""
    with open(GOLD_PATH) as f:
        data = json.load(f)
    return {r["id"]: r for r in data["records"]}


def get_token_results(fname, gold_map, use_corrected=False):
    """Returns dict of (sent_id, tok_idx) -> True/False (correct/incorrect)."""
    filepath = os.path.join(RESULTS_DIR, fname)
    with open(filepath) as f:
        pred_data = json.load(f)
    results = {}
    for sent in pred_data["sentences"]:
        sid = sent["id"]
        if sid not in gold_map:
            continue
        grec = gold_map[sid]
        ptoks = sent.get("predicted_tokens", [])
        if len(ptoks) != len(grec["gold_labels"]):
            continue
        for i, (gl, pt) in enumerate(zip(grec["gold_labels"], ptoks)):
            pl = pt["label"]
            tok = pt["token"]
            if use_corrected:
                gl = correct_gold_label(gl, tok)
            results[(sid, i)] = (gl == pl)
    return results


def compute_metrics(golds, preds):
    """Compute accuracy, macro F1, per-label P/R/F1."""
    tp, fp, fn = Counter(), Counter(), Counter()
    correct = 0
    for g, p in zip(golds, preds):
        if g == p:
            correct += 1
            tp[g] += 1
        else:
            fp[p] += 1
            fn[g] += 1
    acc = correct / len(golds) if golds else 0
    per_label = {}
    f1s = []
    for label in LABELS:
        prec = tp[label] / (tp[label] + fp[label]) if (tp[label] + fp[label]) > 0 else 0
        rec = tp[label] / (tp[label] + fn[label]) if (tp[label] + fn[label]) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        per_label[label] = {"P": prec, "R": rec, "F1": f1}
        f1s.append(f1)
    macro_f1 = sum(f1s) / len(f1s)
    return {"accuracy": acc, "macro_f1": macro_f1, "per_label": per_label}


def mcnemar_test(results_a, results_b):
    """McNemar's test with continuity correction on two paired result dicts."""
    common = set(results_a.keys()) & set(results_b.keys())
    b = sum(1 for k in common if results_a[k] and not results_b[k])
    c = sum(1 for k in common if not results_a[k] and results_b[k])
    if b + c == 0:
        return {"b": b, "c": c, "chi2": 0, "p": 1.0, "sig": "n/a"}
    chi2_stat = (abs(b - c) - 1) ** 2 / (b + c)
    p_value = 1 - chi2.cdf(chi2_stat, df=1)
    sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    return {"b": b, "c": c, "chi2": chi2_stat, "p": p_value, "sig": sig}


# ============================================================
# MAIN
# ============================================================

def main():
    print("Loading gold standard...")
    gold_map = load_gold()

    # --- 1. Corrected evaluation ---
    print("\n" + "=" * 70)
    print("CORRECTED EVALUATION (all runs)")
    print("=" * 70)

    corrected_results = {}
    eval_rows = []

    for name, fname in ALL_FILES.items():
        filepath = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(filepath):
            print(f"  SKIP (file not found): {fname}")
            continue

        with open(filepath) as f:
            pred_data = json.load(f)

        golds_orig, golds_corr, preds = [], [], []
        for sent in pred_data["sentences"]:
            sid = sent["id"]
            if sid not in gold_map:
                continue
            grec = gold_map[sid]
            ptoks = sent.get("predicted_tokens", [])
            if len(ptoks) != len(grec["gold_labels"]):
                continue
            for gl, pt in zip(grec["gold_labels"], ptoks):
                tok = pt["token"]
                pl = pt["label"]
                golds_orig.append(gl)
                golds_corr.append(correct_gold_label(gl, tok))
                preds.append(pl)

        orig_m = compute_metrics(golds_orig, preds)
        corr_m = compute_metrics(golds_corr, preds)

        print(f"  {name:<30s}  Orig Acc={orig_m['accuracy']:.3f}  Corr Acc={corr_m['accuracy']:.3f}  "
              f"Orig MaF1={orig_m['macro_f1']:.3f}  Corr MaF1={corr_m['macro_f1']:.3f}")

        eval_rows.append({
            "run": name,
            "orig_accuracy": round(orig_m["accuracy"], 3),
            "corr_accuracy": round(corr_m["accuracy"], 3),
            "orig_macro_f1": round(orig_m["macro_f1"], 3),
            "corr_macro_f1": round(corr_m["macro_f1"], 3),
        })

        corrected_results[name] = get_token_results(fname, gold_map, use_corrected=True)

    # Save corrected evaluation CSV
    eval_csv = os.path.join(OUTPUT_DIR, "corrected_evaluation.csv")
    with open(eval_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=eval_rows[0].keys())
        writer.writeheader()
        writer.writerows(eval_rows)
    print(f"\nSaved: {eval_csv}")

    # --- 2. McNemar's tests ---
    print("\n" + "=" * 70)
    print("McNEMAR'S TESTS (corrected gold)")
    print("=" * 70)

    sig_rows = []

    # 2a. Zero-shot vs few-shot
    print("\n--- Zero-Shot vs Few-Shot ---")
    models = ["GPT o4-mini", "Claude", "Gemini", "LLaMA"]
    for model in models:
        zs_key = f"{model} ZS"
        fs_key = f"{model} FS"
        if zs_key not in corrected_results or fs_key not in corrected_results:
            continue
        result = mcnemar_test(corrected_results[zs_key], corrected_results[fs_key])
        print(f"  {model:<15s}  b={result['b']:>3d}  c={result['c']:>3d}  "
              f"chi2={result['chi2']:.2f}  p={result['p']:.4f}  {result['sig']}")
        sig_rows.append({
            "comparison": f"{model}: ZS vs FS",
            "b": result["b"], "c": result["c"],
            "chi2": round(result["chi2"], 2),
            "p_value": round(result["p"], 4),
            "significance": result["sig"],
        })

    # 2b. Pairwise model comparison (best strategy per model)
    print("\n--- Pairwise Model Comparison ---")
    best = {
        "GPT o4-mini": "GPT o4-mini FS",
        "Claude": "Claude FS",
        "Gemini": "Gemini ZS",
        "LLaMA": "LLaMA ZS",
    }
    model_names = list(best.keys())
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            ma, mb = model_names[i], model_names[j]
            if best[ma] not in corrected_results or best[mb] not in corrected_results:
                continue
            result = mcnemar_test(corrected_results[best[ma]], corrected_results[best[mb]])
            label = f"{ma} vs {mb}"
            print(f"  {label:<25s}  b={result['b']:>3d}  c={result['c']:>3d}  "
                  f"chi2={result['chi2']:.2f}  p={result['p']:.4f}  {result['sig']}")
            sig_rows.append({
                "comparison": label,
                "b": result["b"], "c": result["c"],
                "chi2": round(result["chi2"], 2),
                "p_value": round(result["p"], 4),
                "significance": result["sig"],
            })

    # 2c. Ablation vs Task 3 Claude runs
    print("\n--- Ablation vs Task 3 ---")
    abl_key = "Claude Ablation (10-shot)"
    if abl_key in corrected_results:
        for baseline in ["Claude ZS", "Claude FS"]:
            if baseline not in corrected_results:
                continue
            result = mcnemar_test(corrected_results[abl_key], corrected_results[baseline])
            label = f"Ablation vs {baseline}"
            print(f"  {label:<35s}  b={result['b']:>3d}  c={result['c']:>3d}  "
                  f"chi2={result['chi2']:.2f}  p={result['p']:.4f}  {result['sig']}")
            sig_rows.append({
                "comparison": label,
                "b": result["b"], "c": result["c"],
                "chi2": round(result["chi2"], 2),
                "p_value": round(result["p"], 4),
                "significance": result["sig"],
            })

    # Save significance results CSV
    sig_csv = os.path.join(OUTPUT_DIR, "significance_results.csv")
    with open(sig_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sig_rows[0].keys())
        writer.writeheader()
        writer.writerows(sig_rows)
    print(f"\nSaved: {sig_csv}")

    # --- 3. Error taxonomy (corrected gold, all runs) ---
    print("\n" + "=" * 70)
    print("ERROR TAXONOMY (corrected gold, all Task 3 runs)")
    print("=" * 70)

    error_counts = Counter()
    error_by_dataset = defaultdict(Counter)

    for name, fname in TASK3_FILES.items():
        filepath = os.path.join(RESULTS_DIR, fname)
        if not os.path.exists(filepath):
            continue
        with open(filepath) as f:
            pred_data = json.load(f)
        for sent in pred_data["sentences"]:
            sid = sent["id"]
            if sid not in gold_map:
                continue
            grec = gold_map[sid]
            ptoks = sent.get("predicted_tokens", [])
            if len(ptoks) != len(grec["gold_labels"]):
                continue
            ds = grec["dataset"]
            for gl, pt in zip(grec["gold_labels"], ptoks):
                tok = pt["token"]
                pl = pt["label"]
                cgl = correct_gold_label(gl, tok)
                if cgl != pl:
                    error_key = f"{cgl} -> {pl}"
                    error_counts[error_key] += 1
                    error_by_dataset[ds][error_key] += 1

    total_errors = sum(error_counts.values())
    print(f"Total corrected errors: {total_errors}")

    error_rows = []
    for error_type, count in error_counts.most_common(20):
        pct = count / total_errors * 100
        print(f"  {error_type:<25s}  {count:>5d}  ({pct:.1f}%)")
        error_rows.append({
            "error_type": error_type,
            "count": count,
            "percentage": round(pct, 1),
        })

    # Save error taxonomy CSV
    error_csv = os.path.join(OUTPUT_DIR, "error_taxonomy.csv")
    with open(error_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["error_type", "count", "percentage"])
        writer.writeheader()
        writer.writerows(error_rows)
    print(f"\nSaved: {error_csv}")

    print("\n" + "=" * 70)
    print("DONE. Output files:")
    print(f"  {eval_csv}")
    print(f"  {sig_csv}")
    print(f"  {error_csv}")
    print("=" * 70)


if __name__ == "__main__":
    main()
