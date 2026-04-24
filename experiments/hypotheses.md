# CS496 Code-Switching Project — Hypotheses

**Course:** CS496 — Kuwait University — Spring 2025/2026  
**Team:** Yousef Joudeh · Seyed Almadani · Abdulaziz Mohammed · Abdallah Almekhyal  
**GitHub:** https://github.com/abojoudah/cs496-codeswitching

---

## Definitions

- **LID** — Language Identification: detecting what language each token belongs to.
- **Arabizi** — Arabic written in Latin script, often using numerals as phonetic substitutes (e.g., 3 = ع, 7 = ح).
- **Macro F1** — The unweighted average F1-score across all labels; treats rare labels equally to common ones.

---

## RQ1 — Token-Level Language Identification

**Research Question:**  
To what extent can LLMs accurately perform token-level language identification on Arabic-English code-switched text, and how does performance vary across different switching patterns?

### H1
> We hypothesize that token-level LID performance, as measured by macro F1-score, will be significantly lower on Arabizi-based code-switched text (AR-LAT tokens) compared to Arabic-script code-switched text (AR tokens).

**Rationale:** Arabizi has no standard spelling and is heavily underrepresented in LLM pretraining data. Models trained primarily on Arabic-script and English text are expected to struggle with Latin-script Arabic.

**Maps to:** Table 2 — Per-Label F1 Breakdown (AR-LAT column vs AR column, across all models and strategies).

---

### H2
> We hypothesize that few-shot prompting will yield higher macro F1-scores than zero-shot prompting for token-level language identification across all models tested.

**Rationale:** Providing labeled examples in the prompt reduces ambiguity in the output format and helps the model understand edge cases such as AR-LAT vs EN short tokens.

**Maps to:** Table 1 — Overall Results (Zero-Shot vs Few-Shot rows for each model).

---

### H3
> We hypothesize that all models will perform significantly worse on AR-LAT (Arabizi) tokens than on AR or EN tokens.

**Rationale:** Arabizi is non-standardized, uses numeral substitutions, and is underrepresented in training data. AR and EN are well-established scripts with abundant training resources.

**Maps to:** Table 2 — Per-Label F1 Breakdown (AR-LAT F1 vs AR F1 and EN F1, across all models).

---

### H4
> We hypothesize that models will perform differently on the Arabizi dataset (English-dominant, Latin-script mixing) compared to the AR-EN CS dataset (Arabic-dominant, script-based mixing).

**Rationale:** The two datasets have different code-switching densities and dominant languages. Models may handle one pattern better than the other depending on their pretraining distribution.

**Maps to:** Table 3 — Per-Dataset Comparison (Arabizi dataset vs AR-EN CS dataset, same metrics split by dataset).

---

## RQ2 — Cross-Model Comparison

**Research Question:**  
Which LLM(s) demonstrate superior performance on Arabic-English code-switched language identification, and is there a statistically meaningful difference across models?

### H1
> We hypothesize that among the four models tested, there is a statistically meaningful difference in overall token-level macro F1 for code-switched language identification.

**Rationale:** Different models have different pretraining data, tokenizers, and multilingual capabilities. These differences should produce measurably different LID performance.

**Maps to:** Table 1 — Overall Results (compare macro F1 across all 4 models).

---

### H2
> We hypothesize that the best-performing model on Arabic-script (AR) inputs will also be the best-performing model on Arabizi (AR-LAT) inputs, suggesting that general multilingual capability drives performance on both.

**Rationale:** If Arabic-script performance and Arabizi performance are correlated, this suggests the underlying capability is general language robustness rather than script-specific training.

**Maps to:** Table 2 — Per-Label F1 Breakdown (AR column vs AR-LAT column; check if model rankings are consistent).

---

## Hypothesis-to-Table Mapping Summary

| Hypothesis | Key Metric | Results Table |
|---|---|---|
| RQ1 H1 | AR-LAT F1 vs AR F1 | Table 2 — Per-Label F1 |
| RQ1 H2 | Macro F1: few-shot vs zero-shot | Table 1 — Overall Results |
| RQ1 H3 | AR-LAT F1 vs AR F1 and EN F1 | Table 2 — Per-Label F1 |
| RQ1 H4 | Metrics split by dataset | Table 3 — Per-Dataset Comparison |
| RQ2 H1 | Macro F1 across all models | Table 1 — Overall Results |
| RQ2 H2 | AR F1 rank vs AR-LAT F1 rank | Table 2 — Per-Label F1 |
