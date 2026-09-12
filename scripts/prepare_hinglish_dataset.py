import json
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple

DATA_DIR = Path("data/raw/Hinglish")
TRAIN_FILE = DATA_DIR / "FinalTrainingOnly.tsv"
VALID_FILE = DATA_DIR / "ValidationOnly.tsv"
PROCESSED_DIR = Path("data/processed/hinglish")
REPORTS_DIR = Path("reports")

def load_split(filepath: Path, split_name: str) -> List[Dict[str, str]]:
    data = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip('\n').split('\t')
                if len(parts) == 3:
                    data.append({
                        "id": parts[0],
                        "text": parts[1],
                        "label": parts[2],
                        "source": split_name
                    })
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return data

def clean_and_deduplicate(data: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, int]]:
    stats = {
        "source_rows": len(data),
        "missing_text_rows": 0,
        "duplicate_groups": 0,
        "same_label_groups": 0,
        "conflicting_label_groups": 0,
        "quarantined_rows": 0
    }
    
    quarantine = []
    
    # 1. Filter missing text
    valid_text_rows = []
    for row in data:
        if not row["text"] or not row["text"].strip():
            row["quarantine_reason"] = "missing_text"
            quarantine.append(row)
            stats["missing_text_rows"] += 1
            stats["quarantined_rows"] += 1
        else:
            valid_text_rows.append(row)
            
    # 2. Group by text
    grouped = {}
    for row in valid_text_rows:
        text = row["text"]
        if text not in grouped:
            grouped[text] = []
        grouped[text].append(row)
        
    # 3. Deduplicate and detect conflicts
    clean_pool = []
    for text, rows in grouped.items():
        if len(rows) > 1:
            stats["duplicate_groups"] += 1
            unique_labels = {r["label"] for r in rows}
            if len(unique_labels) == 1:
                stats["same_label_groups"] += 1
                # retain ONE canonical row
                canonical = rows[0].copy()
                if "source" in canonical:
                    del canonical["source"]
                clean_pool.append(canonical)
            else:
                stats["conflicting_label_groups"] += 1
                # quarantine all rows
                for r in rows:
                    r["quarantine_reason"] = "conflicting_labels"
                    quarantine.append(r)
                    stats["quarantined_rows"] += 1
        else:
            # unique text
            canonical = rows[0].copy()
            if "source" in canonical:
                del canonical["source"]
            clean_pool.append(canonical)
            
    return clean_pool, quarantine, stats


def stratified_split(clean_pool: List[Dict[str, str]], seed: int = 42, train_ratio: float = 0.9) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    # Group by label
    label_groups = {}
    for row in clean_pool:
        label = row["label"]
        if label not in label_groups:
            label_groups[label] = []
        label_groups[label].append(row)
        
    train_split = []
    valid_split = []
    
    rng = random.Random(seed)
    
    for label, items in label_groups.items():
        # sort items to ensure determinism before shuffle
        items.sort(key=lambda x: x["id"])
        rng.shuffle(items)
        split_idx = int(len(items) * train_ratio)
        train_split.extend(items[:split_idx])
        valid_split.extend(items[split_idx:])
        
    return train_split, valid_split

def save_tsv(data: List[Dict[str, str]], filepath: Path, keys: List[str]):
    with open(filepath, "w", encoding="utf-8") as f:
        for row in data:
            f.write("\t".join(str(row.get(k, "")) for k in keys) + "\n")

