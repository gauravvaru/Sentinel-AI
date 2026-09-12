import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = Path("models/hinglish_muril")

def load_model_and_tokenizer():
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model directory {MODEL_DIR} not found. Please train the model in Colab and download the artifacts first.")
        
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    model.eval()
    return model, tokenizer

def predict_text(text: str, model, tokenizer):
    if not text.strip():
        raise ValueError("Cannot predict empty text.")
        
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits
    probs = torch.nn.functional.softmax(logits, dim=-1).squeeze().tolist()
    
    pred_idx = torch.argmax(logits, dim=-1).item()
    
    # Map index to label
    id2label = model.config.id2label
    if not id2label:
        id2label = {0: "negative", 1: "neutral", 2: "positive"}
        
    sentiment = id2label[pred_idx]
    confidence = probs[pred_idx]
    
    return pred_idx, sentiment, confidence, probs

def main():
    if len(sys.argv) < 2:
        print("Usage: python predict_hinglish_muril.py \"<text to predict>\"")
        sys.exit(1)
        
    text = " ".join(sys.argv[1:])
    
    try:
        model, tokenizer = load_model_and_tokenizer()
        pred_label, sentiment, confidence, probs = predict_text(text, model, tokenizer)
        
        print(f"Text: {text}")
        print(f"Prediction: {sentiment}")
        print(f"Label: {pred_label}")
        print(f"Confidence: {confidence:.4f}")
        print("Probabilities:")
        print(f"  negative: {probs[0]:.4f}")
        print(f"  neutral: {probs[1]:.4f}")
        print(f"  positive: {probs[2]:.4f}")
        print(f"Model: {model.config._name_or_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
