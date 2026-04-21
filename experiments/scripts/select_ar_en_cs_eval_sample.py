import json
import math
from collections import Counter, defaultdict
from random import Random

INPUT_PATH = "AR-EN Intra-word CS Corpus.txt"
OUTPUT_PATH = "ar_en_cs_eval_sample_seed42.json"
SEED = 42
SAMPLE_SIZE = 250

def map_tag(tag: str):
    """Map original corpus tags into unified evaluation labels."""
    if tag in {"AR", "NE.AR"}:
        return "AR"
    if tag in {"EN", "NE.EN"}:
        return "EN"
    if tag in {"OTHER", "AMBIG"}:
        return "OTHER"
    if tag == "LANG3":
        return "OL"

    # Composite tags such as "AR EN", "EN AR", "AR EN AR", ...
    # Take the first recognizable label for token-level assignment
    for part in tag.split():
        if part in {"AR", "NE.AR"}:
            return "AR"
        if part in {"EN", "NE.EN"}:
            return "EN"
        if part in {"OTHER", "AMBIG"}:
            return "OTHER"
        if part == "LANG3":
            return "OL"

    return "OTHER"  # fallback for truly unrecognized tags

def map_tag_for_counts(tag: str):
    """Original multi-label version used for sentence-level statistics."""
    if tag in {"AR", "NE.AR"}:
        return ["AR"]
    if tag in {"EN", "NE.EN"}:
        return ["EN"]
    if tag in {"OTHER", "AMBIG"}:
        return ["OTHER"]
    if tag == "LANG3":
        return ["OL"]

    mapped = []
    for part in tag.split():
        if part in {"AR", "NE.AR"}:
            mapped.append("AR")
        elif part in {"EN", "NE.EN"}:
            mapped.append("EN")
        elif part in {"OTHER", "AMBIG"}:
            mapped.append("OTHER")
        elif part == "LANG3":
            mapped.append("OL")

    output = []
    for item in mapped:
        if item not in output:
            output.append(item)
    return output

def parse_sentences(path: str):
    """Parse CoNLL-style file where blank lines separate sentences."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    sentences = []
    current = []

    for line in lines:
        if not line.strip():
            if current:
                sentences.append(current)
                current = []
            continue

        parts = line.split("\t")
        if len(parts) >= 3:
            token, normalized, tag = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            token, tag = parts
            normalized = token
        else:
            continue

        current.append((token, normalized, tag))

    if current:
        sentences.append(current)

    return sentences

def build_sentence_records(sentences):
    records = []
    for i, sentence in enumerate(sentences, start=1):
        label_counter = Counter()
        present_labels = set()

        # --- NEW: per-token gold labels ---
        tokens = []
        gold_labels = []
        # ----------------------------------

        for token, normalized, original_tag in sentence:
            # Single label per token for gold_labels list
            single_label = map_tag(original_tag)
            tokens.append(token)
            gold_labels.append(single_label)

            # Multi-label mapping for sentence-level statistics
            mapped_labels = map_tag_for_counts(original_tag)
            present_labels.update(mapped_labels)
            for label in mapped_labels:
                label_counter[label] += 1

        if label_counter["AR"] > label_counter["EN"]:
            dominance = "AR-dominant"
        elif label_counter["EN"] > label_counter["AR"]:
            dominance = "EN-dominant"
        else:
            dominance = "mixed-balanced"

        if "AR" in present_labels and "EN" in present_labels:
            sentence_type = "mixed_AR_EN"
        elif "AR" in present_labels and "EN" not in present_labels:
            sentence_type = "mono_AR"
        elif "EN" in present_labels and "AR" not in present_labels:
            sentence_type = "mono_EN"
        else:
            sentence_type = "other_only"

        records.append({
            "sentence_id": f"ARENCS_{i:04d}",
            "text": " ".join(tokens),
            # --- NEW: per-token gold labels ---
            "tokens": tokens,
            "gold_labels": gold_labels,
            # ----------------------------------
            "token_count": len(sentence),
            "original_tags": sorted({tag for _, _, tag in sentence}),
            "mapped_counts": dict(label_counter),
            "present_labels": sorted(present_labels),
            "dominance": dominance,
            "sentence_type": sentence_type
        })

    return records

def proportional_quotas(counts: dict, sample_size: int):
    """Largest-remainder proportional allocation."""
    total = sum(counts.values())
    raw = {k: v * sample_size / total for k, v in counts.items()}
    floors = {k: int(math.floor(v)) for k, v in raw.items()}
    remaining = sample_size - sum(floors.values())

    remainders = sorted(
        ((raw[k] - floors[k], k) for k in raw),
        reverse=True
    )

    quotas = floors.copy()
    for _, key in remainders[:remaining]:
        quotas[key] += 1

    return quotas

def main():
    sentences = parse_sentences(INPUT_PATH)
    records = build_sentence_records(sentences)

    # Joint strata preserve both dominance and sentence composition.
    strata_counts = Counter((r["dominance"], r["sentence_type"]) for r in records)
    quotas = proportional_quotas(strata_counts, SAMPLE_SIZE)

    grouped = defaultdict(list)
    for record in records:
        grouped[(record["dominance"], record["sentence_type"])].append(record)

    rng = Random(SEED)
    sample = []

    for stratum, quota in quotas.items():
        items = grouped[stratum][:]
        rng.shuffle(items)
        sample.extend(items[:quota])

    sample = sorted(sample, key=lambda x: int(x["sentence_id"].split("_")[1]))

    # Sanity check
    for r in sample[:3]:
        assert len(r["tokens"]) == len(r["gold_labels"]), \
            f"Token/label mismatch in {r['sentence_id']}"

    output = {
        "seed": SEED,
        "dataset": "AR-EN_CS",
        "source_file": INPUT_PATH,
        "total_available_sentences": len(records),
        "sample_size": len(sample),
        "sampling_method": "stratified_random_sample",
        "stratification": {
            "unit": "sentence",
            "scheme": "joint sentence-level strata based on dominance and sentence type",
            "dominance_definition": "AR-dominant if mapped AR token count > EN count; EN-dominant if EN count > AR count; mixed-balanced if equal",
            "sentence_type_definition": "mixed_AR_EN if both AR and EN are present; mono_AR if only AR is present; mono_EN if only EN is present; other_only otherwise",
            "quotas": {f"{k[0]}__{k[1]}": v for k, v in quotas.items()}
        },
        "sample_distribution": {
            "dominance": dict(Counter(r["dominance"] for r in sample)),
            "sentence_type": dict(Counter(r["sentence_type"] for r in sample)),
            "joint": {f"{k[0]}__{k[1]}": v for k, v in Counter((r["dominance"], r["sentence_type"]) for r in sample).items()}
        },
        "samples": sample
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(sample)} sampled sentences to {OUTPUT_PATH}")
    print("Sanity check passed: tokens and gold_labels lengths match.")

if __name__ == "__main__":
    main()
