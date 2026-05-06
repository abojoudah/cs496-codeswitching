# Code-Switching Handling in Arabic-English Tasks

**Benchmarking LLMs on Arabizi and Mixed Arabic-English Text**

CS496 — Natural Language Processing — Kuwait University — Spring 2025/2026

## Authors

| Name | Email |
|------|-------|
| Yousef Joudeh | s22221110617@ku.edu.kw |
| Seyed Almadani | s2221154931@ku.edu.kw |
| Abdulaziz Mohammed | s2212173741@ku.edu.kw |
| Abdallah Almekhyal | s2231122390@ku.edu.kw |

## Overview

This project investigates how well large language models (LLMs) handle Arabic-English code-switching, focusing on token-level language identification (LID). We benchmark four models — GPT o4-mini, Claude Sonnet 4.6, Gemini 2.5 Flash, and LLaMA 3.3 70B — on two complementary corpora covering Arabizi (Arabic in Latin script) and Arabic-script code-switching.

**Key findings:**
- A gold-label inconsistency was discovered: 55.1% of AR-labeled tokens in the AR-EN CS corpus are actually written in Latin script, inflating reported error rates by 19 percentage points.
- After correction, all models achieve 92–95% accuracy, with Claude Sonnet ranking first (macro F1 = 0.861).
- Few-shot prompting does not significantly improve LID for most models (McNemar's test).
- A targeted 10-shot ablation halves parse failures but cannot resolve intrinsic short-token ambiguity between Arabizi and English.

## Repository Structure

```
cs496-codeswitching/
├── data/
│   ├── README.md                   # Download instructions for datasets
│   └── ...                         # Dataset download scripts
├── annotation/
│   └── iaa_compute.py              # Inter-annotator agreement computation
├── experiments/
│   ├── data/
│   │   └── sample_500.json         # Stratified 500-sentence evaluation sample
│   ├── prompts/
│   │   ├── zero_shot_lid.txt       # Zero-shot prompt template
│   │   ├── few_shot_lid.txt        # Few-shot prompt template (5 examples)
│   │   └── ablation_fewshot10_prompt.txt  # Ablation prompt (10 targeted examples)
│   ├── scripts/
│   │   └── evaluate.py             # Shared evaluation script
│   └── results/
│       ├── o4-mini/                # GPT o4-mini outputs
│       ├── claude-sonnet/          # Claude Sonnet 4.6 outputs (incl. ablation)
│       ├── gemini-flash/           # Gemini 2.5 Flash outputs
│       ├── llama-70b/              # LLaMA 3.3 70B outputs
│       ├── comparison/             # Cross-model comparison tables
│       └── error_analysis/         # Error taxonomy and case studies
├── analysis/
│   ├── significance_tests.py       # McNemar's tests, gold-label correction, error taxonomy
│   ├── corrected_evaluation.csv    # Accuracy & macro F1 under original vs corrected gold
│   ├── significance_results.csv    # McNemar's p-values for all comparisons
│   ├── error_taxonomy.csv          # Error category frequencies after gold correction
│   └── README.md                   # Documentation for analysis scripts
├── paper/
│   └── Code_Switching_Final.pdf    # Final paper (IEEE 2-column format)
├── slides/
│   └── ...                         # Presentation slides (added after presentation)
├── .gitignore
└── README.md                       # This file
```

## Datasets

Two publicly available corpora are used (not redistributed — download scripts provided):

| Dataset | Source | Sentences | Tokens | Focus |
|---------|--------|-----------|--------|-------|
| Arabizi (WANLP 2022) | [HaifaCLG/GitHub](https://github.com/HaifaCLG/Arabizi) | 2,574 | 29,810 | Arabizi + English + French |
| AR-EN CS (Kaggle 2021) | [Kaggle](https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus) | 2,507 | 30,321 | Arabic-script + English |

See `data/README.md` for download instructions.

## Label Scheme

A unified five-label annotation scheme:

| Label | Description | Example |
|-------|-------------|---------|
| AR | Arabic in Arabic script | مرحبا |
| EN | English in Latin script | hello, working |
| AR-LAT | Arabizi: Arabic in Latin script | marhaba, 7abibi |
| OTHER | Punctuation, digits, symbols | . , ! @ # |
| OL | Other language (e.g., French) | Oui, vraiment |

## How to Reproduce

### 1. Clone the repository

```bash
git clone https://github.com/abojoudah/cs496-codeswitching.git
cd cs496-codeswitching
```

### 2. Install dependencies

```bash
pip install scipy
```

### 3. Download datasets

Follow the instructions in `data/README.md` to obtain both corpora.

### 4. Run experiments

The experiment runner is a Google Colab notebook. To run for a specific model:

1. Open the notebook in `experiments/scripts/`
2. Set the model name, API key, and strategy in the config cell
3. The notebook loads `experiments/data/sample_500.json`, calls the API, parses responses, and saves results to `experiments/results/{model}/`

**Experimental parameters:**

| Parameter | Value |
|-----------|-------|
| Temperature | 0.0 |
| Max tokens | 2,048 |
| Batch size | 5 sentences per API call |
| Random seed | 42 |
| Sample size | 500 (250 per dataset) |

### 5. Run evaluation

```bash
cd experiments/scripts
python3 evaluate.py --parsed ../results/claude-sonnet/claude-sonnet-4-6_zero_shot_lid_parsed.json --gold ../data/sample_500.json
```

### 6. Run statistical tests and error analysis

```bash
cd analysis
python3 significance_tests.py
```

This produces:
- `corrected_evaluation.csv` — metrics under original and corrected gold labels
- `significance_results.csv` — McNemar's test p-values
- `error_taxonomy.csv` — error categories after gold-label correction

## Models Tested

| Model | Provider | Access |
|-------|----------|--------|
| GPT o4-mini | OpenAI | API |
| Claude Sonnet 4.6 | Anthropic | API |
| Gemini 2.5 Flash | Google | API |
| LLaMA 3.3 70B Instruct | Meta (open-source) | Together AI API |

## Results Summary

**Overall performance (corrected gold labels):**

| Model | Best Strategy | Accuracy | Macro F1 |
|-------|---------------|----------|----------|
| Claude Sonnet 4.6 | Few-shot | 0.944 | 0.861 |
| Gemini 2.5 Flash | Zero-shot | 0.942 | 0.850 |
| GPT o4-mini | Few-shot | 0.940 | 0.824 |
| LLaMA 3.3 70B | Few-shot | 0.930 | 0.779 |

**Ablation (Claude Sonnet, 10 targeted few-shot examples):**
- Parse failures reduced from 42–46 to 21
- Statistically significant improvement (McNemar's p < 0.01)
- AR-LAT → EN ambiguity persists (44.4% of remaining errors)

## Citation

If you use this work, please cite:

```
Joudeh, Y., Almadani, S., Mohammed, A., & Almekhyal, A. (2026).
Handling Code-Switching in Arabic-English Tasks: Benchmarking LLMs
on Arabizi and Mixed Arabic-English Text. CS496 Course Project,
Kuwait University.
```

## License

This project is for academic purposes (CS496 course project). Datasets are subject to their original licenses.
