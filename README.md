# CS496 — Code-Switching Handling in Arabic-English Tasks

This repository contains datasets, annotation resources, and analysis scripts for a project investigating how large language models handle Arabic-English code-switching, including Arabizi (Arabic written in Latin script).

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
│   ├── annotation_sample.csv   # 250-sentence IAA sample
│   └── iaa_compute.py          # Fleiss Kappa computation script
├── analysis/
│   └── descriptive_stats.py    # Descriptive statistics + figures
└── scripts/
    └── preprocess.py           # Shared preprocessing utilities
```

## Datasets

| Dataset | Source | Sentences | Tokens | Task | Script |
|---|---|---|---|---|---|
| Arabizi (WANLP 2022) | GitHub: HaifaCLG/Arabizi | 2,574 | 29,810 | LID, code-switch detection | `data/arabizi-wanlp/download.sh` |
| Arabic-English CS Corpus | Kaggle: islamkaloop | 2,507 | 30,321 | LID, code-switch detection | `data/arabic-english-cs/download.sh` |
| **Combined** | | **5,081** | **60,131** | | |

**Important:** Raw dataset files are not committed to this repository. Run the download scripts to obtain them locally. This ensures compliance with source platform terms of service.

## Unified Label Scheme

Both datasets are mapped to a five-label annotation scheme:

| Label | Description | Example |
|---|---|---|
| AR | Arabic in Arabic script | مرحبا، كيف |
| EN | English in Latin script | hello, working |
| AR-LAT | Arabizi: Arabic in Latin script | marhaba, 7abibi |
| OTHER | Punctuation, digits, symbols | . , ! @ # |
| OL | Other language (e.g. French) | Oui, vraiment |

See each dataset's README for the full label mapping from original annotations.

## Setup

```bash
git clone https://github.com/abojoudah/cs496-codeswitching.git
cd cs496-codeswitching
bash data/arabizi-wanlp/download.sh
bash data/arabic-english-cs/download.sh
pip install pandas numpy scikit-learn matplotlib seaborn nltk
```

## Citation

```bibtex
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
