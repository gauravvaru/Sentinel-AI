import json
import re
from pathlib import Path
from typing import Dict, Any, List

# Constants
DATA_DIR = Path("data/raw/Hinglish")
TRAIN_FILE = DATA_DIR / "FinalTrainingOnly.tsv"
VALID_FILE = DATA_DIR / "ValidationOnly.tsv"
TEST_FILE = DATA_DIR / "FinalTest.tsv"

REPORTS_DIR = Path("reports")
JSON_REPORT_FILE = REPORTS_DIR / "hinglish_profile.json"
MD_REPORT_FILE = REPORTS_DIR / "hinglish_profile.md"

def get_percentile(data: List[int], p: float) -> float:
    if not data:
        return 0.0
    k = (len(data) - 1) * p
    f = int(k)
    c = min(f + 1, len(data) - 1)
    if f == c:
        return float(data[f])
    return float(data[f] * (c - k) + data[c] * (k - f))

def load_data(filepath: Path, is_test: bool = False) -> tuple[List[Dict[str, str]], int]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        data = []
        malformed = 0
        for line in lines:
            parts = line.strip('\n').split('\t')
            if not is_test:
                if len(parts) == 3:
                    data.append({"id": parts[0], "text": parts[1], "label": parts[2]})
                else:
                    malformed += 1
            else:
                if len(parts) >= 2:
                    data.append({"id": parts[0], "text": parts[1]})
                else:
                    malformed += 1

        return data, malformed
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return [], 0


def analyze_dataset(data: List[Dict[str, str]], malformed_count: int, is_test: bool = False) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}
    stats["row_count"] = len(data)
    stats["malformed_rows"] = malformed_count
    
    if not data:
        return stats

    missing_ids = 0
    missing_texts = 0
    missing_labels = 0
    whitespace_only = 0
    
    id_counts = {}
    text_counts = {}
    
    lengths = []
    
    url_count = 0
    mention_count = 0
    hashtag_count = 0
    non_ascii_chars = 0
    total_chars = 0
    
    label_dist = {"0": 0, "1": 0, "2": 0}
    invalid_labels = []
    
    for row in data:
        # ID check
        r_id = row.get("id", "")
        if not r_id:
            missing_ids += 1
        else:
            id_counts[r_id] = id_counts.get(r_id, 0) + 1
            
        # Text check
        text = row.get("text", "")
        if not text:
            missing_texts += 1
        elif text.strip() == "":
            whitespace_only += 1
            
        if text:
            text_counts[text] = text_counts.get(text, 0) + 1
            lengths.append(len(text))
            
            # Noise characteristics
            if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
                url_count += 1
            if re.search(r'@\w+', text):
                mention_count += 1
            if re.search(r'#\w+', text):
                hashtag_count += 1
                
            non_ascii = sum(1 for c in text if ord(c) > 127)
            non_ascii_chars += non_ascii
            total_chars += len(text)
            
        # Label check
        if not is_test:
            label = row.get("label", "")
            if not label:
                missing_labels += 1
            elif label in ["0", "1", "2"]:
                label_dist[label] += 1
            else:
                invalid_labels.append(label)

    # Compile stats
    stats["missing_ids"] = missing_ids
    stats["missing_texts"] = missing_texts
    stats["whitespace_only_texts"] = whitespace_only
    stats["duplicate_ids"] = sum(1 for v in id_counts.values() if v > 1)
    stats["duplicate_texts"] = sum(1 for v in text_counts.values() if v > 1)
    
    lengths.sort()
    if lengths:
        stats["text_statistics"] = {
            "min": lengths[0],
            "max": lengths[-1],
            "mean": sum(lengths) / len(lengths),
            "median": get_percentile(lengths, 0.5),
            "p25": get_percentile(lengths, 0.25),
            "p75": get_percentile(lengths, 0.75),
            "p95": get_percentile(lengths, 0.95)
        }
    else:
        stats["text_statistics"] = {}
        
    stats["noise_characteristics"] = {
        "url_count": url_count,
        "mention_count": mention_count,
        "hashtag_count": hashtag_count,
        "non_ascii_percentage": (non_ascii_chars / total_chars * 100) if total_chars > 0 else 0.0
    }
    
    if not is_test:
        stats["missing_labels"] = missing_labels
        
        total_valid_labels = sum(label_dist.values())
        stats["label_distribution"] = {
            "0_negative": {"count": label_dist["0"], "percentage": (label_dist["0"] / total_valid_labels * 100) if total_valid_labels > 0 else 0},
            "1_neutral": {"count": label_dist["1"], "percentage": (label_dist["1"] / total_valid_labels * 100) if total_valid_labels > 0 else 0},
            "2_positive": {"count": label_dist["2"], "percentage": (label_dist["2"] / total_valid_labels * 100) if total_valid_labels > 0 else 0}
        }
        stats["invalid_labels_count"] = len(invalid_labels)
        stats["invalid_labels_examples"] = invalid_labels[:5]
        
    return stats


