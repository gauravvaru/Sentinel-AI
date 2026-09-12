# Hinglish TF-IDF + LogReg Baseline Report

**Timestamp:** 2026-09-11T17:45:22.503878Z
**Python Version:** 3.13.7
**scikit-learn Version:** 1.9.1

## Dataset
- **Train Size:** 14091
- **Validation Size:** 1567
### Train Distribution
- 0 (Negative): 4083
- 1 (Neutral): 5310
- 2 (Positive): 4698
### Validation Distribution
- 0 (Negative): 454
- 1 (Neutral): 591
- 2 (Positive): 522

## Configuration
**TF-IDF:**
- N-gram range: (1, 2)
- sublinear_tf: True
- min_df: 2
- max_df: 0.95
**Logistic Regression:**
- max_iter: 2000
- random_state: 42

## Results
- **Macro F1 (Primary Metric):** 0.6641
- **Accuracy:** 0.6605
- **Weighted F1:** 0.6602

### Per-Class Metrics
**0 (Negative):**
- Precision: 0.6775 | Recall: 0.6894 | F1: 0.6834
**1 (Neutral):**
- Precision: 0.5997 | Recall: 0.5905 | F1: 0.5951
**2 (Positive):**
- Precision: 0.7132 | Recall: 0.7146 | F1: 0.7139

### Confusion Matrix
```
[313, 116, 25]
[117, 349, 125]
[32, 117, 373]
```
