// Audience
export interface CohortSummary {
  cohort_id: string;
  label: string;
  user_count: number;
  total_events: number;
  average_engagement: number;
  confidence: number;
  demographics: string;
}

export interface AudienceResponse {
  total_users: number;
  usable_users: number;
  insufficient_data_users: number;
  cohorts: CohortSummary[];
}

// Insights
export interface SentimentEvidence {
  available: boolean;
  positive_ratio: number | null;
  negative_ratio: number | null;
  neutral_ratio: number | null;
  reason: string | null;
}

export interface TrendEvidence {
  available: boolean;
  trending_topics_count: number;
  top_topics: any[];
  reason: string | null;
}

export interface AudienceEvidence {
  available: boolean;
  total_users_analyzed: number;
  usable_users: number;
  insufficient_data_users: number;
  cohort_count: number;
  reason: string | null;
}

export interface NetworkEvidence {
  available: boolean;
  node_count: number;
  edge_count: number;
  community_count: number;
  top_influencers: string[];
  reason: string | null;
}

export interface InsightEvidence {
  timestamp: string;
  time_window_hours: number;
  data_quality: string;
  sentiment: SentimentEvidence;
  trends: TrendEvidence;
  audience: AudienceEvidence;
  network: NetworkEvidence;
  limitations: string[];
}

export interface InsightResponse {
  headline: string;
  summary: string;
  key_findings: string[];
  evidence: InsightEvidence;
  caveats: string[];
  data_quality: string;
}

// Network
export interface InfluencerResponse {
  user_id: string;
  in_degree: number;
  out_degree: number;
  degree_centrality: number;
  pagerank: number;
  betweenness_centrality: number;
}

export interface CommunityResponse {
  community_id: number;
  users_count: number;
  interaction_volume: number;
  top_influencers: any[];
}

export interface TopicNetworkResponse {
  topic_id: number;
  events_analyzed: number;
  users_analyzed: number;
  platform_distribution: Record<string, number>;
  communities: CommunityResponse[];
  top_influencers: InfluencerResponse[];
}

export interface PropagationEvent {
  event_id: string;
  event_time: string | null;
  platform: string;
  event_type: string;
  user_id: string;
  parent_id: string | null;
  mentions: string[];
  text: string;
}

// Main (Trending / Search)
export interface TrendingTopic {
  topic_id: number;
  name: string;
  keywords: string[];
  trend_score: number;
  metrics: Record<string, any>;
}

export interface TrendingTopicsResponse {
  trending: TrendingTopic[];
}

export interface TopicDetails {
  id: number;
  name: string;
  keywords: string[];
  is_outlier: boolean;
  created_at: string;
  trend_data: any;
}