def generate_markdown_report(report: Dict[str, Any], filepath: Path):
    lines = []
    lines.append("# Hinglish Dataset Profile Report")
    lines.append("")
    
    for split in ["train", "valid", "test"]:
        if split not in report:
            continue
            
        data = report[split]
        lines.append(f"## {split.capitalize()} Set")
        lines.append(f"- **Row Count:** {data.get('row_count', 0)}")
        lines.append(f"- **Malformed Rows:** {data.get('malformed_rows', 0)}")
        
        lines.append("\n### Data Quality")
        lines.append(f"- Missing IDs: {data.get('missing_ids', 0)}")
        lines.append(f"- Missing Texts: {data.get('missing_texts', 0)}")
        if split != "test":
            lines.append(f"- Missing Labels: {data.get('missing_labels', 0)}")
        lines.append(f"- Whitespace Only Texts: {data.get('whitespace_only_texts', 0)}")
        lines.append(f"- Duplicate IDs: {data.get('duplicate_ids', 0)}")
        lines.append(f"- Duplicate Texts: {data.get('duplicate_texts', 0)}")
        
        if split != "test" and "label_distribution" in data:
            lines.append("\n### Label Distribution")
            for k, v in data["label_distribution"].items():
                lines.append(f"- {k}: {v['count']} ({v['percentage']:.2f}%)")
            lines.append(f"- Invalid Labels Count: {data.get('invalid_labels_count', 0)}")
            
        if "text_statistics" in data:
            ts = data["text_statistics"]
            lines.append("\n### Text Statistics (Length)")
            lines.append(f"- Min: {ts.get('min', 0)}")
            lines.append(f"- Max: {ts.get('max', 0)}")
            lines.append(f"- Mean: {ts.get('mean', 0):.2f}")
            lines.append(f"- Median: {ts.get('median', 0)}")
        
        if "noise_characteristics" in data:
            nc = data["noise_characteristics"]
            lines.append("\n### Noise Characteristics")
            lines.append(f"- Contain URLs: {nc.get('url_count', 0)}")
            lines.append(f"- Contain Mentions: {nc.get('mention_count', 0)}")
            lines.append(f"- Contain Hashtags: {nc.get('hashtag_count', 0)}")
            lines.append(f"- Non-ASCII Character %: {nc.get('non_ascii_percentage', 0):.2f}%")
        
        lines.append("")

    if "leakage" in report:
        lines.append("## Train/Validation Leakage")
        lines.append(f"- Exact Text Overlap: {report['leakage'].get('exact_text_overlap', 0)} rows")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("Loading datasets...")
    train_data, train_mal = load_data(TRAIN_FILE)
    valid_data, valid_mal = load_data(VALID_FILE)
    test_data, test_mal = load_data(TEST_FILE, is_test=True)

    report = {}
    
    print("Analyzing Train set...")
    report["train"] = analyze_dataset(train_data, train_mal)
    
    print("Analyzing Validation set...")
    report["valid"] = analyze_dataset(valid_data, valid_mal)
    
    print("Analyzing Test set...")
    report["test"] = analyze_dataset(test_data, test_mal, is_test=True)

    print("Checking for leakage...")
    if train_data and valid_data:
        train_texts = {row.get("text", "") for row in train_data if row.get("text")}
        valid_texts = {row.get("text", "") for row in valid_data if row.get("text")}
        overlap = len(train_texts.intersection(valid_texts))
        report["leakage"] = {"exact_text_overlap": overlap}
    
    print("Saving reports...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(JSON_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    generate_markdown_report(report, MD_REPORT_FILE)
    
    print(f"Reports generated successfully at {REPORTS_DIR}/")

if __name__ == "__main__":
    main()
