from typing import Protocol, List

class EmbeddingModel(Protocol):
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode a list of texts into a list of embedding vectors."""
        ...

class SentenceTransformerEmbedding:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        # Note: Do not commit model cache into Git!
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        # Handle empty/None texts
        safe_texts = [text if text else "" for text in texts]
        embeddings = self.model.encode(safe_texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()
