# CS496 — Code-Switching Handling in Arabic-English Tasks

This repository contains datasets, annotation resources, experiment scripts, and analysis outputs for a project investigating how large language models handle Arabic-English code-switching, including Arabizi (Arabic written in Latin script).

## Research Questions

1. **RQ1:** To what extent can LLMs accurately perform token-level language identification on Arabic-English code-switched text, and how does performance vary across switching patterns?
2. **RQ2:** Which LLM(s) demonstrate superior performance on Arabic-English code-switched language identification, and is there a statistically meaningful difference across models?

## Key Findings

- **75.4% of all errors** are AR→AR-LAT: models label Arabic-script tokens as Arabizi, revealing a fundamental lack of script awareness.
- **Few-shot prompting does not improve performance** over zero-shot for any model tested.
- **Dataset composition drives difficulty** more than model choice: a 35-point accuracy gap between the Arabizi and AR-EN CS datasets dwarfs the 7.5-point spread between best and worst models.
- **Gemini 2.5 Flash** leads on accuracy (0.763); **Claude Sonnet 4.6** leads on macro F1 (0.683).

## Repository Structure

```
cs496-codeswitching/
├── data/
│   ├── arabizi-wanlp/              # Arabizi Dataset (WANLP 2022)
│   │   ├── download.sh             # Download script (run this first)
│   │   └── README.md               # Schema, fields, citation
│   └── arabic-english-cs/          # Arabic-English CS Corpus (Kaggle 2021)
│       ├── download.sh             # Download script (run this first)
│       └── README.md               # Schema, fields, citation
├── annotation/
│   ├── guidelines.md               # Annotation guidelines + label definitions
│   ├── annotation_sample.csv       # 250-sentence IAA sample
│   ├── annotation_sample_result.csv
│   ├── create_sample.py
│   └── iaa_compute.py              # Fleiss Kappa computation script
├── analysis/
│   └── descriptive_stats.py        # Descriptive statistics + figures
│ 
└── experiments/
    ├── hypotheses.md               # Research questions and testable hypotheses
    ├── prompts/
    │   ├── zero_shot_lid.txt       # Zero-shot prompt template
    │   └── few_shot_lid.txt        # Few-shot prompt template (5 examples)
    ├── data/
    │   ├── sample_500.json         # Stratified evaluation sample (seed=42)
    |   ├── arabizi_eval_sample_seed42.json # 250 Arabizi sentences extracted separately
    |   ├── ar_en_cs_eval_sample_seed42.json #  250 AR-EN CS sentences extracted separately
    ├── scripts/
    │   ├── experiment_runner.ipynb  # Model-agnostic API runner (Colab)
    │   ├── evaluate.py             # Evaluation metrics script
    │   ├── compile_results.py      # Phase 4: comparison table builder
    │   └── error_analysis.py       # Phase 5: error taxonomy builder
    └── results/
        ├── o4-mini/                # GPT o4-mini outputs
        ├── claude-sonnet/          # Claude Sonnet 4.6 outputs
        ├── gemini-flash/           # Gemini 2.5 Flash outputs
        ├── llama-70b/              # LLaMA 3.3 70B outputs
        ├── comparison/             # Cross-model comparison tables
        └── error_analysis/         # Error taxonomy and case studies
```

## Datasets

| Dataset | Source | Sentences | Tokens | Script |
|---|---|---|---|---|
| Arabizi (WANLP 2022) | GitHub: HaifaCLG/Arabizi | 2,574 | 29,810 | `data/arabizi-wanlp/download.sh` |
| Arabic-English CS Corpus | Kaggle: islamkaloop | 2,507 | 30,321 | `data/arabic-english-cs/download.sh` |
| **Combined** | | **5,081** | **60,131** | |

**Important:** Raw dataset files are not committed to this repository. Run the download scripts to obtain them locally.

## Unified Label Scheme

| Label | Description | Example |
|---|---|---|
| AR | Arabic in Arabic script | مرحبا، كيف |
| EN | English in Latin script | hello, working |
| AR-LAT | Arabizi: Arabic in Latin script | marhaba, 7abibi |
| OTHER | Punctuation, digits, symbols | . , ! @ # |
| OL | Other language (e.g. French) | Oui, vraiment |

## Models Evaluated

| Model | Provider | API |
|---|---|---|
| GPT o4-mini | OpenAI | OpenAI API |
| Claude Sonnet 4.6 | Anthropic | Anthropic API |
| Gemini 2.5 Flash | Google | Google AI API |
| LLaMA 3.3 70B Instruct | Meta (open-source) | Together AI API |

All models were run with temperature=0.0, max_tokens=2048, on a 500-sentence stratified sample (seed=42).

## Setup

```bash
git clone https://github.com/abojoudah/cs496-codeswitching.git
cd cs496-codeswitching

# Download datasets
bash data/arabizi-wanlp/download.sh
bash data/arabic-english-cs/download.sh

# Install dependencies
pip install pandas numpy scikit-learn matplotlib seaborn nltk
```

## Running Experiments

### 1. Experiment Runner

Open `experiments/scripts/experiment_runner.ipynb` in Google Colab. Set your model name and API key in the config cell at the top, then run all cells. The notebook loads the 500-sentence sample, calls the API, and saves raw + parsed outputs to `experiments/results/`.

### 2. Evaluation

Run the evaluation script on any parsed output:

```bash
python3 experiments/scripts/evaluate.py \
  --parsed experiments/results/<model>/<model>_<strategy>_lid_parsed.json \
  --sample experiments/data/sample_500.json \
  --out experiments/results/<model>/ \
  --save-json
```

This produces per-model CSV files (overall metrics, per-label breakdown, confusion matrix) and an optional JSON metrics file.

### 3. Compile Comparison Tables

After all models have been evaluated:

```bash
python3 experiments/scripts/compile_results.py \
  --results-dir experiments/results \
  --sample experiments/data/sample_500.json
```

Outputs three comparison tables to `experiments/results/comparison/`.

### 4. Error Analysis

```bash
python3 experiments/scripts/error_analysis.py \
  --results-dir experiments/results \
  --sample experiments/data/sample_500.json \
  --out experiments/results/error_analysis
```

Outputs error taxonomy, contrastive examples, and representative error cases.

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
