import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
import sys

DATA_DIR = Path("data/raw/Hinglish")
TRAIN_FILE = DATA_DIR / "FinalTrainingOnly.tsv"
VALID_FILE = DATA_DIR / "ValidationOnly.tsv"

REPORTS_DIR = Path("reports")
JSON_REPORT_FILE = REPORTS_DIR / "hinglish_leakage_analysis.json"
MD_REPORT_FILE = REPORTS_DIR / "hinglish_leakage_analysis.md"


def load_data(filepath: Path) -> List[Dict[str, str]]:
    data = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip('\n').split('\t')
            if len(parts) == 3:
                data.append({"id": parts[0], "text": parts[1], "label": parts[2]})
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return data


def group_by_text(data: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Groups data by text, storing a list of {id, label} dicts for each text."""
    grouped = {}
    for row in data:
        text = row["text"]
        if text:  # Ignore empty text
            if text not in grouped:
                grouped[text] = []
            grouped[text].append({"id": row["id"], "label": row["label"]})
    return grouped


def analyze_intra_split_conflicts(grouped_data: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
    """Analyzes conflicts within a single split (train or validation)."""
    multiple_occurrences = 0
    conflicts = 0
    
    for text, instances in grouped_data.items():
        if len(instances) > 1:
            multiple_occurrences += 1
            labels = {inst["label"] for inst in instances}
            if len(labels) > 1:
                conflicts += 1
                
    return {
        "texts_with_multiple_occurrences": multiple_occurrences,
        "texts_with_conflicting_labels": conflicts
    }


def analyze_leakage(train_grouped: Dict[str, List[Dict[str, str]]], valid_grouped: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
    overlapping_texts = set(train_grouped.keys()).intersection(set(valid_grouped.keys()))
    
    same_label_texts = []
    conflicting_label_texts = []
    
    affected_train_rows = 0
    affected_valid_rows = 0
    
    for text in overlapping_texts:
        train_instances = train_grouped[text]
        valid_instances = valid_grouped[text]
        
        affected_train_rows += len(train_instances)
        affected_valid_rows += len(valid_instances)
        
        train_labels = {inst["label"] for inst in train_instances}
        valid_labels = {inst["label"] for inst in valid_instances}
        
        # Combine all labels across train and validation for this text
        all_labels = train_labels.union(valid_labels)
        
        overlap_info = {
            "text": text,
            "train_instances": train_instances,
            "valid_instances": valid_instances,
            "unique_labels": list(all_labels)
        }
        
        if len(all_labels) == 1:
            same_label_texts.append(overlap_info)
        else:
            conflicting_label_texts.append(overlap_info)
            
    total_overlaps = len(overlapping_texts)
    same_count = len(same_label_texts)
    conflict_count = len(conflicting_label_texts)
    
    same_percentage = (same_count / total_overlaps * 100) if total_overlaps > 0 else 0
    conflict_percentage = (conflict_count / total_overlaps * 100) if total_overlaps > 0 else 0
    
    return {
        "total_overlapping_texts": total_overlaps,
        "same_label_overlaps": same_count,
        "conflicting_label_overlaps": conflict_count,
        "same_label_percentage": same_percentage,
        "conflicting_label_percentage": conflict_percentage,
        "affected_train_rows": affected_train_rows,
        "affected_validation_rows": affected_valid_rows,
        "same_label_examples": same_label_texts[:20],
        "conflicting_label_examples": conflicting_label_texts[:20]
    }


def generate_markdown(analysis: Dict[str, Any], intra_train: Dict[str, Any], intra_valid: Dict[str, Any], filepath: Path):
    lines = [
        "# Hinglish Dataset Leakage Analysis",
        "",
        "## Overview",
        f"- **Total Overlapping Texts (Unique Strings):** {analysis['total_overlapping_texts']}",
        f"- **Affected Train Rows:** {analysis['affected_train_rows']}",
        f"- **Affected Validation Rows:** {analysis['affected_validation_rows']}",
        "",
        "## Overlap Categories",
        f"- **Same-Label Overlaps:** {analysis['same_label_overlaps']} ({analysis['same_label_percentage']:.2f}%)",
        f"- **Conflicting-Label Overlaps:** {analysis['conflicting_label_overlaps']} ({analysis['conflicting_label_percentage']:.2f}%)",
        "",
        "## Intra-Split Duplication & Conflicts",
        "### Train Split",
        f"- Texts appearing multiple times: {intra_train['texts_with_multiple_occurrences']}",
        f"- Texts with conflicting labels (among duplicates): {intra_train['texts_with_conflicting_labels']}",
        "### Validation Split",
        f"- Texts appearing multiple times: {intra_valid['texts_with_multiple_occurrences']}",
        f"- Texts with conflicting labels (among duplicates): {intra_valid['texts_with_conflicting_labels']}",
        "",
        "## Representative Conflicting Examples (up to 20)",
        ""
    ]
    
    for ex in analysis['conflicting_label_examples']:
        lines.append(f"**Text:** `{ex['text']}`")
        lines.append(f"- Train instances: {ex['train_instances']}")
        lines.append(f"- Validation instances: {ex['valid_instances']}")
        lines.append("")
        
    lines.append("## Representative Same-Label Examples (up to 20)")
    lines.append("")
    
    for ex in analysis['same_label_examples']:
        lines.append(f"**Text:** `{ex['text']}`")
        lines.append(f"- Train instances: {ex['train_instances']}")
        lines.append(f"- Validation instances: {ex['valid_instances']}")
        lines.append("")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    print("Loading datasets...")
    train_data = load_data(TRAIN_FILE)
    valid_data = load_data(VALID_FILE)
    
    if not train_data or not valid_data:
        print("Failed to load datasets. Ensure the files exist.")
        sys.exit(1)
        
    train_grouped = group_by_text(train_data)
    valid_grouped = group_by_text(valid_data)
    
    print("Analyzing intra-split conflicts...")
    intra_train = analyze_intra_split_conflicts(train_grouped)
    intra_valid = analyze_intra_split_conflicts(valid_grouped)
    
    print("Analyzing leakage...")
    leakage_analysis = analyze_leakage(train_grouped, valid_grouped)
    
    print("Saving reports...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    full_report = {
        "leakage": leakage_analysis,
        "intra_split": {
            "train": intra_train,
            "valid": intra_valid
        }
    }
    
    with open(JSON_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=4)
        
    generate_markdown(leakage_analysis, intra_train, intra_valid, MD_REPORT_FILE)
    print(f"Reports generated successfully at {REPORTS_DIR}/")

if __name__ == "__main__":
    main()
