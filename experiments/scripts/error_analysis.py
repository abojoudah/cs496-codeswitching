"""
error_analysis.py
============================================================
CS496 Code-Switching Project — Phase 5: Error Analysis
============================================================

Analyzes token-level errors across all models and strategies.
Produces:
  - error_taxonomy.json     (error category counts)
  - error_cases.json        (representative failure cases)
  - contrastive_examples.json (tokens where models disagree)
  - all_errors.json         (full error records, capped at 500)
  - error_taxonomy.md       (human-readable write-up)

Usage:
  python3 error_analysis.py \
    --results-dir experiments/results \
    --sample experiments/data/sample_500.json \
    --out experiments/results/error_analysis
"""

import argparse
import glob
import json
import os
from collections import Counter, defaultdict

VALID_LABELS = ["AR", "EN", "AR-LAT", "OTHER", "OL"]

# ── Model config ──────────────────────────────────────────────────────────
# Map folder/file prefixes to display names
MODEL_PATTERNS = {
    "o4-mini": "GPT o4-mini",
    "claude-sonnet-4-6": "Claude Sonnet",
    "gemini-2.5-flash": "Gemini Flash",
    "meta-llama-Llama-3.3-70B-Instruct-Turbo": "LLaMA 70B",
}

STRATEGY_ORDER = ["zero_shot", "few_shot"]


def discover_parsed_files(results_dir):
    """Find all *_lid_parsed.json files recursively."""
    entries = []
    for path in sorted(glob.glob(f"{results_dir}/**/*_lid_parsed.json", recursive=True)):
        fname = os.path.basename(path)
        stem = fname.replace("_lid_parsed.json", "")
        model, strat = None, None
        for s in STRATEGY_ORDER:
            if stem.endswith(f"_{s}"):
                model = stem[: -len(f"_{s}")]
                strat = s
                break
        if model and strat:
            display = MODEL_PATTERNS.get(model, model)
            entries.append({"model": model, "display": display, "strategy": strat, "path": path})
    return entries


def categorize_error(gold, pred):
    return f"{gold}→{pred}"


def severity(gold, pred):
    severe = {
        frozenset({"AR-LAT", "EN"}), frozenset({"AR", "EN"}),
        frozenset({"OL", "EN"}), frozenset({"AR", "AR-LAT"}),
    }
    mild = {
        frozenset({"OTHER", "EN"}), frozenset({"OTHER", "AR"}),
        frozenset({"OTHER", "AR-LAT"}), frozenset({"OTHER", "OL"}),
    }
    pair = frozenset({gold, pred})
    if pair in severe:
        return "Severe"
    elif pair in mild:
        return "Mild"
    else:
        return "Moderate"


