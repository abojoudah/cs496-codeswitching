# Arabic-English Code Switching Corpus (Kaggle 2021)

## Source
- **Title:** Language Identification of Intra-Word Code-Switching for Arabic-English Corpus
- **Creator:** Islam Kaloop (2021)
- **URL:** https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus
- **File:** AR-EN Intra-word CS Corpus.txt

## Download
Run `bash download.sh` from this directory. Requires Kaggle CLI and API key.

## Dataset Description
The corpus was collected from three social media platforms using different collection methods. It is the first annotated AR-EN dataset for intra-word code-switching language identification. Tokens are annotated with language tags reflecting how users informally mix Arabic and English on social media.

## Source Breakdown

| Platform | Tokens | Percentage |
|---|---|---|
| WhatsApp | 13,040 | 43.0% |
| Facebook | 8,692 | 28.7% |
| Twitter (Tweepy API) | 8,589 | 28.3% |
| **Total** | **30,321** | **100%** |

## Schema
The corpus is a plain-text file in CoNLL-style format — one token per line, blank lines separate sentences.

| Column | Description |
|---|---|
| Token | The word in its original script (Arabic or Latin) |
| Language tag | Token-level language ID label |

## Label Definitions

| Label | Meaning | Example |
|---|---|---|
| `AR` | Arabic token in Arabic script | كيف |
| `EN` | English token in Latin script | how |
| `MIX` | Intra-word code-switching | bi-working |
| `OTHER` | Punctuation, digits, symbols | ، . 5 |
| `NE.AR` | Named entity in Arabic script | محمد |
| `NE.EN` | Named entity in Latin script | Mohamed |
| `AMBIG` | Ambiguous token | — |
| `LANG3` | Third language token | — |

## Label Mapping to Our Unified Scheme
For our experiments we map the original labels to our 6-label scheme:

| Original | Our Label |
|---|---|
| AR | AR |
| EN | EN |
| MIX | MIX |
| OTHER | OTHER |
| NE.AR | AR |
| NE.EN | EN |
| AMBIG | OTHER |
| LANG3 | OL |

## Statistics
- Total sentences: 2,507
- Total tokens: 30,321
- Avg tokens per sentence: 12.1
- Max tokens per sentence: 203
- Min tokens per sentence: 1

## Label Distribution

| Label | Count | Percentage |
|---|---|---|
| AR | 19,061 | 62.9% |
| EN | 6,833 | 22.5% |
| OTHER | 3,794 | 12.5% |
| NE.AR | 317 | 1.0% |
| NE.EN | 250 | 0.8% |
| AMBIG | 55 | 0.2% |
| LANG3 | 11 | 0.0% |

## Observed Biases
- Heavily Arabic-dominant (62.9% AR vs 22.5% EN)
- WhatsApp data dominates (43%) — likely more formal register than Twitter
- No dialect labels — Arabic variety is unspecified
- Named entities (NE.AR/NE.EN) comprise 1.8% of tokens

## Relevance to This Project
This corpus captures structured Arabic-English code-switching including intra-word mixing (e.g. Arabic morphological prefixes attached to English stems). Combined with the Arabizi WANLP dataset it covers the full spectrum of Arabic-English code-switching phenomena studied in this thesis.

## Citation
```
Islam Kaloop (2021). Arabic-English Intra-word Code Switching Corpus.
Kaggle. https://www.kaggle.com/datasets/islamkaloop/arabic-english-intra-word-code-switching-corpus
```
