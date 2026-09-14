import type { 
  AudienceResponse, 
  InsightResponse, 
  InfluencerResponse, 
  CommunityResponse, 
  TopicNetworkResponse, 
  PropagationEvent,
  TrendingTopicsResponse,
  TopicDetails
} from '../types/api';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API request failed: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // Main
  getTrendingTopics: (windowHours = 24, limit = 10) => 
    fetchApi<TrendingTopicsResponse>(`/api/topics/trending?window_hours=${windowHours}&limit=${limit}`),
  
  getTopicDetails: (topicId: number) => 
    fetchApi<TopicDetails>(`/api/topics/${topicId}`),
  
  search: (query: string, limit = 10, filters?: any) => 
    fetchApi<{results: any[]}>(`/api/search`, {
      method: 'POST',
      body: JSON.stringify({ query, limit, filters })
    }),

  // Audience
  getAudienceCohorts: (platform?: string, limit = 1000) => 
    fetchApi<AudienceResponse>(`/api/audience/cohorts?limit=${limit}${platform ? `&platform=${platform}` : ''}`),

  // Insights
  getInsights: (timeWindowHours = 24, topicId?: number) => 
    fetchApi<InsightResponse>(`/api/insights?time_window_hours=${timeWindowHours}${topicId ? `&topic_id=${topicId}` : ''}`),

  // Network
  getInfluencers: (timeWindowHours = 24, platform?: string, limit = 50) =>
    fetchApi<InfluencerResponse[]>(`/api/network/influencers?time_window_hours=${timeWindowHours}&limit=${limit}${platform ? `&platform=${platform}` : ''}`),
  
  getCommunities: (timeWindowHours = 24, platform?: string) =>
    fetchApi<CommunityResponse[]>(`/api/network/communities?time_window_hours=${timeWindowHours}${platform ? `&platform=${platform}` : ''}`),
  
  getTopicNetwork: (topicId: number, timeWindowHours = 24) =>
    fetchApi<TopicNetworkResponse>(`/api/network/topic/${topicId}?time_window_hours=${timeWindowHours}`),
  
  getPropagationTimeline: (topicId: number, limit = 500) =>
    fetchApi<PropagationEvent[]>(`/api/network/propagation/${topicId}?limit=${limit}`)
};
