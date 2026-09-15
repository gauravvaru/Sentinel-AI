from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.db.models import SocialEventModel, TopicModel

class TrendAnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_all_topic_trends(self, window_hours: int = 24) -> Dict[int, Dict[str, Any]]:
        """
        Calculate trend scores for all topics efficiently using batched grouping.
        Reduces N+1 query problem by fetching metrics for all topics in 3 concurrent grouped queries.
        """
        now = datetime.now(timezone.utc)
        current_window_start = now - timedelta(hours=window_hours)
        previous_window_start = current_window_start - timedelta(hours=window_hours)
        
        # 1. Current window stats (velocity, engagement, platform count)
        curr_stmt = select(
            SocialEventModel.topic_id,
            func.count(SocialEventModel.id).label('velocity'),
            func.sum(SocialEventModel.likes + SocialEventModel.replies + SocialEventModel.shares).label('engagement'),
            func.count(func.distinct(SocialEventModel.platform)).label('platforms')
        ).where(
            SocialEventModel.topic_id.is_not(None),
            SocialEventModel.event_time >= current_window_start
        ).group_by(SocialEventModel.topic_id)
        
        # 2. Previous window engagement
        prev_stmt = select(
            SocialEventModel.topic_id,
            func.sum(SocialEventModel.likes + SocialEventModel.replies + SocialEventModel.shares).label('engagement')
        ).where(
            SocialEventModel.topic_id.is_not(None),
            SocialEventModel.event_time >= previous_window_start,
            SocialEventModel.event_time < current_window_start
        ).group_by(SocialEventModel.topic_id)
        
        # 3. First event time
        first_stmt = select(
            SocialEventModel.topic_id,
            func.min(SocialEventModel.event_time).label('first_event')
        ).where(
            SocialEventModel.topic_id.is_not(None)
        ).group_by(SocialEventModel.topic_id)
        
        import asyncio
        curr_res, prev_res, first_res = await asyncio.gather(
            self.session.execute(curr_stmt),
            self.session.execute(prev_stmt),
            self.session.execute(first_stmt)
        )
        
        stats = {}
        # Parse first event times
        for row in first_res.all():
            stats[row.topic_id] = {
                "first_event": row.first_event,
                "velocity": 0,
                "curr_eng": 0,
                "prev_eng": 0,
                "platforms": 0
            }
            
        # Parse previous engagements
        for row in prev_res.all():
            if row.topic_id in stats:
                stats[row.topic_id]["prev_eng"] = row.engagement or 0
                
        # Parse current window stats
        for row in curr_res.all():
            if row.topic_id in stats:
                stats[row.topic_id]["velocity"] = row.velocity or 0
                stats[row.topic_id]["curr_eng"] = row.engagement or 0
                stats[row.topic_id]["platforms"] = row.platforms or 0
                
        results = {}
        for topic_id, t_stats in stats.items():
            first_event_time = t_stats["first_event"]
            novelty_score = 0.0
            if first_event_time:
                if first_event_time.tzinfo is None:
                    first_event_time = first_event_time.replace(tzinfo=timezone.utc)
                days_since_first = (now - first_event_time).days
                novelty_score = max(0.0, 1.0 - (days_since_first / 30.0))
                
            curr_eng = t_stats["curr_eng"]
            prev_eng = t_stats["prev_eng"]
            
            engagement_growth = 0.0
            if prev_eng > 0:
                engagement_growth = (curr_eng - prev_eng) / prev_eng
            elif curr_eng > 0:
                engagement_growth = 1.0
                
            v_score = min(t_stats["velocity"] / 100.0, 1.0)
            e_score = min(max(engagement_growth, 0.0), 1.0)
            p_score = min(t_stats["platforms"] / 3.0, 1.0)
            
            trend_score = (v_score * 0.4) + (e_score * 0.3) + (p_score * 0.2) + (novelty_score * 0.1)
            
            results[topic_id] = {
                "topic_id": topic_id,
                "trend_score": round(trend_score, 4),
                "metrics": {
                    "velocity": t_stats["velocity"],
                    "engagement_growth": round(engagement_growth, 2),
                    "platform_count": t_stats["platforms"],
                    "novelty_score": round(novelty_score, 2)
                }
            }
            
        return results
    
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
