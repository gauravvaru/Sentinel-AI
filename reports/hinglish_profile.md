# Hinglish Dataset Profile Report

## Train Set
- **Row Count:** 14594
- **Malformed Rows:** 0

### Data Quality
- Missing IDs: 0
- Missing Texts: 25
- Missing Labels: 0
- Whitespace Only Texts: 0
- Duplicate IDs: 0
- Duplicate Texts: 320

### Label Distribution
- 0_negative: 4252 (29.14%)
- 1_neutral: 5473 (37.50%)
- 2_positive: 4869 (33.36%)
- Invalid Labels Count: 0

### Text Statistics (Length)
- Min: 1
- Max: 504
- Mean: 77.63
- Median: 81.0

### Noise Characteristics
- Contain URLs: 0
- Contain Mentions: 0
- Contain Hashtags: 0
- Non-ASCII Character %: 0.99%

## Valid Set
- **Row Count:** 3000
- **Malformed Rows:** 0

### Data Quality
- Missing IDs: 0
- Missing Texts: 1
- Missing Labels: 0
- Whitespace Only Texts: 0
- Duplicate IDs: 0
- Duplicate Texts: 13

### Label Distribution
- 0_negative: 890 (29.67%)
- 1_neutral: 1128 (37.60%)
- 2_positive: 982 (32.73%)
- Invalid Labels Count: 0

### Text Statistics (Length)
- Min: 2
- Max: 133
- Mean: 76.17
- Median: 80.0

### Noise Characteristics
- Contain URLs: 0
- Contain Mentions: 0
- Contain Hashtags: 0
- Non-ASCII Character %: 1.03%

## Test Set
- **Row Count:** 3000
- **Malformed Rows:** 0

### Data Quality
- Missing IDs: 0
- Missing Texts: 3
- Whitespace Only Texts: 0
- Duplicate IDs: 0
- Duplicate Texts: 13

### Text Statistics (Length)
- Min: 3
- Max: 167
- Mean: 74.57
- Median: 78.0

### Noise Characteristics
- Contain URLs: 0
- Contain Mentions: 0
- Contain Hashtags: 0
- Non-ASCII Character %: 0.12%

## Train/Validation Leakage
- Exact Text Overlap: 1447 rows