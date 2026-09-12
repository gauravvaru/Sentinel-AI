from typing import List, Dict, Any, Tuple
from bertopic import BERTopic
from hdbscan import HDBSCAN
import numpy as np

class TopicDiscoveryService:
    def __init__(self, min_cluster_size: int = 10, language: str = "multilingual"):
        """
        Initialize BERTopic with HDBSCAN.
        """
        self.hdbscan_model = HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )
        # We don't specify embedding_model here because we pass pre-computed embeddings
        self.topic_model = BERTopic(
            hdbscan_model=self.hdbscan_model,
            language=language
        )
    
    def discover_topics(self, documents: List[str], embeddings: List[List[float]]) -> Tuple[List[int], Dict[int, Dict[str, Any]]]:
        """
        Run topic discovery on a set of documents and their pre-computed embeddings.
        Returns:
            - A list of topic assignments (integers), one for each document. -1 indicates outlier.
            - A dictionary mapping topic_id to topic metadata (name, keywords).
        """
        if not documents:
            return [], {}
            
        embeddings_np = np.array(embeddings)
        topics, _ = self.topic_model.fit_transform(documents, embeddings=embeddings_np)
        
        topic_info = self.topic_model.get_topic_info()
        
        metadata = {}
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            # BERTopic returns a name like "0_word1_word2_word3"
            # Get the top keywords for this topic
            keywords = [word for word, score in self.topic_model.get_topic(topic_id)] if topic_id != -1 else []
            
            metadata[topic_id] = {
                "name": row['Name'],
                "keywords": keywords,
                "is_outlier": topic_id == -1,
                "count": row['Count']
            }
            
        return topics, metadata
