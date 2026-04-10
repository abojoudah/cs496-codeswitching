# CS496 — Code-Switching Handling in Arabic-English Tasks

This repository contains datasets, annotation resources, and analysis scripts for a thesis project investigating how large language models handle Arabic-English code-switching, including Arabizi (Arabic written in Latin script).

## Research Questions

1. How accurately do LLMs perform language identification on token-level Arabic-English code-switched text?
2. How well do LLMs translate code-switched Arabic-English sentences compared to fine-tuned encoder baselines?
3. What error patterns emerge when models fail on Arabizi vs. standard Arabic-English mixing?

## Repository Structure

```
cs496-codeswitching/
├── data/
│   ├── arabizi-wanlp/          # Arabizi Dataset (WANLP 2022)
│   │   ├── download.sh         # Download script (run this first)
│   │   └── README.md           # Schema, fields, citation
│   └── arabic-english-cs/      # Arabic-English CS Corpus (Kaggle 2021)
│       ├── download.sh         # Download script (run this first)
│       └── README.md           # Schema, fields, citation
├── annotation/
│   ├── guidelines.md           # Annotation guidelines + label definitions
│   ├── annotation_sample.csv   # 250-sentence IAA sample (to be added)
│   └── iaa_compute.py          # Fleiss Kappa computation script
├── analysis/
│   └── descriptive_stats.py    # Descriptive statistics + figures
└── scripts/
    └── preprocess.py           # Shared preprocessing utilities
```

## Datasets

| Dataset | Source | Size | Task | Script |
|---|---|---|---|---|
| Arabizi (WANLP 2022) | GitHub: HaifaCLG/Arabizi | ~12K sentences | LID, code-switch detection | `data/arabizi-wanlp/download.sh` |
| Arabic-English CS Corpus | Kaggle: islamkaloop | ~10K sentences | LID, code-switch detection | `data/arabic-english-cs/download.sh` |

**Important:** Raw dataset files are not committed to this repository. Run the download scripts to obtain them locally. This ensures compliance with source platform terms of service.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/cs496-codeswitching.git
cd cs496-codeswitching
bash data/arabizi-wanlp/download.sh
bash data/arabic-english-cs/download.sh
pip install pandas numpy scikit-learn matplotlib seaborn nltk
```

## Citation

```
@inproceedings{shehadi-wintner-2022-identifying,
  title     = "Identifying Code-switching in {A}rabizi",
  author    = "Shehadi, Safaa and Wintner, Shuly",
  booktitle = "Proceedings of the Seventh Arabic NLP Workshop (WANLP)",
  year      = "2022",
  pages     = "194--204"
}
```

## License and Ethics

- No PII is stored or committed to this repository.
- Tweet IDs only are retained for Twitter-sourced data (Twitter/X ToS compliant).
- All data is used for academic research only.
