
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.audience.clustering import cluster_users
from src.audience.features import extract_user_features, is_usable_for_clustering
from src.db.models import SocialEventModel, TopicModel
from src.insights.models import (
    AudienceEvidence,
    InsightEvidence,
    NetworkEvidence,
    SentimentEvidence,
    TrendEvidence,
)
from src.network.analyzer import NetworkAnalyzer
from src.semantic.trends import TrendAnalysisService


class InsightEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def gather_evidence(self, time_window_hours: int = 24) -> InsightEvidence:
        """
        Gathers structured evidence from all available Phase 3-6 components.
        Does not invent missing data.
        """
        # 1. Sentiment (Not Implemented in DB)
        sentiment_evidence = SentimentEvidence(
            available=False,
            reason="Sentiment analytics not currently implemented in production."
        )
        
        # 2. Trends (Phase 4)
        trend_evidence = await self._gather_trends(time_window_hours)
        
        # 3. Network (Phase 5)
        network_evidence = await self._gather_network(time_window_hours)
        
        # 4. Audience (Phase 6)
        audience_evidence = await self._gather_audience()
        
        # Data Quality Assessment
        quality_score = 0
        if trend_evidence.available and trend_evidence.trending_topics_count > 0:
            quality_score += 1
        if network_evidence.available and network_evidence.node_count > 0:
            quality_score += 1
        if audience_evidence.available and audience_evidence.usable_users >= 2:
            quality_score += 1
            
        data_quality = "insufficient"
        if quality_score == 3:
            data_quality = "high"
        elif quality_score == 2:
            data_quality = "moderate"
        elif quality_score == 1:
            data_quality = "low"
            
        limitations = [
            "Sentiment analytics are missing.",
            "Demographic analysis is restricted to protect privacy.",
            "Causal relationships cannot be definitively proven from observational network data."
        ]
        if data_quality in ["low", "insufficient"]:
            limitations.append(f"Insight quality is {data_quality} due to lack of meaningful analytics signals.")

        return InsightEvidence(
            time_window_hours=time_window_hours,
            data_quality=data_quality,
            sentiment=sentiment_evidence,
            trends=trend_evidence,
            audience=audience_evidence,
            network=network_evidence,
            limitations=limitations
        )
        
    async def _gather_trends(self, window_hours: int) -> TrendEvidence:
        try:
            stmt = select(TopicModel).where(TopicModel.is_outlier == False)
            result = await self.session.execute(stmt)
            topics = result.scalars().all()
            
            trend_service = TrendAnalysisService(self.session)
            trending = []
            for t in topics:
                t_data = await trend_service.get_topic_trend(t.id, window_hours=window_hours)
                trending.append({
                    "topic_id": t.id,
                    "name": t.name,
                    "trend_score": t_data["trend_score"],
                    "metrics": t_data["metrics"]
                })
                
            trending.sort(key=lambda x: x["trend_score"], reverse=True)
            return TrendEvidence(
                available=True,
                trending_topics_count=len(trending),
                top_topics=trending[:3] if trending else [],
                reason=None if trending else "No trending topics found."
            )
        except Exception as e:  # noqa: BLE001
            return TrendEvidence(available=False, reason=str(e))
            
    async def _gather_network(self, window_hours: int) -> NetworkEvidence:
        try:
            analyzer = NetworkAnalyzer(self.session)
            events = await analyzer._fetch_events(time_window_hours=window_hours)
            network = analyzer.build_network(events)
            
            # Simple check for nodes
            nodes = list(network.nodes())
            edges = list(network.edges())
            
            # Recalculate basic communities/influence from existing properties
            communities = analyzer.detect_communities(network)
            
            influencers = analyzer.calculate_influence(network)
            top_influencers = [str(n["user_id"]) for n in influencers[:3]]

            return NetworkEvidence(
                available=True,
                node_count=len(nodes),
                edge_count=len(edges),
                community_count=len(communities),
                top_influencers=top_influencers,
                reason=None if nodes else "No active network nodes in the given time window."
            )
        except Exception as e:  # noqa: BLE001
            return NetworkEvidence(available=False, reason=str(e))
            
    async def _gather_audience(self) -> AudienceEvidence:
        try:
            # We fetch all events for audience logic
            stmt = select(SocialEventModel)
            result = await self.session.execute(stmt)
            events = result.scalars().all()
            
            # Format to dicts
            event_dicts = []
            for ev in events:
                event_dicts.append({
                    "user_id": ev.user_id,
                    "likes": ev.likes,
                    "replies": ev.replies,
                    "shares": ev.shares,
                    "mentions": ev.mentions,
                    "hashtags": ev.hashtags,
                    "platform": ev.platform,
                    "event_time": ev.event_time
                })
                
            # Aggregate by user
            from collections import defaultdict
            user_events = defaultdict(list)
            for d in event_dicts:
                user_events[d["user_id"]].append(d)
                
            # Extract features
            user_features = {}
            for uid, evs in user_events.items():
                features = extract_user_features(evs)
                if features:
                    user_features[uid] = features
                    
            total_users = len(user_features)
            usable_features = {k: v for k, v in user_features.items() if is_usable_for_clustering(v)}
            usable_users = len(usable_features)
            insufficient = total_users - usable_users
            
            # Attempt clustering
            _, cohorts = cluster_users(usable_features)
            
            return AudienceEvidence(
                available=True,
                total_users_analyzed=total_users,
                usable_users=usable_users,
                insufficient_data_users=insufficient,
                cohort_count=len(cohorts),
                reason=None if usable_users > 0 else "Insufficient behavioral data for cohort clustering."
            )
        except Exception as e:  # noqa: BLE001
            return AudienceEvidence(available=False, reason=str(e))
