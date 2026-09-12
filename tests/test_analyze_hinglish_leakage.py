import pytest
from scripts.analyze_hinglish_leakage import group_by_text, analyze_intra_split_conflicts, analyze_leakage

def test_group_by_text():
    data = [
        {"id": "1", "text": "hello world", "label": "1"},
        {"id": "2", "text": "hello world", "label": "0"},
        {"id": "3", "text": "goodbye", "label": "2"}
    ]
    grouped = group_by_text(data)
    
    assert len(grouped) == 2
    assert "hello world" in grouped
    assert "goodbye" in grouped
    
    assert len(grouped["hello world"]) == 2
    assert grouped["hello world"][0]["id"] == "1"
    assert grouped["hello world"][1]["label"] == "0"


def test_analyze_intra_split_conflicts():
    grouped = {
        "text 1": [{"id": "1", "label": "1"}, {"id": "2", "label": "1"}], # duplicate, no conflict
        "text 2": [{"id": "3", "label": "1"}, {"id": "4", "label": "0"}], # duplicate, conflict
        "text 3": [{"id": "5", "label": "2"}] # single occurrence
    }
    
    res = analyze_intra_split_conflicts(grouped)
    assert res["texts_with_multiple_occurrences"] == 2
    assert res["texts_with_conflicting_labels"] == 1


def test_analyze_leakage():
    train = {
        "common same": [{"id": "t1", "label": "1"}],
        "common conflict": [{"id": "t2", "label": "1"}],
        "only train": [{"id": "t3", "label": "2"}],
        "common same multi": [{"id": "t4", "label": "0"}, {"id": "t5", "label": "0"}],
        "common conflict intra": [{"id": "t6", "label": "1"}, {"id": "t7", "label": "0"}]
    }
    
    valid = {
        "common same": [{"id": "v1", "label": "1"}],
        "common conflict": [{"id": "v2", "label": "0"}],
        "only valid": [{"id": "v3", "label": "1"}],
        "common same multi": [{"id": "v4", "label": "0"}],
        "common conflict intra": [{"id": "v5", "label": "1"}]
    }
    
    res = analyze_leakage(train, valid)
    
    assert res["total_overlapping_texts"] == 4 # common same, common conflict, common same multi, common conflict intra
    assert res["same_label_overlaps"] == 2 # common same, common same multi
    assert res["conflicting_label_overlaps"] == 2 # common conflict, common conflict intra
    
    # 1 (common same) + 1 (common conflict) + 2 (common same multi) + 2 (common conflict intra) = 6 train rows
    assert res["affected_train_rows"] == 6
    # 1 (common same) + 1 (common conflict) + 1 (common same multi) + 1 (common conflict intra) = 4 valid rows
    assert res["affected_validation_rows"] == 4

