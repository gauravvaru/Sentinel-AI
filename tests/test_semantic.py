import pytest
import numpy as np
from src.semantic.embeddings import SentenceTransformerEmbedding
from src.semantic.topic_discovery import TopicDiscoveryService
from src.semantic.trends import TrendAnalysisService
from fastapi.testclient import TestClient
from src.api.main import app

def test_embeddings():
    """Test the SentenceTransformer wrapper."""
    embedder = SentenceTransformerEmbedding()
    # It might take a moment to download in CI, but it should work
    texts = ["This is a test document", "Another document to test embeddings"]
    embeddings = embedder.encode(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert isinstance(embeddings[0][0], float)

def test_topic_discovery():
    """Test BERTopic + HDBSCAN wrapper."""
    discovery = TopicDiscoveryService(min_cluster_size=2)
    
    # We need enough documents to form a cluster
    documents = [
        "I love Python programming",
        "Python is great for data science",
        "Data science uses Python heavily",
        "I enjoy writing Python code",
        "The weather is very nice today",
        "It's sunny and beautiful outside",
        "I went for a walk in the sun",
        "Perfect weather for a walk"
    ]
    
    # Mock embeddings instead of calling the actual model for speed
    # We create two distinct clusters (first 4, next 4)
    embeddings = []
    for i in range(8):
        vec = np.zeros(384)
        if i < 4:
            vec[0] = 1.0 # Tech cluster
        else:
            vec[1] = 1.0 # Weather cluster
        # Add a tiny bit of noise
        vec += np.random.normal(0, 0.01, 384)
        embeddings.append(vec.tolist())
        
    topics, metadata = discovery.discover_topics(documents, embeddings)
    
    assert len(topics) == 8
    # With min_cluster_size=2, we should get at least some non-outlier topics
    assert len(metadata) > 0

# Test client for the API
client = TestClient(app)

def test_api_docs():
    """Test if FastAPI is set up and can serve docs."""
    response = client.get("/docs")
    assert response.status_code == 200
