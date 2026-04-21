"""
test_evaluate.py
============================================================
Creates dummy parsed output + dummy sample data with known
correct answers, runs evaluate.py, and checks the results.

Run from the repo root:
  python experiments/scripts/test_evaluate.py
============================================================
"""

import json
import os

# ── Create dummy sample (gold standard) ──────────────────────────────────────

dummy_sample = {
    "total_sentences": 3,
    "dataset_breakdown": {"arabizi": 2, "ar_en_cs": 1},
    "total_tokens": 12,
    "label_distribution": {"EN": 5, "AR-LAT": 3, "AR": 2, "OTHER": 2},
    "records": [
        {
            "id": "test_001",
            "dataset": "arabizi",
            "text": "hello 7abibi .",
            "tokens": ["hello", "7abibi", "."],
            "gold_labels": ["EN", "AR-LAT", "OTHER"],
            "sentence_type": "mixed_AR-LAT_EN",
            "n_tokens": 3
        },
        {
            "id": "test_002",
            "dataset": "arabizi",
            "text": "ana raye7 today bro !",
            "tokens": ["ana", "raye7", "today", "bro", "!"],
            "gold_labels": ["AR-LAT", "AR-LAT", "EN", "EN", "OTHER"],
            "sentence_type": "mixed_AR-LAT_EN",
            "n_tokens": 5
        },
        {
            "id": "test_003",
            "dataset": "ar_en_cs",
            "text": "the كتاب is good .",
            "tokens": ["the", "كتاب", "is", "good"],
            "gold_labels": ["EN", "AR", "EN", "AR"],
            "sentence_type": "mixed_AR_EN",
            "n_tokens": 4
        }
    ]
}

# ── Create dummy parsed output (perfect predictions) ─────────────────────────

dummy_parsed_perfect = {
    "model": "test-model",
    "provider": "test",
    "experiment": "lid",
    "strategy": "zero_shot",
    "total_sentences": 3,
    "parse_failures": 0,
    "parse_failure_rate": 0.0,
    "sentences": [
        {
            "id": "test_001",
            "dataset": "arabizi",
            "text": "hello 7abibi .",
            "predicted_tokens": [
                {"token": "hello", "label": "EN"},
                {"token": "7abibi", "label": "AR-LAT"},
                {"token": ".", "label": "OTHER"}
            ],
            "gold_labels": ["EN", "AR-LAT", "OTHER"],
            "n_tokens_expected": 3,
            "n_tokens_predicted": 3
        },
        {
            "id": "test_002",
            "dataset": "arabizi",
            "text": "ana raye7 today bro !",
            "predicted_tokens": [
                {"token": "ana", "label": "AR-LAT"},
                {"token": "raye7", "label": "AR-LAT"},
                {"token": "today", "label": "EN"},
                {"token": "bro", "label": "EN"},
                {"token": "!", "label": "OTHER"}
            ],
            "gold_labels": ["AR-LAT", "AR-LAT", "EN", "EN", "OTHER"],
            "n_tokens_expected": 5,
            "n_tokens_predicted": 5
        },
        {
            "id": "test_003",
            "dataset": "ar_en_cs",
            "text": "the كتاب is good .",
            "predicted_tokens": [
                {"token": "the", "label": "EN"},
                {"token": "كتاب", "label": "AR"},
                {"token": "is", "label": "EN"},
                {"token": "good", "label": "AR"}
            ],
            "gold_labels": ["EN", "AR", "EN", "AR"],
            "n_tokens_expected": 4,
            "n_tokens_predicted": 4
        }
    ]
}

# ── Create dummy parsed output (with errors) ─────────────────────────────────

dummy_parsed_errors = {
    "model": "test-model-bad",
    "provider": "test",
    "experiment": "lid",
    "strategy": "zero_shot",
    "total_sentences": 3,
    "parse_failures": 0,
    "parse_failure_rate": 0.0,
    "sentences": [
        {
            "id": "test_001",
            "dataset": "arabizi",
            "text": "hello 7abibi .",
            "predicted_tokens": [
                {"token": "hello", "label": "EN"},
                {"token": "7abibi", "label": "EN"},       # WRONG: should be AR-LAT
                {"token": ".", "label": "OTHER"}
            ],
            "gold_labels": ["EN", "AR-LAT", "OTHER"],
            "n_tokens_expected": 3,
            "n_tokens_predicted": 3
        },
        {
            "id": "test_002",
            "dataset": "arabizi",
            "text": "ana raye7 today bro !",
            "predicted_tokens": [
                {"token": "ana", "label": "EN"},           # WRONG: should be AR-LAT
                {"token": "raye7", "label": "AR-LAT"},
                {"token": "today", "label": "EN"},
                {"token": "bro", "label": "EN"},
                {"token": "!", "label": "OTHER"}
            ],
            "gold_labels": ["AR-LAT", "AR-LAT", "EN", "EN", "OTHER"],
            "n_tokens_expected": 5,
            "n_tokens_predicted": 5
        },
        {
            "id": "test_003",
            "dataset": "ar_en_cs",
            "text": "the كتاب is good .",
            "predicted_tokens": [
                {"token": "the", "label": "EN"},
                {"token": "كتاب", "label": "EN"},         # WRONG: should be AR
                {"token": "is", "label": "EN"},
                {"token": "good", "label": "EN"}           # WRONG: should be AR
            ],
            "gold_labels": ["EN", "AR", "EN", "AR"],
            "n_tokens_expected": 4,
            "n_tokens_predicted": 4
        }
    ]
}


def main():
    os.makedirs("experiments/results/test", exist_ok=True)

    # Save dummy files
    with open("experiments/results/test/dummy_sample.json", "w") as f:
        json.dump(dummy_sample, f, ensure_ascii=False, indent=2)

    with open("experiments/results/test/dummy_parsed_perfect.json", "w") as f:
        json.dump(dummy_parsed_perfect, f, ensure_ascii=False, indent=2)

    with open("experiments/results/test/dummy_parsed_errors.json", "w") as f:
        json.dump(dummy_parsed_errors, f, ensure_ascii=False, indent=2)

    print("Dummy test files created.\n")

    # ── Test 1: Perfect predictions ──────────────────────────────────────
    print("=" * 70)
    print("TEST 1: Perfect predictions — expecting 100% accuracy, F1 = 1.0")
    print("=" * 70)
    os.system(
        "python experiments/scripts/evaluate.py "
        "--parsed experiments/results/test/dummy_parsed_perfect.json "
        "--sample experiments/results/test/dummy_sample.json "
        "--out experiments/results/test"
    )

    print("\n")

    # ── Test 2: Predictions with errors ──────────────────────────────────
    print("=" * 70)
    print("TEST 2: Predictions with errors — expecting accuracy < 100%")
    print("=" * 70)
    os.system(
        "python experiments/scripts/evaluate.py "
        "--parsed experiments/results/test/dummy_parsed_errors.json "
        "--sample experiments/results/test/dummy_sample.json "
        "--out experiments/results/test"
    )

    print("\n")

    # ── Verify expected results ──────────────────────────────────────────
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print("Test 1 should show: accuracy=1.0, macro_f1=1.0, all per-label F1=1.0")
    print("Test 2 should show:")
    print("  - accuracy < 1.0")
    print("  - AR-LAT recall < 1.0 (one AR-LAT token missed)")
    print("  - AR recall = 0.0 (both AR tokens labeled as EN)")
    print("  - EN precision < 1.0 (AR tokens wrongly labeled as EN)")
    print("  - Confusion matrix should show EN<->AR-LAT and EN<->AR confusion")


if __name__ == "__main__":
    main()
