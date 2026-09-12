from typing import Protocol, List, Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.db.models import SocialEventModel, TopicModel
import json

class VectorStore(Protocol):
    async def search(self, query_embedding: List[float], limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for the most similar events using cosine similarity."""
        ...
    
    async def update_event_embedding(self, event_id: str, embedding: List[float]) -> None:
        """Update the embedding for a specific event."""
        ...

class PGVectorStore:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def search(self, query_embedding: List[float], limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Cosine distance operator is <=>. To get similarity (descending), we order by cosine distance ascending.
        # pgvector uses cosine distance: 1 - cosine_similarity.
        
        stmt = select(SocialEventModel).order_by(SocialEventModel.embedding.cosine_distance(query_embedding)).limit(limit)
        
        if filters:
            if 'platform' in filters:
                stmt = stmt.where(SocialEventModel.platform == filters['platform'])
            if 'language' in filters:
                stmt = stmt.where(SocialEventModel.language == filters['language'])
        
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        
        # We need to map to dictionaries for the API response.
        return [
            {
                "id": event.id,
                "text": event.text,
                "platform": event.platform,
                "language": event.language,
                "event_time": event.event_time,
                "topic_id": event.topic_id,
            } for event in events
        ]
        
    async def update_event_embedding(self, event_id: str, embedding: List[float]) -> None:
        stmt = update(SocialEventModel).where(SocialEventModel.id == event_id).values(embedding=embedding)
        await self.session.execute(stmt)
        await self.session.commit()
