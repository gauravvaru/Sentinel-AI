import asyncio
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.db.session import engine, async_session
from src.db.models import SocialEventModel, TopicModel
from src.semantic.embeddings import SentenceTransformerEmbedding
from src.semantic.topic_discovery import TopicDiscoveryService
from src.semantic.vector_store import PGVectorStore
import os

async def run_pipeline(limit: int = 100):
    print("Starting Topics & Trends Pipeline...")
    
    # 1. Fetch un-embedded events
    print(f"Fetching up to {limit} events without embeddings...")
    async with async_session() as session:
        stmt = select(SocialEventModel).where(SocialEventModel.embedding == None).limit(limit)
        result = await session.execute(stmt)
        events = result.scalars().all()
        
    if not events:
        print("No new events to process.")
        return
        
    print(f"Found {len(events)} events.")
    texts = [event.text for event in events]
    
    # 2. Generate Embeddings
    print("Generating embeddings using paraphrase-multilingual-MiniLM-L12-v2...")
    embedder = SentenceTransformerEmbedding()
    embeddings = embedder.encode(texts)
    
    # 3. Topic Discovery
    print("Running BERTopic + HDBSCAN for topic discovery...")
    discovery = TopicDiscoveryService(min_cluster_size=min(5, len(texts)//2))
    topics, topic_metadata = discovery.discover_topics(texts, embeddings)
    
    # 4. Save to Database
    print("Saving topics and updating events...")
    async with async_session() as session:
        # Save topics first
        topic_db_map = {} # Maps BERTopic ID to Database Topic ID
        for topic_id, metadata in topic_metadata.items():
            new_topic = TopicModel(
                name=metadata["name"],
                keywords=metadata["keywords"],
                is_outlier=metadata["is_outlier"]
            )
            session.add(new_topic)
            await session.flush() # To get the auto-generated ID
            topic_db_map[topic_id] = new_topic.id
            
        # Update events
        vector_store = PGVectorStore(session)
        for i, event in enumerate(events):
            event.embedding = embeddings[i]
            if topics[i] in topic_db_map:
                event.topic_id = topic_db_map[topics[i]]
            session.add(event)
            
        await session.commit()
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
