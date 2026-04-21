# CS496 Code-Switching Project — Hypotheses

**Course:** CS496 — Kuwait University — Spring 2025/2026  
**Team:** Yousef Joudeh · Seyed Almadani · Abdulaziz Mohammed · Abdallah Almekhyal  
**GitHub:** https://github.com/abojoudah/cs496-codeswitching

---

## Definitions

- **LID** — Language Identification: detecting what language each token belongs to.
- **Arabizi** — Arabic written in Latin script, often using numerals as phonetic substitutes (e.g., 3 = ع, 7 = ح).
- **Semantic meaning** — The literal, dictionary-level meaning of a word or sentence.
- **Pragmatic meaning** — The contextual, cultural, or implied meaning behind a word or sentence.
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

## RQ2 — Machine Translation of Code-Switched Text

**Research Question:**  
How do LLMs preserve semantic and pragmatic meaning when translating Arabic-English code-switched text into fluent English?

### H1
> We hypothesize that translation quality, as measured by automatic metrics (BLEU, chrF++, BERTScore) and human evaluation, will be lower for Arabizi-based code-switched inputs than for Arabic-script code-switched inputs.

**Rationale:** Arabizi's non-standard spelling creates ambiguity that disrupts both tokenization and meaning recovery during translation.

**Maps to:** Table 3 — Per-Dataset Comparison (Arabizi dataset vs AR-EN CS dataset, translation metrics).

---

### H2
> We hypothesize that few-shot prompting will produce higher translation quality scores than zero-shot prompting for Arabic-English code-switched translation.

**Rationale:** Few-shot examples demonstrate the expected output style and help the model handle code-switched input more consistently.

**Maps to:** Table 1 — Overall Results (Zero-Shot vs Few-Shot rows, translation metric columns).

---

### H3
> We hypothesize that human evaluation ratings for semantic preservation will exceed those for pragmatic preservation across all models tested.

**Rationale:** Literal meaning is easier to recover from surface forms than culturally implied meaning. For example, "khalas" can be translated literally as "finished" but pragmatically signals exhaustion or frustration — a distinction models are unlikely to capture consistently.

**Maps to:** Human Evaluation Table — Semantic score vs Pragmatic score per model.

---

## RQ3 — Cross-Task and Cross-Model Comparison

**Research Question:**  
Which LLM(s) demonstrate superior performance on Arabic-English code-switching tasks, and is there evidence of task-specific specialization (LID vs translation) across models?

### H1
> We hypothesize that no single LLM will achieve the highest ranking on both token-level LID and translation tasks simultaneously, indicating task-specific specialization.

**Rationale:** LID requires strict format compliance and fine-grained label accuracy. Translation rewards fluency and semantic coverage. These objectives may favor different model architectures or training emphases.

**Maps to:** Combined summary table — Model rankings on LID (macro F1) vs MT (BLEU/BERTScore) side by side.

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
| RQ2 H1 | BLEU / chrF++ / BERTScore by dataset | Table 3 — Per-Dataset Comparison |
| RQ2 H2 | Translation metrics: few-shot vs zero-shot | Table 1 — Overall Results |
| RQ2 H3 | Human eval: semantic score vs pragmatic score | Human Evaluation Table |
| RQ3 H1 | LID rank vs MT rank per model | Summary Ranking Table |
| RQ3 H2 | AR F1 rank vs AR-LAT F1 rank per model | Table 2 — Per-Label F1 |
