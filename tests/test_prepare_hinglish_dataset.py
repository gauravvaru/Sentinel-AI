import pytest
from scripts.prepare_hinglish_dataset import clean_and_deduplicate, stratified_split

def test_clean_and_deduplicate_missing_text():
    data = [
        {"id": "1", "text": "  ", "label": "1", "source": "train"},
        {"id": "2", "text": "", "label": "2", "source": "valid"},
        {"id": "3", "text": "hello", "label": "0", "source": "train"}
    ]
    clean_pool, quarantine, stats = clean_and_deduplicate(data)
    
    assert len(clean_pool) == 1
    assert clean_pool[0]["text"] == "hello"
    
    assert len(quarantine) == 2
    assert quarantine[0]["quarantine_reason"] == "missing_text"
    assert quarantine[1]["quarantine_reason"] == "missing_text"
    
    assert stats["missing_text_rows"] == 2

def test_clean_and_deduplicate_same_label():
    data = [
        {"id": "1", "text": "duplicate", "label": "1", "source": "train"},
        {"id": "2", "text": "duplicate", "label": "1", "source": "valid"}
    ]
    clean_pool, quarantine, stats = clean_and_deduplicate(data)
    
    assert len(clean_pool) == 1
    assert clean_pool[0]["text"] == "duplicate"
    assert clean_pool[0]["label"] == "1"
    assert "source" not in clean_pool[0]  # ensure metadata removed from clean pool
    
    assert len(quarantine) == 0
    assert stats["same_label_groups"] == 1
    assert stats["conflicting_label_groups"] == 0

def test_clean_and_deduplicate_conflicting_label():
    data = [
        {"id": "1", "text": "conflict", "label": "1", "source": "train"},
        {"id": "2", "text": "conflict", "label": "0", "source": "valid"}
    ]
    clean_pool, quarantine, stats = clean_and_deduplicate(data)
    
    assert len(clean_pool) == 0
    assert len(quarantine) == 2
    assert quarantine[0]["quarantine_reason"] == "conflicting_labels"
    assert quarantine[1]["quarantine_reason"] == "conflicting_labels"
    assert stats["conflicting_label_groups"] == 1
    assert stats["same_label_groups"] == 0

def test_stratified_split_deterministic_and_stratified():
    # Create 100 rows for each label
    clean_pool = []
    for i in range(100):
        clean_pool.append({"id": f"0_{i}", "text": f"text_0_{i}", "label": "0"})
        clean_pool.append({"id": f"1_{i}", "text": f"text_1_{i}", "label": "1"})
        clean_pool.append({"id": f"2_{i}", "text": f"text_2_{i}", "label": "2"})
        
    train1, valid1 = stratified_split(clean_pool, seed=42, train_ratio=0.9)
    train2, valid2 = stratified_split(clean_pool, seed=42, train_ratio=0.9)
    
    # Deterministic
    assert [x["id"] for x in train1] == [x["id"] for x in train2]
    assert [x["id"] for x in valid1] == [x["id"] for x in valid2]
    
    # Stratified
    train_labels = [x["label"] for x in train1]
    valid_labels = [x["label"] for x in valid1]
    
    # 90% of 100 = 90
    assert train_labels.count("0") == 90
    assert train_labels.count("1") == 90
    assert train_labels.count("2") == 90
    
    assert valid_labels.count("0") == 10
    assert valid_labels.count("1") == 10
    assert valid_labels.count("2") == 10

def test_zero_overlap():
    # The split should have zero overlap by definition of how it operates on a single pool.
    clean_pool = [
        {"id": f"{i}", "text": f"unique_text_{i}", "label": "1"} for i in range(100)
    ]
    train, valid = stratified_split(clean_pool, seed=42, train_ratio=0.9)
    
    train_texts = {x["text"] for x in train}
    valid_texts = {x["text"] for x in valid}
    
    assert len(train_texts.intersection(valid_texts)) == 0

