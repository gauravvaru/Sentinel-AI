from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_session
from src.network.analyzer import NetworkAnalyzer
from pydantic import BaseModel

router = APIRouter(prefix="/api/network", tags=["Network Intelligence"])

class InfluencerResponse(BaseModel):
    user_id: str
    in_degree: float
    out_degree: float
    degree_centrality: float
    pagerank: float
    betweenness_centrality: float

class CommunityResponse(BaseModel):
    community_id: int
    users_count: int
    interaction_volume: float
    top_influencers: List[Dict[str, Any]]

class TopicNetworkResponse(BaseModel):
    topic_id: int
    events_analyzed: int
    users_analyzed: int
    platform_distribution: Dict[str, int]
    communities: List[CommunityResponse]
    top_influencers: List[InfluencerResponse]

class PropagationEvent(BaseModel):
    event_id: str
    event_time: Optional[str]
    platform: str
    event_type: str
    user_id: str
    parent_id: Optional[str]
    mentions: List[str]
    text: str

@router.get("/influencers", response_model=List[InfluencerResponse])
async def get_influencers(
    time_window_hours: int = Query(24, description="Time window in hours"),
    platform: Optional[str] = None,
    limit: int = Query(50, description="Max influencers to return"),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieves the most influential users across the entire network within the given time window.
    Calculated via PageRank on actual observed interaction graphs.
    """
    analyzer = NetworkAnalyzer(session)
    events = await analyzer._fetch_events(time_window_hours=time_window_hours, platform=platform, limit=5000)
    G = analyzer.build_network(events)
    influencers = analyzer.calculate_influence(G)
    return influencers[:limit]

@router.get("/communities", response_model=List[CommunityResponse])
async def get_communities(
    time_window_hours: int = Query(24, description="Time window in hours"),
    platform: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detected communities in the interaction network using deterministic Louvain.
    """
    analyzer = NetworkAnalyzer(session)
    events = await analyzer._fetch_events(time_window_hours=time_window_hours, platform=platform, limit=5000)
    G = analyzer.build_network(events)
    communities = analyzer.detect_communities(G)
    return communities

@router.get("/topic/{topic_id}", response_model=TopicNetworkResponse)
async def get_topic_network(
    topic_id: int,
    time_window_hours: int = Query(24, description="Time window in hours"),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze the communities and influencers for a specific topic.
    """
    analyzer = NetworkAnalyzer(session)
    result = await analyzer.get_topic_communities(topic_id, time_window_hours=time_window_hours)
    return result

@router.get("/propagation/{topic_id}", response_model=List[PropagationEvent])
async def get_propagation_timeline(
    topic_id: int,
    limit: int = Query(500, description="Max events to return"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get a chronological timeline of observed interactions for a topic.
    Allows replaying how a narrative spread without claiming causal influence.
    """
    analyzer = NetworkAnalyzer(session)
    timeline = await analyzer.get_propagation_timeline(topic_id, limit=limit)
    return timeline
