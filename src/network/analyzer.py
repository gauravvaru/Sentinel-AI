import networkx as nx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models import SocialEventModel, TopicModel
import json

class NetworkAnalyzer:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _fetch_events(self, time_window_hours: Optional[int] = None,
                           topic_id: Optional[int] = None,
                           platform: Optional[str] = None,
                           limit: int = 10000) -> List[SocialEventModel]:
        stmt = select(SocialEventModel)
        
        if time_window_hours is not None:
            cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)
            stmt = stmt.where(SocialEventModel.event_time >= cutoff)
            
        if topic_id is not None:
            stmt = stmt.where(SocialEventModel.topic_id == topic_id)
            
        if platform is not None:
            stmt = stmt.where(SocialEventModel.platform == platform)
            
        stmt = stmt.order_by(SocialEventModel.event_time.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    def build_network(self, events: List[SocialEventModel]) -> nx.DiGraph:
        """
        Builds a directed graph from actual stored events.
        Edges represent observed interactions.
        """
        G = nx.DiGraph()
        
        # We need a lookup to resolve parent_id to user_id for parent-event interactions
        # Since parent_id is platform_event_id, we map platform_event_id -> user_id
        # We only have events within our loaded set, but that's what we can analyze.
        event_to_user = {e.platform_event_id: e.user_id for e in events}
        
        for e in events:
            # Ensure the source node exists
            if not G.has_node(e.user_id):
                G.add_node(e.user_id, follower_count=e.follower_count)
            else:
                # Update follower count if it's higher/present
                if e.follower_count and (G.nodes[e.user_id].get('follower_count') or 0) < e.follower_count:
                    G.nodes[e.user_id]['follower_count'] = e.follower_count

            # 1. Parent-event interactions via parent_id
            if e.parent_id and e.parent_id in event_to_user:
                target_user = event_to_user[e.parent_id]
                # Avoid self-loops for simplicity unless meaningful, but let's allow them as some people interact with themselves.
                interaction_type = e.event_type # e.g. "post", "comment"
                
                if not G.has_node(target_user):
                    G.add_node(target_user, follower_count=0)
                    
                if G.has_edge(e.user_id, target_user):
                    G[e.user_id][target_user]['weight'] += 1
                    G[e.user_id][target_user]['interactions'].append(interaction_type)
                else:
                    G.add_edge(e.user_id, target_user, weight=1, interactions=[interaction_type])

            # 2. Mention relationships via mentions field
            mentions = e.mentions
            if isinstance(mentions, str):
                try:
                    mentions = json.loads(mentions)
                except:
                    mentions = []
            elif mentions is None:
                mentions = []
            
            for mentioned_user in mentions:
                if not G.has_node(mentioned_user):
                    G.add_node(mentioned_user, follower_count=0)
                    
                if G.has_edge(e.user_id, mentioned_user):
                    G[e.user_id][mentioned_user]['weight'] += 1
                    G[e.user_id][mentioned_user]['interactions'].append('mention')
                else:
                    G.add_edge(e.user_id, mentioned_user, weight=1, interactions=['mention'])
                    
        return G

    def calculate_influence(self, G: nx.DiGraph) -> List[Dict[str, Any]]:
        """
        Calculates influence metrics for each node in the graph.
        Returns a list of nodes with their metrics, sorted by PageRank.
        """
        if len(G) == 0:
            return []
            
        in_degrees = dict(G.in_degree(weight='weight'))
        out_degrees = dict(G.out_degree(weight='weight'))
        
        # Centrality metrics
        try:
            degree_cent = nx.degree_centrality(G)
        except Exception:
            degree_cent = {n: 0.0 for n in G.nodes()}
            
        try:
            pagerank = nx.pagerank(G, weight='weight')
        except Exception:
            pagerank = {n: 0.0 for n in G.nodes()}
            
        try:
            # Betweenness centrality can be slow, but graph is bounded.
            betweenness = nx.betweenness_centrality(G, weight='weight')
        except Exception:
            betweenness = {n: 0.0 for n in G.nodes()}
            
        influencers = []
        for node in G.nodes():
            influencers.append({
                "user_id": node,
                "in_degree": in_degrees.get(node, 0),
                "out_degree": out_degrees.get(node, 0),
                "degree_centrality": degree_cent.get(node, 0.0),
                "pagerank": pagerank.get(node, 0.0),
                "betweenness_centrality": betweenness.get(node, 0.0),
            })
            
        # Sort by PageRank descending
        influencers.sort(key=lambda x: x['pagerank'], reverse=True)
        return influencers

    def detect_communities(self, G: nx.DiGraph) -> List[Dict[str, Any]]:
        """
        Detects communities using Louvain algorithm.
        Returns a list of communities with aggregate stats.
        """
        if len(G) == 0:
            return []
            
        # Louvain works on undirected graphs naturally, but nx supports directed too or converts internally depending on version.
        # nx 3.0+ louvain_communities handles DiGraph by considering edge weights or ignoring direction.
        try:
            communities = nx.community.louvain_communities(G, seed=42)
        except Exception:
            # Fallback for very small/empty or incompatible graphs
            return []
            
        pagerank = nx.pagerank(G, weight='weight')
        
        result = []
        for idx, comm in enumerate(communities):
            comm_subgraph = G.subgraph(comm)
            interaction_volume = comm_subgraph.size(weight='weight')
            
            # Find influential members in this community
            members = []
            for node in comm:
                members.append({"user_id": node, "pagerank": pagerank.get(node, 0.0)})
            members.sort(key=lambda x: x['pagerank'], reverse=True)
            
            result.append({
                "community_id": idx,
                "users_count": len(comm),
                "interaction_volume": interaction_volume,
                "top_influencers": members[:5] # Top 5 members
            })
            
        # Sort communities by interaction volume
        result.sort(key=lambda x: x['interaction_volume'], reverse=True)
        return result

    async def get_topic_communities(self, topic_id: int, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Analyzes communities and influencers discussing a specific topic.
        """
        events = await self._fetch_events(time_window_hours=time_window_hours, topic_id=topic_id)
        if not events:
            return {
                "topic_id": topic_id, 
                "events_analyzed": 0, 
                "users_analyzed": 0,
                "platform_distribution": {},
                "communities": [], 
                "top_influencers": []
            }
            
        G = self.build_network(events)
        communities = self.detect_communities(G)
        influencers = self.calculate_influence(G)
        
        # Platform distribution
        platforms = {}
        for e in events:
            platforms[e.platform] = platforms.get(e.platform, 0) + 1
            
        return {
            "topic_id": topic_id,
            "events_analyzed": len(events),
            "users_analyzed": len(G.nodes()),
            "platform_distribution": platforms,
            "communities": communities,
            "top_influencers": influencers[:10]
        }

    async def get_propagation_timeline(self, topic_id: int, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Returns chronological events for a topic to show observed interaction-based propagation.
        """
        # Fetch events ordered by time ASC for timeline replay
        stmt = select(SocialEventModel).where(SocialEventModel.topic_id == topic_id).order_by(SocialEventModel.event_time.asc()).limit(limit)
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        
        timeline = []
        for e in events:
            timeline.append({
                "event_id": e.id,
                "event_time": e.event_time.isoformat() if e.event_time else None,
                "platform": e.platform,
                "event_type": e.event_type,
                "user_id": e.user_id,
                "parent_id": e.parent_id,
                "mentions": e.mentions if isinstance(e.mentions, list) else json.loads(e.mentions or "[]"),
                "text": e.text
            })
            
        return timeline
