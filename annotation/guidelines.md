# Annotation Guidelines — Token-Level Language Identification

**Project:** CS496 — Code-Switching Handling in Arabic-English Tasks  
**Task:** Word-level Language Identification (LID) for Arabic-English code-switched text  
**Version:** 1.0  
**Annotators:** 3 (you + 2 teammates)

---

## 1. Overview

Each token (word) in a sentence must be assigned exactly one language label from the tagset below. Annotation is performed at the **word level**, not the sentence level. Every token gets one and only one label.

The goal is to identify the language of each token as it appears in the text, based on its **script, morphology, and lexical identity** — not its meaning or context.

---

## 2. Label Set

| Label | Full Name | Description |
|---|---|---|
| `AR` | Arabic | Token in Arabic script belonging to Arabic (MSA or any dialect) |
| `EN` | English | Token in Latin script belonging to English |
| `AR-LAT` | Arabizi | Token in Latin script that represents spoken Arabic (transliteration) |
| `MIX` | Mixed | Single token with morphemes from two languages (intra-word switching) |
| `OL` | Other Language | Any language other than Arabic and English (French, etc.) |
| `OTHER` | Other | Punctuation, digits, URLs, hashtags, emoticons, usernames |

---

## 3. Label Definitions and Examples

### AR — Arabic
Any token written in the Arabic script that belongs to Arabic, regardless of dialect (Modern Standard Arabic, Egyptian, Levantine, Gulf, etc.).

| Token | Label | Reason |
|---|---|---|
| مرحبا | AR | Arabic greeting, Arabic script |
| كيف | AR | Arabic question word |
| بحب | AR | Egyptian Arabic "I love", Arabic script |
| إنت | AR | Levantine "you", Arabic script |

### EN — English
Any token written in the Latin script that is an English word (not a transliteration of Arabic).

| Token | Label | Reason |
|---|---|---|
| hello | EN | English greeting |
| working | EN | English verb |
| honestly | EN | English adverb |
| the | EN | English article |

### AR-LAT — Arabizi
A token written in the Latin script that represents an Arabic word or morpheme. Arabizi uses numbers as letter substitutes (3=ع, 7=ح, 2=ء).

| Token | Label | Reason |
|---|---|---|
| marhaba | AR-LAT | Arabizi spelling of مرحبا |
| kif | AR-LAT | Arabizi spelling of كيف (how) |
| 3arabi | AR-LAT | Arabizi for عربي (Arabic) |
| 7abibi | AR-LAT | Arabizi for حبيبي (my love) |
| sho | AR-LAT | Arabizi for شو (what, Levantine) |
| yalla | AR-LAT | Arabizi for يلا (let's go) |

**Key distinction from EN:** If a word looks like it could be English but is used as an Arabic transliteration in context, label it AR-LAT. When in doubt, check if the word has an obvious Arabic counterpart.

### MIX — Intra-word code-switching
A single token that contains morphemes from two different languages fused together. This is the rarest category.

| Token | Label | Reason |
|---|---|---|
| bi-working | MIX | Arabic prefix بـ (bi-) + English stem "working" |
| ma-understand-sh | MIX | Arabic negation frame + English verb |
| el-meeting | MIX | Arabic definite article ال (el-) + English noun |
| 7abib-i | MIX | Arabizi stem + Arabic suffix if merged as one token |

**Note:** Only label MIX if the mixing occurs **within a single token** (no space). If the Arabic and English parts are separate tokens, label each one individually.

### OTHER — Non-linguistic tokens
Punctuation, numbers, symbols, URLs, usernames, hashtags, emoticons.

| Token | Label | Reason |
|---|---|---|
| . , ! ? | OTHER | Punctuation |
| @username | OTHER | Mention |
| #arabic | OTHER | Hashtag |
| http://... | OTHER | URL |
| 3, 100, 2024 | OTHER | Digits (unless part of Arabizi like 3arabi — then AR-LAT) |
| :) ❤ | OTHER | Emoticons |

**Important exception:** Numbers used as Arabizi letter substitutes within a word (e.g. 3arabi, 7abibi) are part of AR-LAT tokens, not OTHER.

---

## 4. Edge Cases and Decision Rules

### 4.1 Loanwords
Words borrowed from English into Arabic and used as Arabic words (e.g. "mobile", "internet", "computer") should be labeled **AR** if written in Arabic script, or **EN** if written in Latin script — do not label them AR-LAT.

| Token | Label | Reason |
|---|---|---|
| موبايل | AR | Loanword in Arabic script |
| mobile | EN | Same word but in Latin script, used as English |
| internet | EN | Widely borrowed but used in English form |

### 4.2 Named entities (people, places, brands)
Label by script. Arabic-script names → AR. Latin-script names → EN.

| Token | Label | Reason |
|---|---|---|
| محمد | AR | Arabic name in Arabic script |
| Mohamed | EN | Same name in Latin script |
| Kuwait | EN | Place name in Latin script |
| الكويت | AR | Same place in Arabic script |

### 4.3 Ambiguous Arabizi vs. English
If a token could be either English or Arabizi, look at:
1. Surrounding tokens: if the sentence is primarily Arabizi, prefer AR-LAT.
2. Phonological plausibility: does it sound like an Arabic word when read?
3. Numbers: presence of 2, 3, 5, 6, 7, 8, 9 as letters strongly indicates Arabizi.

| Token | Context | Label | Reason |
|---|---|---|---|
| ana | "ana mabsoot" | AR-LAT | أنا in Arabizi |
| ana | "ana conda environment" | EN | English tech term |

### 4.4 Repeated characters for emphasis
"hahahaha", "lolll", "wowwww" → **EN**  
"hhhhhh" → **AR-LAT** (Arabic laughter marker ههههه written in Latin)

---

## 5. Annotation Process for IAA

1. All three annotators receive the **same sample of 250 sentences** from the combined dataset.
2. Each annotator works **independently** — do not discuss labels during annotation.
3. Use the provided `annotation_sample.csv` file and add your labels in your assigned column (`annotator_1`, `annotator_2`, `annotator_3`).
4. After all three are done, run `iaa_compute.py` to compute Fleiss' Kappa.
5. Disagreements on more than 10% of tokens should trigger a discussion and guidelines revision.

---

## 6. Annotation File Format

The shared annotation file is `annotation_sample.csv` with the following columns:

```
sentence_id, token_id, token, annotator_1, annotator_2, annotator_3
1, 1, مرحبا, AR, AR, AR
1, 2, how, EN, EN, EN
1, 3, are, EN, EN, EN
1, 4, u, AR-LAT, EN, AR-LAT
```

Fill in only your assigned annotator column. Leave other columns blank — they will be filled by your teammates.

---

## 7. Quality Thresholds

| Metric | Acceptable | Good | Excellent |
|---|---|---|---|
| Fleiss' Kappa (κ) | 0.61–0.80 | 0.80–0.90 | > 0.90 |

A κ below 0.60 indicates substantial disagreement and requires guideline revision before proceeding.

---

## 8. Reference

These guidelines are adapted from:
- Shehadi & Wintner (2022) — Arabizi annotation scheme
- Solorio & Liu (2008) — foundational code-switching annotation principles
- LinCE benchmark (Aguilar et al., 2020) — LID tagset conventions
