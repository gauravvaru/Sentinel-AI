from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class SentimentEvidence(BaseModel):
    available: bool = False
    positive_ratio: float | None = None
    negative_ratio: float | None = None
    neutral_ratio: float | None = None
    reason: str | None = "Sentiment analytics not currently implemented in production."

class TrendEvidence(BaseModel):
    available: bool = False
    trending_topics_count: int = 0
    top_topics: list[dict[str, Any]] = Field(default_factory=list)
    reason: str | None = None

class AudienceEvidence(BaseModel):
    available: bool = False
    total_users_analyzed: int = 0
    usable_users: int = 0
    insufficient_data_users: int = 0
    cohort_count: int = 0
    reason: str | None = None

class NetworkEvidence(BaseModel):
    available: bool = False
    node_count: int = 0
    edge_count: int = 0
    community_count: int = 0
    top_influencers: list[str] = Field(default_factory=list)
    reason: str | None = None

class InsightEvidence(BaseModel):
    """
    The master structured evidence model containing only verified, 
    persisted analytics. No LLM invention allowed here.
    """
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_window_hours: int
    data_quality: str = "insufficient" # high, moderate, low, insufficient
    sentiment: SentimentEvidence
    trends: TrendEvidence
    audience: AudienceEvidence
    network: NetworkEvidence
    limitations: list[str] = Field(default_factory=list)

class InsightResponse(BaseModel):
    headline: str
    summary: str
    key_findings: list[str]
    evidence: InsightEvidence
    caveats: list[str]
    data_quality: str
