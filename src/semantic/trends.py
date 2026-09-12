from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.db.models import SocialEventModel, TopicModel

class TrendAnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_topic_trend(self, topic_id: int, window_hours: int = 24) -> Dict[str, Any]:
        """
        Calculate the trend score for a specific topic based on:
        - Velocity (0.4)
        - Engagement Growth (0.3)
        - Cross-platform presence (0.2)
        - Novelty (0.1)
        """
        now = datetime.now(timezone.utc)
        current_window_start = now - timedelta(hours=window_hours)
        previous_window_start = current_window_start - timedelta(hours=window_hours)
        
        # 1. Velocity (events in current window)
        velocity_stmt = select(func.count(SocialEventModel.id)).where(
            SocialEventModel.topic_id == topic_id,
            SocialEventModel.event_time >= current_window_start
        )
        velocity_result = await self.session.execute(velocity_stmt)
        current_velocity = velocity_result.scalar() or 0
        
        # 2. Engagement Growth (likes + replies + shares)
        # Current window engagement
        curr_eng_stmt = select(func.sum(SocialEventModel.likes + SocialEventModel.replies + SocialEventModel.shares)).where(
            SocialEventModel.topic_id == topic_id,
            SocialEventModel.event_time >= current_window_start
        )
        curr_eng_res = await self.session.execute(curr_eng_stmt)
        curr_eng = curr_eng_res.scalar() or 0
        
        # Previous window engagement
        prev_eng_stmt = select(func.sum(SocialEventModel.likes + SocialEventModel.replies + SocialEventModel.shares)).where(
            SocialEventModel.topic_id == topic_id,
            SocialEventModel.event_time >= previous_window_start,
            SocialEventModel.event_time < current_window_start
        )
        prev_eng_res = await self.session.execute(prev_eng_stmt)
        prev_eng = prev_eng_res.scalar() or 0
        
        engagement_growth = 0.0
        if prev_eng > 0:
            engagement_growth = (curr_eng - prev_eng) / prev_eng
        elif curr_eng > 0:
            engagement_growth = 1.0 # Max growth if went from 0 to something
            
        # 3. Cross-platform presence
        platform_stmt = select(func.count(func.distinct(SocialEventModel.platform))).where(
            SocialEventModel.topic_id == topic_id,
            SocialEventModel.event_time >= current_window_start
        )
        platform_res = await self.session.execute(platform_stmt)
        platform_count = platform_res.scalar() or 0
        
        # 4. Novelty (Time since first event)
        first_event_stmt = select(func.min(SocialEventModel.event_time)).where(
            SocialEventModel.topic_id == topic_id
        )
        first_event_res = await self.session.execute(first_event_stmt)
        first_event_time = first_event_res.scalar()
        
        novelty_score = 0.0
        if first_event_time:
            # Ensure timezone awareness
            if first_event_time.tzinfo is None:
                first_event_time = first_event_time.replace(tzinfo=timezone.utc)
            days_since_first = (now - first_event_time).days
            # Newer topics get higher novelty. Max score for < 1 day, decays over 30 days.
            novelty_score = max(0.0, 1.0 - (days_since_first / 30.0))
            
        # Normalization
        v_score = min(current_velocity / 100.0, 1.0) # Assume 100 events/window is max velocity
        e_score = min(max(engagement_growth, 0.0), 1.0)
        p_score = min(platform_count / 3.0, 1.0) # Assume max 3 platforms
        
        trend_score = (v_score * 0.4) + (e_score * 0.3) + (p_score * 0.2) + (novelty_score * 0.1)
        
        return {
            "topic_id": topic_id,
            "trend_score": round(trend_score, 4),
            "metrics": {
                "velocity": current_velocity,
                "engagement_growth": round(engagement_growth, 2),
                "platform_count": platform_count,
                "novelty_score": round(novelty_score, 2)
            }
        }
