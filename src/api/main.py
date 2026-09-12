from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.session import get_session
from src.db.models import TopicModel
from src.semantic.embeddings import SentenceTransformerEmbedding
from src.semantic.vector_store import PGVectorStore
from src.semantic.trends import TrendAnalysisService

from src.api.network import router as network_router

app = FastAPI(title="SentinelAI API")
app.include_router(network_router)

# Initialize models
# In a real production app, we would load this in a lifespan handler to avoid blocking.
# For simplicity and MVP, we load it eagerly.
embedding_model = SentenceTransformerEmbedding()

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

@app.post("/api/search")
async def semantic_search(request: SearchRequest, session: AsyncSession = Depends(get_session)):
    """Search for social events using semantic similarity."""
    query_embedding = embedding_model.encode([request.query])[0]
    
    vector_store = PGVectorStore(session)
    results = await vector_store.search(
        query_embedding=query_embedding,
        limit=request.limit,
        filters=request.filters
    )
    
    return {"results": results}

@app.get("/api/topics/trending")
async def get_trending_topics(window_hours: int = 24, limit: int = 10, session: AsyncSession = Depends(get_session)):
    """Get the top trending topics."""
    # First, get all valid topics (not outliers)
    stmt = select(TopicModel).where(TopicModel.is_outlier == False)
    result = await session.execute(stmt)
    topics = result.scalars().all()
    
    trend_service = TrendAnalysisService(session)
    trending = []
    
    for topic in topics:
        trend_data = await trend_service.get_topic_trend(topic.id, window_hours=window_hours)
        trending.append({
            "topic_id": topic.id,
            "name": topic.name,
            "keywords": topic.keywords,
            "trend_score": trend_data["trend_score"],
            "metrics": trend_data["metrics"]
        })
        
    # Sort by trend_score descending
    trending.sort(key=lambda x: x["trend_score"], reverse=True)
    
    return {"trending": trending[:limit]}

@app.get("/api/topics/{topic_id}")
async def get_topic_details(topic_id: int, session: AsyncSession = Depends(get_session)):
    """Get details for a specific topic."""
    stmt = select(TopicModel).where(TopicModel.id == topic_id)
    result = await session.execute(stmt)
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
        
    trend_service = TrendAnalysisService(session)
    trend_data = await trend_service.get_topic_trend(topic_id)
    
    return {
        "id": topic.id,
        "name": topic.name,
        "keywords": topic.keywords,
        "is_outlier": topic.is_outlier,
        "created_at": topic.created_at,
        "trend_data": trend_data
    }
