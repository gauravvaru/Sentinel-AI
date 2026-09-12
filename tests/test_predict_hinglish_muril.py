import pytest
import torch
from unittest.mock import MagicMock
from scripts.predict_hinglish_muril import predict_text

class DummyConfig:
    def __init__(self):
        self.id2label = {0: "negative", 1: "neutral", 2: "positive"}
        self._name_or_path = "dummy/model"

class DummyModel:
    def __init__(self):
        self.config = DummyConfig()
        
    def __call__(self, **kwargs):
        class Output:
            # logits for 3 classes
            logits = torch.tensor([[0.1, 2.5, -0.5]])
        return Output()

class DummyTokenizer:
    def __call__(self, text, **kwargs):
        return {"input_ids": torch.tensor([[1, 2, 3]])}

def test_predict_text_schema_and_distribution():
    model = DummyModel()
    tokenizer = DummyTokenizer()
    
    pred_idx, sentiment, confidence, probs = predict_text("test sentence", model, tokenizer)
    
    # 1. verify label mapping
    assert pred_idx == 1
    assert sentiment == "neutral"
    
    # 2. probabilities form a valid distribution
    assert len(probs) == 3
    assert abs(sum(probs) - 1.0) < 1e-6
    for p in probs:
        assert 0 <= p <= 1
        
    # 3. predicted label is 0, 1, or 2
    assert pred_idx in [0, 1, 2]
    
    # 4. confidence matches the probability of the predicted class
    assert abs(confidence - probs[1]) < 1e-6

def test_predict_empty_text():
    model = DummyModel()
    tokenizer = DummyTokenizer()
    
    with pytest.raises(ValueError, match="Cannot predict empty text"):
        predict_text("   ", model, tokenizer)
