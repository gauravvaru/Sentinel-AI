import * as React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Panel } from '@/components/ui/Panel';
import { Badge } from '@/components/ui/Badge';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';

export function Inspector() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const topicIdParam = searchParams.get('topicId');
  const topicId = topicIdParam ? parseInt(topicIdParam, 10) : null;

  const { data: topicDetails, isLoading: loadingTopic, error: errorTopic } = usePolling({
    fetcher: () => topicId ? api.getTopicDetails(topicId) : Promise.resolve(null),
    intervalMs: 30000,
    enabled: !!topicId
  });

  const { data: networkData, isLoading: loadingNetwork } = usePolling({
    fetcher: () => topicId ? api.getTopicNetwork(topicId, 24) : Promise.resolve(null),
    intervalMs: 30000,
    enabled: !!topicId
  });

  if (!topicId) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 h-full w-full">
        <EmptyState 
          title="No Narrative Selected" 
          message="Select a topic from the Overview to inspect its detailed narrative telemetry." 
        />
        <button 
          onClick={() => navigate('/')}
          className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-lg font-sans text-[13px] font-medium"
        >
          Go to Overview
        </button>
      </div>
    );
  }

  if (loadingTopic && !topicDetails) {
    return <LoadingState message="Loading narrative analysis..." />;
  }

  if (errorTopic || !topicDetails) {
    return <ErrorState message={`Failed to load narrative details for topic ${topicId}.`} />;
  }

  return (
    <div className="flex flex-col w-full gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-6 flex flex-col gap-4">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-3 mb-1 flex-wrap">
              <h1 className="font-sans text-[20px] font-semibold tracking-tight text-text-primary">
                {topicDetails.name}
              </h1>
              {topicDetails.is_outlier && <Badge variant="danger">ANOMALY DETECTED</Badge>}
            </div>
            <div className="flex items-center gap-2 text-text-secondary font-mono text-[11px] uppercase tracking-wider">
              <span>ID: {topicDetails.id}</span>
              <span>•</span>
              <span>Created: {new Date(topicDetails.created_at).toLocaleString()}</span>
            </div>
          </div>
          <div className="shrink-0 flex items-center gap-3">
             <button 
                onClick={() => navigate(`/propagation?topicId=${topicId}`)}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-surface-secondary hover:bg-surface-elevated text-text-primary font-sans text-[13px] transition-colors cursor-pointer" type="button"
             >
                <span>View Propagation</span>
                <span className="material-symbols-outlined text-[16px]">alt_route</span>
             </button>
             <button 
                onClick={() => navigate(`/network?topicId=${topicId}`)}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-surface-secondary hover:bg-surface-elevated text-text-primary font-sans text-[13px] transition-colors cursor-pointer" type="button"
             >
                <span>View Network</span>
                <span className="material-symbols-outlined text-[16px]">hub</span>
             </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-2">
          {topicDetails.keywords.map((kw, i) => (
            <span key={i} className="text-text-secondary bg-surface-secondary px-2.5 py-1 rounded font-mono text-[11px]">
              {kw}
            </span>
          ))}
        </div>
      </section>

      {/* KPI Strip */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] p-5 grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-border-subtle gap-y-4">
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Trend Score</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">
              {topicDetails.trend_data?.trend_score?.toFixed(2) || 'N/A'}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Narrative velocity</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Network Nodes</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">
              {networkData?.users_analyzed?.toLocaleString() || 0}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Unique entities involved</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Network Events</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">
              {networkData?.events_analyzed?.toLocaleString() || 0}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Observed interactions</span>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid gap-6 grid-cols-1 xl:grid-cols-2 items-start">
        <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden min-h-[400px]">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
            <h3 className="font-sans text-[14px] text-text-primary font-semibold">Community Structure</h3>
          </div>
          <div className="p-6 overflow-y-auto">
            {loadingNetwork && !networkData ? (
              <div className="flex h-full items-center justify-center text-text-muted font-sans text-[13px]">Loading network...</div>
            ) : (
              <div className="space-y-4">
                {networkData?.communities?.map((community) => (
                  <div key={community.community_id} className="flex flex-col gap-3 p-4 bg-surface-secondary/30 border border-border-subtle rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-sans font-semibold text-[13px] text-text-primary">Community {community.community_id}</span>
                      <span className="text-[11px] text-text-muted font-mono">{community.users_count} users</span>
                    </div>
                    <div className="text-[12px] text-text-secondary font-sans leading-relaxed">
                      <span className="font-medium text-text-primary">Top Influencers:</span> {community.top_influencers.map(inf => inf.user_id || inf).join(', ') || 'None detected'}
                    </div>
                  </div>
                ))}
                {(!networkData?.communities || networkData.communities.length === 0) && (
                  <div className="text-text-muted text-[13px] font-sans text-center py-8">No communities detected in this window.</div>
                )}
              </div>
            )}
          </div>
        </section>

        <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden min-h-[400px]">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
            <h3 className="font-sans text-[14px] text-text-primary font-semibold">Top Influencers</h3>
          </div>
          <div className="w-full overflow-x-auto">
            {loadingNetwork && !networkData ? (
              <div className="flex h-full min-h-[300px] items-center justify-center text-text-muted font-sans text-[13px]">Loading influencers...</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-header/60 text-text-muted font-mono text-[11px] uppercase tracking-wider">
                    <th className="py-3 px-6 font-semibold">User ID</th>
                    <th className="py-3 px-6 font-semibold">PageRank</th>
                    <th className="py-3 px-6 font-semibold">Centrality</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle font-sans text-[13px]">
                  {networkData?.top_influencers?.map((inf) => (
                    <tr key={inf.user_id} className="hover:bg-surface-secondary/60 transition-colors">
                      <td className="py-3 px-6 font-mono text-text-primary">{inf.user_id}</td>
                      <td className="py-3 px-6 text-text-primary font-mono">{inf.pagerank.toFixed(4)}</td>
                      <td className="py-3 px-6 text-text-secondary font-mono">{inf.degree_centrality.toFixed(4)}</td>
                    </tr>
                  ))}
                  {(!networkData?.top_influencers || networkData.top_influencers.length === 0) && (
                    <tr>
                      <td colSpan={3} className="py-8 px-6 text-text-muted text-center">No influencers detected.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
