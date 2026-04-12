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

## Original Label Definitions

The numeric categories are defined in the original authors' source code (`main.py`, line 21):

```python
categ_names = ['Arabizi', 'English', 'French ', 'Arabic ','Shared', 'Other  ']
```

| categ | Original Name | Description |
|---|---|---|
| 0 | Arabizi | Arabic words written in Latin script |
| 1 | English | English tokens |
| 2 | French | French tokens |
| 3 | Arabic | Arabic tokens in Arabic script |
| 4 | Shared | Cross-linguistic words of Arabic origin in Latin script (e.g. Mashallah, allah, inshallah) |
| 5 | Other | Punctuation, digits, symbols, URLs |

## Label Mapping to Our Unified Scheme

We map the original six numeric categories to our unified 6-label scheme:

| categ | Original Name | Our Label | Rationale |
|---|---|---|---|
| 0 | Arabizi | AR-LAT | Arabic words in Latin script |
| 1 | English | EN | Direct match |
| 2 | French | OL | Other language |
| 3 | Arabic | AR | Direct match |
| 4 | Shared | AR-LAT | Arabic-origin words in Latin script (e.g. Mashallah, allah) |
| 5 | Other | OTHER | Direct match |

**Note on Shared tokens (categ 4):** These 1,402 tokens are words of Arabic origin written in Latin script that are widely used across languages. Since they are Arabic words rendered in Latin script, we map them to AR-LAT alongside the core Arabizi tokens (categ 0).

## Dataset Statistics

All numbers verified against the actual data file.

### Overall

| Metric | Value |
|---|---|
| Total sentences | 2,574 |
| Total tokens | 29,810 |
| Avg tokens per sentence | 11.6 |
| Max tokens per sentence | 166 |
| Min tokens per sentence | 1 |
| Code-switched sentences | 335 (13.0%) |

### Original Label Distribution (before mapping)

| categ | Original Name | Count | Percentage |
|---|---|---|---|
| 1 | English | 16,564 | 55.6% |
| 0 | Arabizi | 4,862 | 16.3% |
| 5 | Other | 4,162 | 14.0% |
| 3 | Arabic | 2,671 | 9.0% |
| 4 | Shared | 1,402 | 4.7% |
| 2 | French | 149 | 0.5% |

### Mapped Label Distribution (after mapping)

| Our Label | Count | Percentage |
|---|---|---|
| EN | 16,564 | 55.6% |
| AR-LAT | 6,264 | 21.0% |
| OTHER | 4,162 | 14.0% |
| AR | 2,671 | 9.0% |
| OL | 149 | 0.5% |

### Source Breakdown

| Platform | Tokens | Percentage |
|---|---|---|
| Twitter | 16,058 | 53.9% |
| Reddit | 13,752 | 46.1% |

## Observed Biases

- **English-dominant:** 55.6% of tokens are English — most posts switch heavily into English
- **Low Arabic-script content:** only 9.0% AR tokens in Arabic script — users prefer Arabizi over Arabic script
- **Sparse code-switching:** only 13% of sentences contain actual code-switching
- **French presence:** 0.5% OL tokens (French) — mainly from North African users (Algerian, Moroccan, Tunisian)
- **Shared token ambiguity:** 4.7% of tokens are cross-linguistic words (Mashallah, allah, etc.) mapped to AR-LAT, which may introduce ambiguity at the boundary between Arabizi and language-neutral words
- **Informal register only:** all data from social media — no formal or written Arabic
- **Label noise:** original annotations contain inconsistencies (e.g. Arabic-script tokens labeled as Arabizi, French tokens labeled as Arabic) — this motivated our independent re-annotation

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
