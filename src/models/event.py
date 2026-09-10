from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SocialEvent(BaseModel):
    id: str
    platform: str
    event_type: str

    platform_event_id: str
    user_id: str
    parent_id: Optional[str] = None

    text: str
    language: Optional[str] = None

    event_time: datetime
    ingested_at: datetime
    processed_at: Optional[datetime] = None

    mentions: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)

    likes: int = 0
    replies: int = 0
    shares: int = 0

    location: Optional[str] = None
    follower_count: Optional[int] = None

    raw_payload: Dict[str, Any] = Field(default_factory=dict)
