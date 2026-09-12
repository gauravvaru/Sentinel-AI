import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import sklearn

DATA_DIR = Path("data/processed/hinglish")
TRAIN_FILE = DATA_DIR / "train.tsv"
VALID_FILE = DATA_DIR / "validation.tsv"
MODELS_DIR = Path("models/hinglish_baseline")
REPORTS_DIR = Path("reports")

def load_data(filepath: Path) -> Tuple[List[str], List[str]]:
    texts = []
    labels = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip('\n').split('\t')
            if len(parts) >= 3:
                texts.append(parts[1])
                labels.append(parts[2])
    return texts, labels

def validate_data(texts: List[str], labels: List[str], name: str):
    if len(texts) == 0:
        raise ValueError(f"{name} set is empty.")
    if len(texts) != len(labels):
        raise ValueError(f"Length mismatch in {name} set.")
        
    for text, label in zip(texts, labels):
        if not text or not text.strip():
            raise ValueError(f"Empty text found in {name} set.")
        if label not in ["0", "1", "2"]:
            raise ValueError(f"Invalid label '{label}' found in {name} set.")

def get_class_distribution(labels: List[str]) -> Dict[str, int]:
    dist = {"0": 0, "1": 0, "2": 0}
    for label in labels:
        dist[label] += 1
    return dist

def train_baseline():
    print("Loading data...")
    train_texts, train_labels = load_data(TRAIN_FILE)
    valid_texts, valid_labels = load_data(VALID_FILE)
    
    print("Validating data...")
    validate_data(train_texts, train_labels, "train")
    validate_data(valid_texts, valid_labels, "validation")
    
    print("Training TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_df=0.95
    )
    
    X_train = vectorizer.fit_transform(train_texts)
    X_valid = vectorizer.transform(valid_texts)
    
    print("Training Logistic Regression...")
    clf = LogisticRegression(max_iter=2000, random_state=42)
    clf.fit(X_train, train_labels)
    
    print("Predicting validation set...")
    valid_preds = clf.predict(X_valid)
    
    print("Calculating metrics...")
    acc = accuracy_score(valid_labels, valid_preds)
    macro_f1 = f1_score(valid_labels, valid_preds, average="macro")
    weighted_f1 = f1_score(valid_labels, valid_preds, average="weighted")
    
    precision_macro = precision_score(valid_labels, valid_preds, average="macro")
    recall_macro = recall_score(valid_labels, valid_preds, average="macro")
    
    per_class_precision = precision_score(valid_labels, valid_preds, average=None).tolist()
    per_class_recall = recall_score(valid_labels, valid_preds, average=None).tolist()
    per_class_f1 = f1_score(valid_labels, valid_preds, average=None).tolist()
    
    cm = confusion_matrix(valid_labels, valid_preds).tolist()
    
    print("Saving artifacts...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "logreg_classifier.joblib")
    
    config = {
        "tfidf": {
            "ngram_range": [1, 2],
            "sublinear_tf": True,
            "min_df": 2,
            "max_df": 0.95
        },
        "logreg": {
            "max_iter": 2000,
            "random_state": 42
        }
    }
    
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        
    print("Generating reports...")
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": {
            "python_version": sys.version,
            "scikit_learn_version": sklearn.__version__
        },
        "dataset": {
            "train_size": len(train_texts),
            "validation_size": len(valid_texts),
            "train_class_distribution": get_class_distribution(train_labels),
            "validation_class_distribution": get_class_distribution(valid_labels)
        },
        "configuration": config,
        "results": {
            "accuracy": acc,
            "macro_f1": macro_f1,
            "weighted_f1": weighted_f1,
            "macro_precision": precision_macro,
            "macro_recall": recall_macro,
            "per_class": {
                "0": {
                    "precision": per_class_precision[0],
                    "recall": per_class_recall[0],
                    "f1": per_class_f1[0]
                },
                "1": {
                    "precision": per_class_precision[1],
                    "recall": per_class_recall[1],
                    "f1": per_class_f1[1]
                },
                "2": {
                    "precision": per_class_precision[2],
                    "recall": per_class_recall[2],
                    "f1": per_class_f1[2]
                }
            },
            "confusion_matrix": cm
        }
    }
    
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(REPORTS_DIR / "hinglish_baseline.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    md_lines = [
        "# Hinglish TF-IDF + LogReg Baseline Report",
        "",
        f"**Timestamp:** {report['timestamp']}",
        f"**Python Version:** {sys.version.split()[0]}",
        f"**scikit-learn Version:** {sklearn.__version__}",
        "",
        "## Dataset",
        f"- **Train Size:** {report['dataset']['train_size']}",
        f"- **Validation Size:** {report['dataset']['validation_size']}",
        "### Train Distribution",
        f"- 0 (Negative): {report['dataset']['train_class_distribution']['0']}",
        f"- 1 (Neutral): {report['dataset']['train_class_distribution']['1']}",
        f"- 2 (Positive): {report['dataset']['train_class_distribution']['2']}",
        "### Validation Distribution",
        f"- 0 (Negative): {report['dataset']['validation_class_distribution']['0']}",
        f"- 1 (Neutral): {report['dataset']['validation_class_distribution']['1']}",
        f"- 2 (Positive): {report['dataset']['validation_class_distribution']['2']}",
        "",
        "## Configuration",
        "**TF-IDF:**",
        "- N-gram range: (1, 2)",
        "- sublinear_tf: True",
        "- min_df: 2",
        "- max_df: 0.95",
        "**Logistic Regression:**",
        "- max_iter: 2000",
        "- random_state: 42",
        "",
        "## Results",
        f"- **Macro F1 (Primary Metric):** {macro_f1:.4f}",
        f"- **Accuracy:** {acc:.4f}",
        f"- **Weighted F1:** {weighted_f1:.4f}",
        "",
        "### Per-Class Metrics",
        "**0 (Negative):**",
        f"- Precision: {per_class_precision[0]:.4f} | Recall: {per_class_recall[0]:.4f} | F1: {per_class_f1[0]:.4f}",
        "**1 (Neutral):**",
        f"- Precision: {per_class_precision[1]:.4f} | Recall: {per_class_recall[1]:.4f} | F1: {per_class_f1[1]:.4f}",
        "**2 (Positive):**",
        f"- Precision: {per_class_precision[2]:.4f} | Recall: {per_class_recall[2]:.4f} | F1: {per_class_f1[2]:.4f}",
        "",
        "### Confusion Matrix",
        "```",
        f"{cm[0]}",
        f"{cm[1]}",
        f"{cm[2]}",
        "```",
        ""
    ]
    
    with open(REPORTS_DIR / "hinglish_baseline.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    print(f"Reports generated successfully at {REPORTS_DIR}/")

if __name__ == "__main__":
    train_baseline()
