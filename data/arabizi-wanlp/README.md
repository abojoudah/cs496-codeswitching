# Arabizi Dataset (WANLP 2022)

## Source

| Field | Details |
|---|---|
| Paper | Shehadi & Wintner (2022). "Identifying Code-switching in Arabizi." |
| Venue | Seventh Arabic NLP Workshop (WANLP) @ ACL 2022 |
| GitHub | https://github.com/HaifaCLG/Arabizi |
| ACL Anthology | https://aclanthology.org/2022.wanlp-1.18 |

## Download

```bash
bash download.sh
```

Requires `git`. Clones the original repository and copies only the data files into this folder. Raw files are excluded from GitHub by `.gitignore`.

## Files

| File | Size | Description |
|---|---|---|
| `words_annotated.csv` | 1.1 MB | Word-level language ID annotations — primary file |
| `sen_annotated.csv` | 253 KB | Sentence-level annotations |
| `arabizi-reddit_new.zip` | 13 MB | Raw Reddit posts in Arabizi |
| `arabizi_tweet_ids_auto.csv` | 14 MB | Tweet IDs only (no raw text — Twitter ToS compliant) |

## Schema — words_annotated.csv

| Column | Type | Description |
|---|---|---|
| `source` | string | Platform: `reddit` or `twitter` |
| `user_name` | int | Anonymized user ID |
| `sen_id` | string | Unique sentence identifier |
| `sen_num` | int | Sentence number within user |
| `token` | string | Word in original script |
| `categ` | int | Original language ID category (see mapping below) |

## Label Mapping

Original dataset uses numeric categories. We map them to our unified 6-label scheme:

| categ | Our Label | Meaning | Example |
|---|---|---|---|
| 1 | EN | English in Latin script | hello, working |
| 2 | AR | Arabic in Arabic script | مرحبا، كيف |
| 3 | AR-LAT | Arabizi — Arabic in Latin script | marhaba, 7abibi, yalla |
| 4 | OL | Other language (mainly French) | Oui, vraiment, merci |
| 5 | OTHER | Punctuation, digits, symbols, URLs | . , ! @ # |

## Dataset Statistics

All numbers verified against the actual data file using `analysis/descriptive_stats.py`.

### Overall

| Metric | Value |
|---|---|
| Total sentences | 2,574 |
| Total tokens | 29,810 |
| Avg tokens per sentence | 11.6 |
| Max tokens per sentence | 166 |
| Min tokens per sentence | 1 |
| Code-switched sentences | 335 (13.0%) |

### Label Distribution

| Label | Count | Percentage |
|---|---|---|
| EN | 16,564 | 55.6% |
| OTHER | 4,162 | 14.0% |
| AR-LAT | 2,671 | 9.0% |
| OL | 1,402 | 4.7% |
| AR | 149 | 0.5% |

### Source Breakdown

| Platform | Tokens | Percentage |
|---|---|---|
| Twitter | 16,058 | 53.9% |
| Reddit | 13,752 | 46.1% |

## Observed Biases

- **English-dominant:** 55.6% of tokens are English — most posts switch heavily into English
- **Low Arabic-script content:** only 0.5% AR tokens — users prefer Arabizi over Arabic script
- **Sparse code-switching:** only 13% of sentences contain actual code-switching
- **French presence:** 4.7% OL tokens — mainly North African users (Algerian, Moroccan, Tunisian)
- **Informal register only:** all data from social media — no formal or written Arabic
- **Label noise:** original annotations contain inconsistencies (e.g. Arabic-script tokens labeled as AR-LAT, French tokens labeled as AR) — this motivated our independent re-annotation

## Relevance to This Project

This dataset is the primary resource for studying Arabizi — Arabic written in Latin script — which is the dominant form of informal Arabic-English code-switching on social media. It provides word-level labels needed for our language identification benchmarking task. The dataset was used to generate our 250-sentence IAA annotation sample (see `annotation/`).

## Citation

```bibtex
@inproceedings{shehadi-wintner-2022-identifying,
  title     = "Identifying Code-switching in {A}rabizi",
  author    = "Shehadi, Safaa and Wintner, Shuly",
  booktitle = "Proceedings of the Seventh Arabic NLP Workshop (WANLP)",
  month     = dec,
  year      = "2022",
  address   = "Abu Dhabi, United Arab Emirates",
  publisher = "Association for Computational Linguistics",
  url       = "https://aclanthology.org/2022.wanlp-1.18",
  pages     = "194--204"
}
```