def main():
    parser = argparse.ArgumentParser(description="Phase 5: Error Analysis")
    parser.add_argument("--results-dir", default="experiments/results")
    parser.add_argument("--sample", default="experiments/data/sample_500.json")
    parser.add_argument("--out", default="experiments/results/error_analysis")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Load sample
    with open(args.sample) as f:
        sample = json.load(f)
    gold_lookup = {r["id"]: r for r in sample["records"]}

    # Discover and load parsed files
    entries = discover_parsed_files(args.results_dir)
    if not entries:
        print("ERROR: No *_lid_parsed.json files found.")
        return

    parsed = {}
    for e in entries:
        with open(e["path"]) as f:
            parsed[(e["model"], e["strategy"])] = json.load(f)

    models_list = sorted(set(e["model"] for e in entries))
    display_map = {e["model"]: e["display"] for e in entries}

    # ── Build token prediction matrix ─────────────────────────────────────
    token_data = {}
    for sid, rec in gold_lookup.items():
        for tidx, (tok, glabel) in enumerate(zip(rec["tokens"], rec["gold_labels"])):
            token_data[(sid, tidx)] = {
                "sid": sid, "token_idx": tidx, "token": tok,
                "gold": glabel, "dataset": rec["dataset"],
                "text": rec["text"], "preds": {},
            }

    for (model, strat), pdata in parsed.items():
        sent_lookup = {s["id"]: s for s in pdata["sentences"]}
        for key, tinfo in token_data.items():
            sid, tidx = key
            s = sent_lookup.get(sid)
            if not s:
                continue
            ptokens = s.get("predicted_tokens", [])
            gold_labels = gold_lookup[sid]["gold_labels"]
            if len(ptokens) != len(gold_labels):
                tinfo["preds"][(model, strat)] = "__SKIP__"
                continue
            plabel = ptokens[tidx].get("label", "OTHER")
            if plabel not in VALID_LABELS:
                plabel = "OTHER"
            tinfo["preds"][(model, strat)] = plabel

    # ── Collect errors ────────────────────────────────────────────────────
    error_counts = defaultdict(Counter)
    error_by_dataset = defaultdict(lambda: defaultdict(Counter))
    error_records = []
    sev_counts = defaultdict(Counter)

    for key, tinfo in token_data.items():
        for (model, strat), plabel in tinfo["preds"].items():
            if plabel == "__SKIP__":
                continue
            gold = tinfo["gold"]
            if plabel != gold:
                cat = categorize_error(gold, plabel)
                sev = severity(gold, plabel)
                error_counts[(model, strat)][cat] += 1
                error_by_dataset[(model, strat)][tinfo["dataset"]][cat] += 1
                sev_counts[(model, strat)][sev] += 1
                error_records.append({
                    "sid": tinfo["sid"], "token_idx": tinfo["token_idx"],
                    "token": tinfo["token"], "gold": gold, "predicted": plabel,
                    "category": cat, "severity": sev, "dataset": tinfo["dataset"],
                    "model": model, "display": display_map.get(model, model),
                    "strategy": strat, "sentence": tinfo["text"][:150],
                })

    # ── Error taxonomy ────────────────────────────────────────────────────
    total_cat = Counter()
    for counts in error_counts.values():
        total_cat += counts
    total_errors = sum(total_cat.values())

    taxonomy = {
        "total_errors": total_errors,
        "categories": [
            {"category": cat, "count": cnt, "pct": round(cnt / total_errors * 100, 1)}
            for cat, cnt in total_cat.most_common()
        ],
    }
    with open(f"{args.out}/error_taxonomy.json", "w") as f:
        json.dump(taxonomy, f, indent=2)

    # ── Contrastive examples (zero-shot) ──────────────────────────────────
    contrastive = []
    for key, tinfo in token_data.items():
        zs = {}
        for m in models_list:
            p = tinfo["preds"].get((m, "zero_shot"), "__SKIP__")
            if p != "__SKIP__":
                zs[m] = p
        if len(zs) < len(models_list):
            continue
        correct = [m for m, p in zs.items() if p == tinfo["gold"]]
        wrong = [m for m, p in zs.items() if p != tinfo["gold"]]
        if correct and wrong:
            contrastive.append({
                "token": tinfo["token"], "gold": tinfo["gold"],
                "dataset": tinfo["dataset"], "sid": tinfo["sid"],
                "sentence": tinfo["text"][:120],
                **{display_map.get(m, m): zs[m] for m in models_list},
            })

    # Deduplicate by pattern
    seen = set()
    top_contrastive = []
    for c in contrastive:
        preds = tuple(c.get(display_map.get(m, m)) for m in models_list)
        cat_key = (c["gold"], preds)
        if cat_key not in seen and len(top_contrastive) < 20:
            seen.add(cat_key)
            top_contrastive.append(c)

    with open(f"{args.out}/contrastive_examples.json", "w") as f:
        json.dump(top_contrastive, f, indent=2, ensure_ascii=False)

    # ── Representative error cases ────────────────────────────────────────
    rep_cases = []
    seen_rep = set()
    for rec in sorted(error_records, key=lambda x: x["category"]):
        if rec["strategy"] != "zero_shot":
            continue
        cat_model = (rec["category"], rec["model"])
        if cat_model in seen_rep:
            continue
        if len(rep_cases) >= 20:
            break
        seen_rep.add(cat_model)
        rep_cases.append(rec)

    with open(f"{args.out}/error_cases.json", "w") as f:
        json.dump(rep_cases, f, indent=2, ensure_ascii=False)

    # ── All errors sample ─────────────────────────────────────────────────
    with open(f"{args.out}/all_errors.json", "w") as f:
        json.dump(error_records[:500], f, indent=2, ensure_ascii=False)

    # ── Print summary ─────────────────────────────────────────────────────
    print("=" * 70)
    print(f"Error Analysis Complete — {total_errors} total errors across {len(parsed)} runs")
    print("=" * 70)
    print(f"\nTop error categories:")
    for cat, cnt in total_cat.most_common(5):
        print(f"  {cat:<20} {cnt:>6} ({cnt/total_errors*100:.1f}%)")
    print(f"\nContrastive examples found: {len(contrastive)} ({len(top_contrastive)} unique patterns saved)")
    print(f"Representative cases saved: {len(rep_cases)}")
    print(f"\nOutputs saved to: {args.out}/")
    print("  error_taxonomy.json")
    print("  contrastive_examples.json")
    print("  error_cases.json")
    print("  all_errors.json")


if __name__ == "__main__":
    main()