def generate_report(stats: Dict[str, Any], train_split: List[Dict[str, str]], valid_split: List[Dict[str, str]], seed: int):
    # Calculate distributions
    train_dist = {"0": 0, "1": 0, "2": 0}
    for r in train_split:
        train_dist[r["label"]] = train_dist.get(r["label"], 0) + 1
        
    valid_dist = {"0": 0, "1": 0, "2": 0}
    for r in valid_split:
        valid_dist[r["label"]] = valid_dist.get(r["label"], 0) + 1
        
    # Overlap check
    train_texts = {r["text"] for r in train_split}
    valid_texts = {r["text"] for r in valid_split}
    overlap = len(train_texts.intersection(valid_texts))
    
    report = {
        "source_row_counts": stats["source_rows"],
        "cleaned_row_count": len(train_split) + len(valid_split),
        "missing_text_rows_quarantined": stats["missing_text_rows"],
        "duplicate_groups": stats["duplicate_groups"],
        "same_label_duplicate_groups": stats["same_label_groups"],
        "conflicting_label_groups": stats["conflicting_label_groups"],
        "quarantined_rows": stats["quarantined_rows"],
        "final_train_count": len(train_split),
        "final_validation_count": len(valid_split),
        "final_class_distributions": {
            "train": train_dist,
            "validation": valid_dist
        },
        "exact_train_validation_overlap": overlap,
        "random_seed": seed,
        "preprocessing_decisions": [
            "Missing text rows are quarantined.",
            "Text-level deduplication is applied.",
            "Identical texts with the same label are merged into a single canonical row.",
            "Identical texts with conflicting labels are entirely quarantined.",
            "Stratified split by label ensures balanced distributions.",
            "Test set is left completely untouched."
        ]
    }
    
    with open(REPORTS_DIR / "hinglish_preparation.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    md_lines = [
        "# Hinglish Dataset Preparation Report",
        "",
        f"- **Source Row Count:** {report['source_row_counts']}",
        f"- **Cleaned Row Count:** {report['cleaned_row_count']}",
        f"- **Missing Text Rows Quarantined:** {report['missing_text_rows_quarantined']}",
        f"- **Quarantined Rows (Total):** {report['quarantined_rows']}",
        "",
        "## Duplicates",
        f"- **Duplicate Groups:** {report['duplicate_groups']}",
        f"- **Same-Label Duplicate Groups:** {report['same_label_duplicate_groups']}",
        f"- **Conflicting-Label Groups:** {report['conflicting_label_groups']}",
        "",
        "## Final Splits",
        f"- **Random Seed:** {report['random_seed']}",
        f"- **Train Count:** {report['final_train_count']}",
        f"- **Validation Count:** {report['final_validation_count']}",
        f"- **Train/Validation Overlap:** {report['exact_train_validation_overlap']}",
        "",
        "### Train Class Distribution",
        f"- 0 (Negative): {train_dist.get('0', 0)}",
        f"- 1 (Neutral): {train_dist.get('1', 0)}",
        f"- 2 (Positive): {train_dist.get('2', 0)}",
        "",
        "### Validation Class Distribution",
        f"- 0 (Negative): {valid_dist.get('0', 0)}",
        f"- 1 (Neutral): {valid_dist.get('1', 0)}",
        f"- 2 (Positive): {valid_dist.get('2', 0)}",
        "",
        "## Preprocessing Decisions",
    ]
    for decision in report['preprocessing_decisions']:
        md_lines.append(f"- {decision}")
        
    with open(REPORTS_DIR / "hinglish_preparation.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

def main():
    print("Loading datasets...")
    train_raw = load_split(TRAIN_FILE, "train")
    valid_raw = load_split(VALID_FILE, "validation")
    
    combined = train_raw + valid_raw
    print(f"Loaded {len(combined)} rows.")
    
    print("Cleaning and deduplicating...")
    clean_pool, quarantine_pool, stats = clean_and_deduplicate(combined)
    
    print(f"Clean pool size: {len(clean_pool)}")
    print("Stratifying and splitting...")
    SEED = 42
    train_split, valid_split = stratified_split(clean_pool, seed=SEED, train_ratio=0.9)
    
    print("Saving datasets...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    save_tsv(train_split, PROCESSED_DIR / "train.tsv", ["id", "text", "label"])
    save_tsv(valid_split, PROCESSED_DIR / "validation.tsv", ["id", "text", "label"])
    save_tsv(quarantine_pool, PROCESSED_DIR / "quarantine.tsv", ["id", "text", "label", "source", "quarantine_reason"])
    
    print("Generating report...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    generate_report(stats, train_split, valid_split, SEED)
    print("Done.")

if __name__ == "__main__":
    main()
