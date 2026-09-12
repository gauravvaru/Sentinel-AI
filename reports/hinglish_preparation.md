# Hinglish Dataset Preparation Report

- **Source Row Count:** 17594
- **Cleaned Row Count:** 15658
- **Missing Text Rows Quarantined:** 26
- **Quarantined Rows (Total):** 300

## Duplicates
- **Duplicate Groups:** 1682
- **Same-Label Duplicate Groups:** 1569
- **Conflicting-Label Groups:** 113

## Final Splits
- **Random Seed:** 42
- **Train Count:** 14091
- **Validation Count:** 1567
- **Train/Validation Overlap:** 0

### Train Class Distribution
- 0 (Negative): 4083
- 1 (Neutral): 5310
- 2 (Positive): 4698

### Validation Class Distribution
- 0 (Negative): 454
- 1 (Neutral): 591
- 2 (Positive): 522

## Preprocessing Decisions
- Missing text rows are quarantined.
- Text-level deduplication is applied.
- Identical texts with the same label are merged into a single canonical row.
- Identical texts with conflicting labels are entirely quarantined.
- Stratified split by label ensures balanced distributions.
- Test set is left completely untouched.