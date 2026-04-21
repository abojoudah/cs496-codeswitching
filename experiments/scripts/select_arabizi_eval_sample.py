import json
import numpy as np
import pandas as pd

SEED = 42
INPUT_FILE = "experiments/data/words_annotated.csv"
OUTPUT_PATH = "experiments/data/ar_en_cs_eval_sample_seed42.json"

LABEL_MAP = {
    0: "AR-LAT",
    1: "EN",
    2: "OL",
    3: "AR",
    4: "AR-LAT",   # Shared -> AR-LAT (project mapping)
    5: "OTHER",
}

def build_sentence_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["mapped_label"] = df["categ"].map(LABEL_MAP)

    rows = []
    for sen_id, g in df.groupby("sen_id", sort=False):
        labels = g["mapped_label"].tolist()
        tokens = g["token"].astype(str).tolist()
        non_other = [x for x in labels if x != "OTHER"]
        uniq_non_other = sorted(set(non_other))

        if len(uniq_non_other) == 0:
            sentence_type = "other_only"
        elif len(uniq_non_other) == 1:
            sentence_type = f"mono_{uniq_non_other[0]}"
        else:
            sentence_type = "mixed_" + "_".join(uniq_non_other)

        rows.append({
            "sen_id": sen_id,
            "source": g["source"].iloc[0],
            "user_name": int(g["user_name"].iloc[0]),
            "sen_num": int(g["sen_num"].iloc[0]),
            "text": " ".join(tokens),
            # --- NEW: per-token gold labels ---
            "tokens": tokens,
            "gold_labels": labels,
            # ----------------------------------
            "n_tokens": len(g),
            "label_counts": g["mapped_label"].value_counts().to_dict(),
            "non_other_labels": uniq_non_other,
            "contains_ar_lat": "AR-LAT" in uniq_non_other,
            "contains_ol": "OL" in uniq_non_other,
            "contains_en": "EN" in uniq_non_other,
            "contains_ar": "AR" in uniq_non_other,
            "is_mixed_cs": len(uniq_non_other) >= 2,
            "sentence_type": sentence_type,
        })

    return pd.DataFrame(rows)

def largest_remainder_allocation(counts: pd.Series, n_sample: int) -> pd.Series:
    quotas = counts / counts.sum() * n_sample
    alloc = np.floor(quotas).astype(int)
    alloc = alloc.clip(lower=1)

    remainder_to_fill = n_sample - int(alloc.sum())
    remainders = (quotas - alloc).sort_values(ascending=False)

    if remainder_to_fill > 0:
        for idx in remainders.index[:remainder_to_fill]:
            alloc[idx] += 1
    elif remainder_to_fill < 0:
        for idx in remainders.sort_values().index[:abs(remainder_to_fill)]:
            if alloc[idx] > 1:
                alloc[idx] -= 1

    assert int(alloc.sum()) == n_sample
    return alloc

def main():
    df = pd.read_csv(INPUT_FILE)
    sentence_df = build_sentence_table(df)

    counts = sentence_df["sentence_type"].value_counts().sort_index()
    sample_alloc = largest_remainder_allocation(counts, n_sample=250)

    sampled_parts = []
    for sentence_type, k in sample_alloc.items():
        subset = sentence_df[sentence_df["sentence_type"] == sentence_type]
        sampled_parts.append(subset.sample(n=int(k), random_state=SEED))

    sample = pd.concat(sampled_parts, ignore_index=True).sort_values(
        ["sentence_type", "sen_id"]
    ).reset_index(drop=True)

    records = []
    for i, row in sample.iterrows():
        records.append({
            "global_id": i + 1,
            "dataset": "arabizi",
            "original_id": row["sen_id"],
            "text": row["text"],
            # --- NEW: per-token gold labels ---
            "tokens": row["tokens"],
            "gold_labels": row["gold_labels"],
            # ----------------------------------
            "source": row["source"],
            "user_name": int(row["user_name"]),
            "sen_num": int(row["sen_num"]),
            "n_tokens": int(row["n_tokens"]),
            "sentence_type": row["sentence_type"],
            "non_other_labels": row["non_other_labels"],
            "contains_ar_lat": bool(row["contains_ar_lat"]),
            "contains_ol": bool(row["contains_ol"]),
            "contains_en": bool(row["contains_en"]),
            "contains_ar": bool(row["contains_ar"]),
            "is_mixed_cs": bool(row["is_mixed_cs"]),
            "label_counts": row["label_counts"],
        })

    output = {
        "seed": SEED,
        "dataset": "Arabizi (WANLP 2022)",
        "source_file": "words_annotated.csv",
        "sampling_unit": "sentence",
        "sampling_size": 250,
        "population_size": int(len(sentence_df)),
        "sampling_method": (
            "Stratified random sampling over mutually exclusive sentence_type strata "
            "derived from token-level labels grouped by sen_id."
        ),
        "label_mapping": LABEL_MAP,
        "strata_population_counts": counts.to_dict(),
        "strata_sample_counts": sample["sentence_type"].value_counts().sort_index().to_dict(),
        "records": records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(records)} records to {OUTPUT_FILE}")
    # Sanity check
    for r in records[:3]:
        assert len(r["tokens"]) == len(r["gold_labels"]), \
            f"Token/label mismatch in record {r['global_id']}"
    print("Sanity check passed: tokens and gold_labels lengths match.")

if __name__ == "__main__":
    main()
