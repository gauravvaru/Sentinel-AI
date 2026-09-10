from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SocialEventModel(Base):
    __tablename__ = 'social_events'

    id = Column(String, primary_key=True)
    platform = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    
    platform_event_id = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    parent_id = Column(String, nullable=True)

    text = Column(Text, nullable=False)
    language = Column(String, nullable=True)

    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    mentions = Column(JSON, nullable=False, default=list)
    hashtags = Column(JSON, nullable=False, default=list)

    likes = Column(Integer, nullable=False, default=0)
    replies = Column(Integer, nullable=False, default=0)
    shares = Column(Integer, nullable=False, default=0)

    location = Column(String, nullable=True)
    follower_count = Column(Integer, nullable=True)

    raw_payload = Column(JSON, nullable=False, default=dict)
