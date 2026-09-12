import sys
from pathlib import Path
import joblib

MODELS_DIR = Path("models/hinglish_baseline")

def load_models():
    vectorizer_path = MODELS_DIR / "tfidf_vectorizer.joblib"
    clf_path = MODELS_DIR / "logreg_classifier.joblib"
    
    if not vectorizer_path.exists() or not clf_path.exists():
        raise FileNotFoundError(f"Model artifacts not found in {MODELS_DIR}. Run training script first.")
        
    vectorizer = joblib.load(vectorizer_path)
    clf = joblib.load(clf_path)
    return vectorizer, clf

def predict_text(text: str, vectorizer, clf):
    if not text.strip():
        raise ValueError("Cannot predict empty text.")
        
    features = vectorizer.transform([text])
    pred_label = clf.predict(features)[0]
    probs = clf.predict_proba(features)[0]
    
    classes = clf.classes_
    class_idx = list(classes).index(pred_label)
    confidence = probs[class_idx]
    
    sentiment_map = {"0": "negative", "1": "neutral", "2": "positive"}
    sentiment = sentiment_map.get(pred_label, "unknown")
    
    return pred_label, sentiment, float(confidence)

def main():
    if len(sys.argv) < 2:
        print("Usage: python predict_hinglish.py \"<text to predict>\"")
        sys.exit(1)
        
    text = " ".join(sys.argv[1:])
    
    try:
        vectorizer, clf = load_models()
        pred_label, sentiment, confidence = predict_text(text, vectorizer, clf)
        
        print(f"Text: \"{text}\"")
        print("Prediction:")
        print(f"label={pred_label}")
        print(f"sentiment={sentiment}")
        print(f"confidence={confidence:.4f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
