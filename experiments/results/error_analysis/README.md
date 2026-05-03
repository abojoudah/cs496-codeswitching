# Error Taxonomy — Code-Switching LID

## Overview

Error analysis was conducted across all four models (GPT o4-mini, Claude Sonnet 4.6, Gemini 2.5 Flash, LLaMA 3.3 70B) on both zero-shot and few-shot runs (8 runs total). A total of **9,556 token-level errors** were identified.

## Key Finding

**75.4% of all errors are AR→AR-LAT** — models systematically mislabel Arabic-script tokens as Arabizi. This error is concentrated almost entirely in the AR-EN CS dataset (89.8% of that dataset's errors). The models appear to lack reliable script awareness, defaulting to AR-LAT when encountering Arabic tokens.

## Error Categories

| # | Category | Count | % of Errors | Severity | Description |
|---|----------|-------|-------------|----------|-------------|
| 1 | AR→AR-LAT | 7,209 | 75.4% | Severe | Arabic-script tokens mislabeled as Arabizi. Dominant in AR-EN CS dataset. |
| 2 | AR-LAT→EN | 885 | 9.3% | Severe | Arabizi tokens mislabeled as English. Short/ambiguous tokens like "la", "ana". |
| 3 | OTHER→EN | 345 | 3.6% | Mild | Punctuation/symbols labeled as English. |
| 4 | AR→EN | 229 | 2.4% | Severe | Arabic-script tokens labeled as English. |
| 5 | EN→OTHER | 208 | 2.2% | Mild | English words labeled as punctuation/symbols. |
| 6 | EN→AR-LAT | 137 | 1.4% | Severe | English tokens misidentified as Arabizi ("en", "an"). |
| 7 | EN→AR | 123 | 1.3% | Severe | English tokens labeled as Arabic. |
| 8 | OTHER→AR | 113 | 1.2% | Mild | Symbols labeled as Arabic. |
| 9 | OTHER→AR-LAT | 97 | 1.0% | Mild | Digits/symbols as Arabizi (e.g., "3" as phonetic ain). |
| 10 | OTHER→OL | 88 | 0.9% | Mild | Symbols labeled as other language. |

## Error Distribution by Dataset

### Arabizi Dataset (824 errors, zero-shot across 4 models)
- **AR-LAT→EN (55.8%)**: Dominant. Short Arabizi tokens resemble English words.
- **EN→OTHER (14.1%)**: English words misclassified as symbols.
- **OTHER→EN (9.0%)**: Symbols labeled as English.

### AR-EN CS Dataset (4,075 errors, zero-shot across 4 models)
- **AR→AR-LAT (89.8%)**: Overwhelming. Models cannot distinguish Arabic-script from Arabizi.
- **AR→EN (3.1%)**: Arabic tokens labeled as English.
- **OTHER→EN (2.4%)**: Symbols labeled as English.

## Parse Failures

| Model | Zero-shot | Few-shot | Change |
|-------|-----------|----------|--------|
| GPT o4-mini | 35 (7.0%) | 65 (13.0%) | +6.0% |
| Claude Sonnet | 46 (9.2%) | 42 (8.4%) | -0.8% |
| Gemini Flash | 38 (7.6%) | 38 (7.6%) | 0.0% |
| LLaMA 70B | 57 (11.4%) | 66 (13.2%) | +1.8% |

Few-shot prompting increases parse failures for GPT o4-mini (+6%) and LLaMA (+1.8%), likely due to longer prompts causing format compliance issues. Claude and Gemini remain stable.

## Error Severity

- **Severe**: Confusion between language labels (AR↔EN, AR-LAT↔EN, AR↔AR-LAT, OL↔EN)
- **Moderate**: Other language-to-language confusions
- **Mild**: Confusion involving OTHER (punctuation/symbols)

| Model | Strategy | Severe | Moderate | Mild |
|-------|----------|--------|----------|------|
| GPT o4-mini | Zero-shot | 1,058 | 7 | 118 |
| GPT o4-mini | Few-shot | 966 | 3 | 96 |
| Claude Sonnet | Zero-shot | 1,144 | 1 | 116 |
| Claude Sonnet | Few-shot | 1,150 | 1 | 116 |
| Gemini Flash | Zero-shot | 1,077 | 1 | 120 |
| Gemini Flash | Few-shot | 1,068 | 3 | 103 |
| LLaMA 70B | Zero-shot | 1,122 | 3 | 132 |
| LLaMA 70B | Few-shot | 1,017 | 5 | 129 |

The vast majority of errors are severe — direct language-label confusions, not boundary issues.

## Contrastive Examples (Zero-Shot)

116 tokens where at least one model was correct and another wrong. Key patterns:

| Token | Gold | o4-mini | Claude | Gemini | LLaMA | Insight |
|-------|------|---------|--------|--------|-------|---------|
| fl | AR-LAT | ✓ | ✓ | ✓ | EN ✗ | LLaMA misses short Arabizi |
| El | AR-LAT | OL ✗ | ✓ | ✓ | EN ✗ | o4-mini thinks French, LLaMA thinks English |
| ahmed | AR-LAT | EN ✗ | ✓ | ✓ | ✓ | o4-mini doesn't recognize Arabic names in Latin script |
| en | EN | AR-LAT ✗ | AR-LAT ✗ | AR-LAT ✗ | ✓ | Only LLaMA correctly identifies "en" as English |
| bravo | EN | ✓ | OL ✗ | OL ✗ | ✓ | Claude/Gemini detect Romance-language origin |
| Allah | AR-LAT | ✓ | EN ✗ | EN ✗ | EN ✗ | Only o4-mini recognizes transliterated religious term |
| brgr | AR-LAT | EN ✗ | EN ✗ | ✓ | EN ✗ | Only Gemini recognizes abbreviated Arabizi |

## Root Cause Analysis

1. **AR→AR-LAT dominance (75.4%)**: The prompt describes AR-LAT as "Arabic written in Latin script" and AR as "Arabic written in Arabic script." Despite this, models systematically assign AR-LAT to Arabic-script tokens in the AR-EN CS dataset. This suggests that LLMs process the semantic meaning of tokens (recognizing Arabic words) but fail to attend to script information (whether the token uses Arabic or Latin characters). This is the single most important finding.

2. **Short-token ambiguity**: Tokens like "la", "en", "an", "El" are genuinely ambiguous between Arabizi, English, and French. These drive AR-LAT↔EN and OL↔EN confusions in the Arabizi dataset.

3. **Borrowed/cross-linguistic words**: "MacChicken", "bravo", "Allah" — words with cross-linguistic usage are consistently misclassified because their language membership depends on context, not lexical form.

4. **Parse failures scale with prompt length**: Longer few-shot prompts degrade format compliance for GPT o4-mini and LLaMA, while Claude and Gemini handle the additional context without increased failures.

5. **No model dominates across all error types**: Each model has unique blind spots — o4-mini misses Arabic names, Claude/Gemini over-detect Romance languages, LLaMA struggles with short Arabizi tokens. This supports H4 (meaningful cross-model differences).
