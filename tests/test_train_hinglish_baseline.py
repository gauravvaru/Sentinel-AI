import pytest
import os
from pathlib import Path
from scripts.train_hinglish_baseline import validate_data, load_data, train_baseline
from scripts.predict_hinglish import load_models, predict_text

def test_validate_data_success():
    texts = ["hello", "world"]
    labels = ["0", "1"]
    validate_data(texts, labels, "test")

def test_validate_data_empty():
    with pytest.raises(ValueError, match="is empty"):
        validate_data([], [], "test")

def test_validate_data_mismatch():
    with pytest.raises(ValueError, match="Length mismatch"):
        validate_data(["hello"], ["0", "1"], "test")

def test_validate_data_empty_text():
    with pytest.raises(ValueError, match="Empty text found"):
        validate_data(["   "], ["0"], "test")

def test_validate_data_invalid_label():
    with pytest.raises(ValueError, match="Invalid label"):
        validate_data(["hello"], ["3"], "test")

def test_training_and_prediction(tmp_path, monkeypatch):
    # Mock data directories to use a temp directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    train_file = data_dir / "train.tsv"
    valid_file = data_dir / "validation.tsv"
    
    # Write dummy TSV data
    with open(train_file, "w") as f:
        f.write("1\tI hate this\t0\n")
        f.write("2\tI love this\t2\n")
        f.write("3\tThis is okay\t1\n")
        f.write("4\tI hate you\t0\n")
        f.write("5\tI love you\t2\n")
        
    with open(valid_file, "w") as f:
        f.write("6\tI hate you\t0\n")
        f.write("7\tIt is fine\t1\n")
        f.write("8\tLove it\t2\n")
        
    # Override paths in train script
    monkeypatch.setattr("scripts.train_hinglish_baseline.TRAIN_FILE", train_file)
    monkeypatch.setattr("scripts.train_hinglish_baseline.VALID_FILE", valid_file)
    
    models_dir = tmp_path / "models"
    reports_dir = tmp_path / "reports"
    monkeypatch.setattr("scripts.train_hinglish_baseline.MODELS_DIR", models_dir)
    monkeypatch.setattr("scripts.train_hinglish_baseline.REPORTS_DIR", reports_dir)
    
    # Run training
    train_baseline()
    
    # Check artifacts exist
    assert (models_dir / "tfidf_vectorizer.joblib").exists()
    assert (models_dir / "logreg_classifier.joblib").exists()
    assert (reports_dir / "hinglish_baseline.json").exists()
    
    # Mock paths in predict script
    monkeypatch.setattr("scripts.predict_hinglish.MODELS_DIR", models_dir)
    
    # Load models
    vectorizer, clf = load_models()
    assert vectorizer is not None
    assert clf is not None
    
    # Predict output
    label, sentiment, confidence = predict_text("hate", vectorizer, clf)
    assert label in ["0", "1", "2"]
    assert sentiment in ["negative", "neutral", "positive"]
    assert 0.0 <= confidence <= 1.0

def test_load_data(tmp_path):
    f_path = tmp_path / "test.tsv"
    with open(f_path, "w") as f:
        f.write("id1\ttext1\t0\n")
        f.write("id2\ttext2\t1\n")
        
    texts, labels = load_data(f_path)
    assert texts == ["text1", "text2"]
    assert labels == ["0", "1"]
