from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audience.clustering import cluster_users
from src.audience.features import extract_user_features, is_usable_for_clustering
from src.db.models import SocialEventModel
from src.db.session import get_session

audience_router = APIRouter(prefix="/api/audience", tags=["Audience"])

class CohortSummary(BaseModel):
    cohort_id: str
    label: str
    user_count: int
    total_events: int
    average_engagement: float
    confidence: float
    demographics: str

class AudienceResponse(BaseModel):
    total_users: int
    usable_users: int
    insufficient_data_users: int
    cohorts: list[CohortSummary]

from src.utils.cache import ttl_cache

@audience_router.get("/cohorts", response_model=AudienceResponse)
@ttl_cache(ttl_seconds=60)
async def get_audience_cohorts(
    platform: str | None = None,
    limit: int = 1000,
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze audience cohorts based on observable behavior.
    """
    # Fetch data
    query = select(SocialEventModel)
    if platform:
        query = query.where(SocialEventModel.platform == platform)
    
    # We apply a limit for safety if DB is huge, though we'd really want time windows
    query = query.order_by(SocialEventModel.event_time.desc()).limit(limit)
    
    result = await session.execute(query)
    events = result.scalars().all()
    
    # Group by user_id
    user_events: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        uid = ev.user_id
        if uid not in user_events:
            user_events[uid] = []
        
        # We convert to a dict to match the feature extractor
        ev_dict = {
            "likes": ev.likes,
            "replies": ev.replies,
            "shares": ev.shares,
            "mentions": ev.mentions,
            "hashtags": ev.hashtags,
            "platform": ev.platform,
            "event_time": ev.event_time
        }
        user_events[uid].append(ev_dict)
        
    total_users = len(user_events)
    
    def _cpu_bound_work():
        usable_features = {}
        insufficient_count = 0
        
        for uid, u_events in user_events.items():
            features = extract_user_features(u_events)
            if is_usable_for_clustering(features):
                usable_features[uid] = features
            else:
                insufficient_count += 1
                
        usable_users = len(usable_features)
        
        if usable_users < 2:
            return usable_users, insufficient_count, []
            
        # Cluster
        _, cohort_summaries = cluster_users(usable_features)
        return usable_users, insufficient_count, cohort_summaries

    import asyncio
    usable_users, insufficient_count, cohort_summaries = await asyncio.to_thread(_cpu_bound_work)
    
    return AudienceResponse(
        total_users=total_users,
        usable_users=usable_users,
        insufficient_data_users=insufficient_count,
        cohorts=cohort_summaries
    )
