# Analysis — Task 4

This folder contains the statistical analysis scripts and outputs for Task 4 (Analysis and Discussion).

## Files

| File | Description |
|------|-------------|
| `significance_tests.py` | Main analysis script: gold-label correction, McNemar's tests, error taxonomy |
| `corrected_evaluation.csv` | Accuracy and macro F1 for all runs under original and corrected gold labels |
| `significance_results.csv` | McNemar's test p-values for all comparisons (ZS vs FS, pairwise models, ablation) |
| `error_taxonomy.csv` | Error category frequencies after gold-label correction |

## How to Run

```bash
cd analysis/
pip install scipy
python significance_tests.py
```

The script reads from `../experiments/results/` and `../experiments/data/sample_500.json`, and writes CSV outputs to this folder.

## Gold-Label Correction

During extended error analysis, we discovered that 55.1% of AR-labeled tokens in the AR-EN CS dataset are actually written in Latin script (Arabizi). The original corpus labeled by language identity, but our unified scheme defines AR as "Arabic in Arabic script." The correction relabels these Latin-script AR tokens as AR-LAT before evaluation. See Section III of the paper for details.

## McNemar's Test

McNemar's test (with continuity correction) is used for all significance comparisons. It is appropriate for paired nominal classification data where the same tokens are labeled by two systems. Significance levels: *** p<0.001, ** p<0.01, * p<0.05, ns = not significant.
